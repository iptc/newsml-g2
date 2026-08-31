# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 International Press Telecommunications Council (IPTC)
# The MIT License — see LICENSE in the repository root.

"""
Build a browsable HTML preview of the generated reference.

This is a **preview harness, not the publishing pipeline**. Its purpose is to
settle the information architecture — what belongs in the left index, what
belongs across the top, how search should behave — while that question is still
cheap to change. The real site is a Phase 3 decision and will use the same
toolchain as the rest of iptc.org, with the IPTC design system.

What does transfer is the structure: the page groupings, the nav labels and the
search behaviour are renderer-independent, and are the part worth arguing about
now.

Layout, following the convention the C2PA specification site uses:

    ┌──────────────────────────────────────────────────┐
    │ top bar: artefact links + search                 │
    ├────────────┬───────────────────────┬─────────────┤
    │ left:      │ page content          │ right:      │
    │ all pages  │                       │ this page   │
    └────────────┴───────────────────────┴─────────────┘

No external assets: no CDN, no web fonts, no build step beyond Asciidoctor.
It has to work offline on a laptop in a meeting.
"""

from __future__ import annotations

import html
import json
import os
import re
import shutil
import subprocess

# The document roots, listed first because they are where a reader starts.
ITEM_TYPES = (
    'newsItem', 'packageItem', 'conceptItem', 'knowledgeItem',
    'planningItem', 'catalogItem', 'newsMessage',
)

# Cross-artefact links. Placeholders where a destination does not exist yet are
# marked so the gap is visible rather than silently dropped.
TOP_LINKS = (
    ('Specification', 'https://iptc.org/std/NewsML-G2/specification/', False),
    ('Guidelines', 'https://iptc.org/std/NewsML-G2/guidelines/', False),
    ('Schema reference', 'index.html', True),
    ('Examples', 'https://github.com/iptc/newsml-g2/tree/main/examples', False),
    ('Schemas', 'https://github.com/iptc/newsml-g2/tree/main/specification', False),
)

# The official mark from iptc.org/about-iptc/logos-and-design-assets/
# (logo_iptc_white_text_gradient.svg). Copied into the output rather than
# inlined as a data URI, which would repeat it across all 224 pages.
LOGO = 'iptc-logo.svg'

HEADING_RE = re.compile(
    r'<h([23])\s+id="([^"]+)"[^>]*>(.*?)</h\1>', re.S)
TAG_RE = re.compile(r'<[^>]+>')
TITLE_RE = re.compile(r'<h1[^>]*>(.*?)</h1>', re.S)


def _text(fragment):
    return html.unescape(TAG_RE.sub('', fragment)).strip()


def _describe(name, schema):
    """
    A one-line description for a search result and its tooltip.

    Taken from the schema rather than scraped from the rendered page: the page
    body starts with the definition but continues into headings, admonition
    labels and content-model rows, which read as noise in a tooltip.
    """
    if name.startswith('attgroup-'):
        group = name[len('attgroup-'):]
        if schema is not None:
            count = len(schema._expand_attribute_group(group))
            return 'Attribute group — %d attribute%s' % (
                count, '' if count == 1 else 's')
        return 'Attribute group'
    if schema is not None and name in schema.elements:
        doc = schema.elements[name].doc
        if doc:
            return ' '.join(doc.split())
    return ''


def render_fragments(pages_dir):
    """
    Run Asciidoctor once over every page, producing body-only HTML.
    """
    sources = sorted(
        name for name in os.listdir(pages_dir) if name.endswith('.adoc')
    )
    if not sources:
        raise SystemExit('no .adoc pages in %s — run with --pages first' % pages_dir)
    try:
        subprocess.run(
            ['asciidoctor', '--embedded', '-a', 'nofooter'] + sources,
            cwd=pages_dir, check=True,
        )
    except FileNotFoundError:
        raise SystemExit(
            'asciidoctor is not on PATH.\n'
            '\n'
            'The HTML preview needs it to turn the generated AsciiDoc into\n'
            'pages; everything else in this tool is pure Python. Install it\n'
            'with `gem install asciidoctor`, or drop --preview to generate\n'
            'the AsciiDoc sources only.'
        )
    return [name[:-5] for name in sources]


def _copy_assets(pages_dir):
    """
    Place the static assets beside the pages.

    Kept as files rather than inlined: a 31 KB data URI repeated across 224
    pages would add roughly 7 MB for one small image, and the whole point of
    replacing the XMLSpy output was to stop shipping pages that large.
    """
    source = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
    if not os.path.isdir(source):
        return
    for name in os.listdir(source):
        shutil.copyfile(os.path.join(source, name),
                        os.path.join(pages_dir, name))


def classify(names):
    """
    Group pages for the left index.

    A flat list of 224 entries is technically complete and practically
    unusable. Item types come first because they are document roots and the
    place a reader starts; attribute groups are separated because they are a
    different kind of thing from an element.
    """
    items, attribute_groups, elements = [], [], []
    for name in names:
        if name == 'index':
            continue
        if name.startswith('attgroup-'):
            attribute_groups.append(name)
        elif name in ITEM_TYPES:
            items.append(name)
        else:
            elements.append(name)
    items.sort(key=lambda n: ITEM_TYPES.index(n))
    return [
        ('Item types', items, True),
        ('Elements', sorted(elements, key=str.lower), False),
        ('Attribute groups', attribute_groups, False),
    ]


def _label(name):
    if name.startswith('attgroup-'):
        return name[len('attgroup-'):]
    return '&lt;%s&gt;' % name


def build(output_dir, schema=None):
    pages_dir = os.path.join(output_dir, 'pages')
    names = render_fragments(pages_dir)
    _copy_assets(pages_dir)
    groups = classify(names)
    index = []

    for name in names:
        if name == 'index':
            continue
        path = os.path.join(pages_dir, name + '.html')
        with open(path, encoding='utf-8') as handle:
            fragment = handle.read()

        title_match = TITLE_RE.search(fragment)
        title = _text(title_match.group(1)) if title_match else name
        body = TITLE_RE.sub('', fragment, count=1)

        headings = [
            (level, anchor, _text(text))
            for level, anchor, text in HEADING_RE.findall(body)
        ]
        index.append({
            'u': name + '.html',
            't': title,
            'x': _describe(name, schema),
            # Matched against but never displayed, so the whole page stays
            # findable by words in its User Note without putting scraped body
            # text — headings, admonition labels, mid-word truncation — in
            # front of a reader.
            'b': ' '.join(_text(body).split())[:400].lower(),
        })

        with open(path, 'w', encoding='utf-8') as handle:
            handle.write(page_html(name, title, body, headings, groups))

    if schema is not None:
        index.extend(attribute_index(schema))

    with open(os.path.join(pages_dir, 'search-index.json'), 'w',
              encoding='utf-8') as handle:
        json.dump(index, handle, separators=(',', ':'))

    with open(os.path.join(pages_dir, 'index.html'), 'w',
              encoding='utf-8') as handle:
        handle.write(landing_html(groups, len(index)))

    return len(index)


CSS = """
:root{--bg:#fff;--fg:#1b2430;--muted:#5d6b7a;--rule:#dde4ec;--accent:#1a4d8f;
--accent-soft:#eaf1fa;--bar:#10233d;--code:#f4f7fb;--sidebar:#fafbfd}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;font:15px/1.6 -apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
color:var(--fg);background:var(--bg)}
code,kbd{font-family:ui-monospace,"SF Mono",Menlo,monospace;font-size:.9em}

header.top{position:sticky;top:0;z-index:20;background:var(--bar);color:#fff;
display:flex;align-items:center;gap:22px;padding:0 18px;height:52px}
header.top .brand{font-weight:600;letter-spacing:.2px;white-space:nowrap}
header.top .brand span{opacity:.65;font-weight:400}
header.top nav{display:flex;gap:16px;flex:1;overflow-x:auto;justify-content:flex-end}
header.top nav a{color:#c9d8ec;text-decoration:none;white-space:nowrap;
padding:4px 2px;border-bottom:2px solid transparent;font-size:14px}
header.top nav a:hover{color:#fff}
header.top nav a.here{color:#fff;border-bottom-color:#5b9bd5}
header.top .logo{display:flex;align-items:center;flex:none;line-height:0}
header.top .logo img{display:block}
@media(max-width:900px){header.top .logo{display:none}}
header.top nav a.ext::after{content:"↗";font-size:10px;opacity:.6;margin-left:3px;
vertical-align:super}
.search{position:relative}
.search input{width:300px;padding:6px 10px;border-radius:5px;
border:1px solid #2c456b;background:#1a3358;color:#fff;font-size:13px}
.search input::placeholder{color:#8fa6c4}
.search input:focus{outline:2px solid #5b9bd5;outline-offset:-1px}
.results{position:absolute;top:36px;right:0;width:400px;max-height:60vh;overflow:auto;
background:#fff;color:var(--fg);border:1px solid var(--rule);border-radius:6px;
box-shadow:0 8px 28px rgba(16,35,61,.18);display:none}
.results.open{display:block}
.results a{display:block;padding:8px 12px;text-decoration:none;color:var(--fg);
border-bottom:1px solid #f0f3f7}
.results a:last-child{border-bottom:0}
.results a:hover,.results a.sel{background:var(--accent-soft)}
.results .t{font-weight:600;color:var(--accent)}
.results .src{color:var(--muted);font-weight:400;font-size:12.5px;margin-left:6px}
.results .kind{float:right;font-size:10px;text-transform:uppercase;
letter-spacing:.06em;color:var(--muted);background:var(--code);
padding:1px 6px;border-radius:9px;margin-left:8px}
.results .x{font-size:12px;color:var(--muted);display:block;
overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.results .none{padding:12px;color:var(--muted);font-size:13px}

.shell{display:grid;grid-template-columns:270px minmax(0,1fr) 220px;
align-items:start;gap:0}
aside.left{position:sticky;top:52px;height:calc(100vh - 52px);overflow-y:auto;
border-right:1px solid var(--rule);background:var(--sidebar);padding:16px 0 40px}
aside.left h2{font-size:11px;text-transform:uppercase;letter-spacing:.09em;
color:var(--muted);margin:18px 16px 6px}
aside.left a{display:block;padding:3px 16px;text-decoration:none;color:var(--fg);
font-size:13.5px;border-left:3px solid transparent}
aside.left a:hover{background:var(--accent-soft)}
aside.left a.here{border-left-color:var(--accent);background:var(--accent-soft);
color:var(--accent);font-weight:600}
aside.left code{background:none}

main{padding:26px 34px 80px;min-width:0}
nav.toc{position:sticky;top:52px;max-height:calc(100vh - 52px);overflow-y:auto;
padding:26px 16px 40px;font-size:13px}
nav.toc h2{font-size:11px;text-transform:uppercase;letter-spacing:.09em;
color:var(--muted);margin:0 0 8px}
nav.toc a{display:block;color:var(--muted);text-decoration:none;padding:2px 0;
border-left:2px solid var(--rule);padding-left:9px}
nav.toc a:hover{color:var(--accent)}
nav.toc a.l3{padding-left:20px;font-size:12.5px}
nav.toc a.active{color:var(--accent);border-left-color:var(--accent);font-weight:600}

h1{font-size:27px;margin:0 0 4px;letter-spacing:-.01em}
h2{font-size:19px;margin:30px 0 10px;padding-bottom:5px;border-bottom:1px solid var(--rule)}
h3{font-size:15.5px;margin:20px 0 8px;color:var(--accent)}
main a{color:var(--accent)}
main table{border-collapse:collapse;width:100%;margin:10px 0 18px;font-size:13.5px}
main th{background:var(--accent);color:#fff;text-align:left;padding:7px 9px}
main td{padding:6px 9px;border:1px solid var(--rule);vertical-align:top}
main tbody tr:nth-child(even) td{background:#f8fafd}
main td[colspan]{background:var(--accent-soft);font-weight:600;color:var(--accent);
font-size:12.5px;letter-spacing:.02em}
main tbody tr:nth-child(even) td[colspan]{background:var(--accent-soft)}
main td[colspan] a{color:var(--accent)}
/* so a #attr-… jump is not hidden behind the sticky bar */
main td span[id],main [id]{scroll-margin-top:64px}
:target{background:#fff6d8;transition:background .6s ease}
main code{background:var(--code);padding:1px 5px;border-radius:3px}
main a code{background:var(--accent-soft)}
.ulist ul{padding-left:20px}
.admonitionblock td.content{border-left:3px solid var(--accent);padding-left:12px;
background:var(--code)}
.admonitionblock .title{font-weight:600;color:var(--accent)}
.preview-note{background:#fff8e6;border:1px solid #e8d9a8;border-radius:5px;
padding:9px 13px;font-size:13px;color:#6b5518;margin:0 0 20px}
.landing{max-width:720px}
.landing .stat{display:inline-block;margin:0 26px 14px 0}
.landing .stat b{display:block;font-size:23px;color:var(--accent)}
.landing .stat span{font-size:12px;color:var(--muted);text-transform:uppercase;
letter-spacing:.06em}
@media(max-width:1100px){.shell{grid-template-columns:240px minmax(0,1fr)}nav.toc{display:none}}
@media(max-width:760px){.shell{grid-template-columns:1fr}aside.left{display:none}}
"""

JS = """
(function(){
var box=document.getElementById('q'),out=document.getElementById('r'),idx=null,sel=-1;
if(!box)return;
function load(){if(idx)return Promise.resolve(idx);
return fetch('search-index.json').then(function(r){return r.json()}).then(function(d){idx=d;return d})}
function esc(s){return s.replace(/[&<>]/g,function(c){
return {'&':'&amp;','<':'&lt;','>':'&gt;'}[c]})}
function att(s){return s.replace(/[&<>"]/g,function(c){
return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function run(){var q=box.value.trim().toLowerCase();
if(q.length<2){out.classList.remove('open');out.innerHTML='';sel=-1;return}
load().then(function(d){
var hits=[],i;
var bare=q.replace(/^@/,'');
for(i=0;i<d.length;i++){
var isAttr=d[i].k==='a',t=d[i].t.toLowerCase(),
tt=isAttr?t.slice(1):t,p=tt.indexOf(bare);
if(p>-1){hits.push({e:d[i],s:(p===0?0:2)+(isAttr?1:0)});continue}
if(d[i].x.toLowerCase().indexOf(bare)>-1||(d[i].b||'').indexOf(bare)>-1||(d[i].s||'').toLowerCase().indexOf(bare)>-1)hits.push({e:d[i],s:4+(isAttr?1:0)})}
hits.sort(function(a,b){return a.s-b.s||a.e.t.length-b.e.t.length||(a.e.s||'').localeCompare(b.e.s||'')});
hits=hits.slice(0,25);sel=-1;
if(!hits.length){out.innerHTML='<div class="none">No match for &ldquo;'+esc(q)+'&rdquo;</div>';
out.classList.add('open');return}
out.innerHTML=hits.map(function(h){
var tip=h.e.t+(h.e.s?' ('+h.e.s+')':'')+(h.e.x?' — '+h.e.x:'');
return '<a href="'+h.e.u+'" title="'+att(tip)+'"><span class="t">'+esc(h.e.t)+'</span>'+
(h.e.s?'<span class="src">'+esc(h.e.s)+'</span>':'')+
'<span class="kind">'+(h.e.k==='a'?'attribute':'element')+'</span>'+
'<span class="x">'+esc(h.e.x.slice(0,90))+'</span></a>'}).join('');
out.classList.add('open')})}
box.addEventListener('input',run);
box.addEventListener('keydown',function(e){
var links=out.querySelectorAll('a');
if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();
if(!links.length)return;
if(sel>-1)links[sel].classList.remove('sel');
sel=e.key==='ArrowDown'?(sel+1)%links.length:(sel<=0?links.length-1:sel-1);
links[sel].classList.add('sel');links[sel].scrollIntoView({block:'nearest'})}
else if(e.key==='Enter'&&sel>-1){e.preventDefault();links[sel].click()}
else if(e.key==='Escape'){out.classList.remove('open');box.blur()}});
document.addEventListener('click',function(e){
if(!e.target.closest('.search'))out.classList.remove('open')});
document.addEventListener('keydown',function(e){
if(e.key==='/'&&document.activeElement!==box){e.preventDefault();box.focus()}});
// highlight the in-page TOC entry for whatever is on screen
var heads=[].slice.call(document.querySelectorAll('main h2[id],main h3[id]'));
var tocLinks={};[].forEach.call(document.querySelectorAll('nav.toc a'),function(a){
tocLinks[a.getAttribute('href').slice(1)]=a});
if(heads.length&&'IntersectionObserver' in window){
var seen={};
new IntersectionObserver(function(es){
es.forEach(function(en){seen[en.target.id]=en.isIntersecting});
var cur=null;heads.forEach(function(h){if(seen[h.id]&&!cur)cur=h.id});
for(var k in tocLinks)tocLinks[k].classList.toggle('active',k===cur)},
{rootMargin:'-52px 0px -70% 0px'}).observe&&heads.forEach(function(h){
new IntersectionObserver(function(es){
es.forEach(function(en){seen[en.target.id]=en.isIntersecting});
var cur=null;heads.forEach(function(x){if(seen[x.id]&&!cur)cur=x.id});
for(var k in tocLinks)tocLinks[k].classList.toggle('active',k===cur)},
{rootMargin:'-52px 0px -70% 0px'}).observe(h)})}
})();
"""


def _top_bar(current_is_reference=True):
    links = []
    for label, href, internal in TOP_LINKS:
        classes = []
        if internal and current_is_reference:
            classes.append('here')
        if not internal:
            classes.append('ext')
        attr = ' class="%s"' % ' '.join(classes) if classes else ''
        target = '' if internal else ' target="_blank" rel="noopener"'
        links.append('<a href="%s"%s%s>%s</a>' % (href, attr, target, label))
    return """<header class="top">
  <div class="brand">NewsML-G2 <span>2.35</span></div>
  <nav>%s</nav>
  <div class="search">
    <input id="q" type="search"
           placeholder="Press / to search elements and attributes"
           autocomplete="off" spellcheck="false"
           aria-label="Search elements and attributes">
    <div class="results" id="r"></div>
  </div>
  <a class="logo" href="https://iptc.org/" target="_blank" rel="noopener"
     title="IPTC home page"><img src="%s" alt="IPTC" width="30" height="30"></a>
</header>""" % (''.join(links), LOGO)


def _left_index(groups, current=None):
    out = ['<aside class="left">']
    for heading, names, _ in groups:
        if not names:
            continue
        out.append('<h2>%s</h2>' % heading)
        for name in names:
            cls = ' class="here"' if name == current else ''
            out.append('<a href="%s.html"%s><code>%s</code></a>'
                       % (name, cls, _label(name)))
    out.append('</aside>')
    return '\n'.join(out)


def _right_toc(headings):
    if not headings:
        return '<nav class="toc"></nav>'
    out = ['<nav class="toc"><h2>On this page</h2>']
    for level, anchor, text in headings:
        cls = ' class="l3"' if level == '3' else ''
        out.append('<a href="#%s"%s>%s</a>' % (anchor, cls, html.escape(text)))
    out.append('</nav>')
    return '\n'.join(out)


PREVIEW_BANNER = (
    '<p class="preview-note"><strong>Preview.</strong> Generated from the '
    'NewsML-G2 2.35 XML Schema by <code>tools/xsdref</code>. This layout is a '
    'harness for reviewing structure and content — it is not the published '
    'site.</p>'
)


def _document(title, body, extra_head=''):
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s — NewsML-G2 Reference</title>
<style>%s</style>%s</head>
<body>%s<script>%s</script></body></html>""" % (
        html.escape(title), CSS, extra_head, body, JS)


def page_html(name, title, body, headings, groups):
    shell = """%s
<div class="shell">
%s
<main>%s<h1>%s</h1>
%s
</main>
%s
</div>""" % (_top_bar(), _left_index(groups, current=name), PREVIEW_BANNER,
             html.escape(title), body, _right_toc(headings))
    return _document(title, shell)


def landing_html(groups, page_count):
    counts = {heading: len(names) for heading, names, _ in groups}
    body = """%s
<div class="shell">
%s
<main>%s
<div class="landing">
<h1>NewsML-G2 Element Reference</h1>
<p>Generated from <code>NewsML-G2_2.35-spec-All-Power.xsd</code>. Every element
name in the schema has a page giving its definition, the contexts it is
declared in, its content model and its attributes, with any User Note or
Implementation Note from Specification &sect;14 merged in.</p>
<p><span class="stat"><b>%d</b><span>pages</span></span>
<span class="stat"><b>%d</b><span>item types</span></span>
<span class="stat"><b>%d</b><span>elements</span></span>
<span class="stat"><b>%d</b><span>attribute groups</span></span></p>
<h2>Where to start</h2>
<p>Pick a document root from <strong>Item types</strong> in the left index and
follow the content model down; every element name links to its own page. Or
press <kbd>/</kbd> and search.</p>
<h2>What this is not</h2>
<p>This preview replaces the hand-run XMLSpy schema documentation, whose
<code>NewsItem</code> page alone was 12.4&nbsp;MB. The styling here is a review
harness, not a design: the published version will use the IPTC design system and
the same toolchain as the rest of iptc.org.</p>
</div>
</main>
<nav class="toc"></nav>
</div>""" % (_top_bar(), _left_index(groups), PREVIEW_BANNER, page_count,
             counts.get('Item types', 0), counts.get('Elements', 0),
             counts.get('Attribute groups', 0))
    return _document('Element Reference', body)


def attribute_index(schema):
    """
    Search entries for attributes, pointing at the page that defines each one.

    An attribute is not a page, so it needs a canonical home. A group attribute
    gets one — its attributeGroup page — which is why those pages are kept even
    though the element pages now expand them inline. An attribute declared
    directly on an element points at that element.

    Where the same name is declared in more than one place the entries are kept
    separate rather than merged, because they are genuinely different
    declarations: `role` appears in several groups with different documentation.
    """
    entries = []
    seen = set()

    for group in sorted(schema.attribute_groups):
        for attr in schema._expand_attribute_group(group):
            key = (attr.name, group)
            if key in seen:
                continue
            seen.add(key)
            entries.append({
                'u': 'attgroup-%s.html#attr-%s'
                     % (group, attr.name.replace(':', '-')),
                't': '@' + attr.name,
                # Preposition follows the relationship: an attribute is *in* a
                # group, but *on* an element.
                's': 'in %s' % group,
                'x': (attr.doc or '')[:500],
                'k': 'a',
            })

    for name in schema.element_names():
        for declaration in schema.elements[name].declarations:
            for attr in declaration.attributes:
                if not attr.is_local:
                    continue
                key = (attr.name, name)
                if key in seen:
                    continue
                seen.add(key)
                entries.append({
                    'u': '%s.html#attr-%s' % (name, attr.name.replace(':', '-')),
                    't': '@' + attr.name,
                    's': 'on <%s>' % name,
                    'x': (attr.doc or '')[:500],
                    'k': 'a',
                })

    return entries
