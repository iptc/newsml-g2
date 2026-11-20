# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 International Press Telecommunications Council (IPTC)
# The MIT License — see LICENSE in the repository root.

"""
Render split chapters into the shared documentation shell.

Same three-part frame as the schema reference: artefact links and search
across the top, an index of chapters down the left with the current chapter's
sections expanded, and the sub-headings of the current chapter on the right.

Layout and styling here are provisional. The published site is a Phase 3
decision and will use the IPTC design system; what is worth settling now is
the information architecture, which is renderer-independent.
"""

from __future__ import annotations

import html
import json
import os

# Relative to a chapter page. The books and the schema reference are written
# as sibling folders of one site (see tools/docsite.py), so these hold wherever
# that site is served from.
TOP_LINKS = (
    ('Specification', '../specification/preface.html'),
    ('Guidelines', '../guidelines/preface.html'),
    ('Schema reference', '../reference/index.html'),
    ('Examples', 'https://github.com/iptc/newsml-g2/tree/main/examples'),
    ('Schemas', 'https://github.com/iptc/newsml-g2/tree/main/specification'),
)

BANNER = ('<strong>Preview.</strong> Built from the NewsML-G2 AsciiDoc '
          'sources by <code>tools/prosedoc</code>. This layout is a harness '
          'for reviewing structure — it is not the published site.')

CSS = """
:root{--bg:#fff;--fg:#1b2430;--muted:#5d6b7a;--rule:#dde4ec;--accent:#1a4d8f;
--accent-soft:#eaf1fa;--bar:#10233d;--code:#f4f7fb;--sidebar:#fafbfd}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;font:15px/1.65 -apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:var(--fg)}
code,kbd{font-family:ui-monospace,"SF Mono",Menlo,monospace;font-size:.9em}
header.top{position:sticky;top:0;z-index:20;background:var(--bar);color:#fff;
display:flex;align-items:center;gap:22px;padding:0 18px;height:52px}
header.top .brand{font-weight:600;white-space:nowrap}
header.top .brand span{opacity:.65;font-weight:400}
header.top nav{display:flex;gap:16px;flex:1;justify-content:flex-end;overflow-x:auto}
header.top nav a{color:#c9d8ec;text-decoration:none;white-space:nowrap;font-size:14px;
padding:4px 2px;border-bottom:2px solid transparent}
header.top nav a.here{color:#fff;border-bottom-color:#5b9bd5}
header.top .search{position:relative}
header.top .search input{width:300px;padding:6px 10px;border-radius:5px;
border:1px solid #2c456b;background:#1a3358;color:#fff;font-size:13px}
header.top .search input::placeholder{color:#8fa6c4}
.results{position:absolute;top:36px;right:0;width:420px;max-height:60vh;overflow:auto;
background:#fff;color:var(--fg);border:1px solid var(--rule);border-radius:6px;
box-shadow:0 8px 28px rgba(16,35,61,.18);display:none}
.results.open{display:block}
.results a{display:block;padding:8px 12px;text-decoration:none;color:var(--fg);
border-bottom:1px solid #f0f3f7;font-size:14px;line-height:1.4}
.results a:last-child{border-bottom:0}
.results a:hover,.results a.sel{background:var(--accent-soft)}
.results .t{font-weight:600;color:var(--accent)}
.results .kind{float:right;font-size:10px;text-transform:uppercase;
letter-spacing:.06em;color:var(--muted);background:var(--code);
padding:1px 6px;border-radius:9px;margin-left:8px}
.results .x{font-size:12px;color:var(--muted);display:block;
overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.results .none{padding:12px;color:var(--muted);font-size:13px}
.shell{display:grid;grid-template-columns:270px minmax(0,1fr) 235px;align-items:start}
aside.left,nav.toc{position:sticky;top:52px;max-height:calc(100vh - 52px);overflow-y:auto}
aside.left{border-right:1px solid var(--rule);background:var(--sidebar);padding:16px 0 40px}
aside.left h2{font-size:11.5px;text-transform:uppercase;letter-spacing:.09em;
color:var(--muted);margin:18px 16px 8px}
aside.left a{display:block;text-decoration:none;color:var(--fg);font-size:14.5px;
padding:5px 16px;border-left:3px solid transparent;line-height:1.4}
aside.left a:hover{background:var(--accent-soft)}
aside.left a.here{border-left-color:var(--accent);background:var(--accent-soft);
color:var(--accent);font-weight:600}
aside.left a.sub{padding-left:32px;font-size:13.5px;color:var(--muted);border-left-color:transparent}
aside.left a.sub:hover{color:var(--accent)}
aside.left .grp{border-bottom:1px solid var(--rule);padding-bottom:6px;margin-bottom:6px}
nav.toc{padding:26px 18px 40px}
nav.toc h2{font-size:11.5px;text-transform:uppercase;letter-spacing:.09em;
color:var(--muted);margin:0 0 10px}
nav.toc a{display:block;color:var(--muted);text-decoration:none;padding:3px 0 3px 10px;
border-left:2px solid var(--rule);font-size:14px;line-height:1.4}
nav.toc a:hover,nav.toc a.active{color:var(--accent);border-left-color:var(--accent)}
nav.toc a.l3{padding-left:22px;font-size:13px}
main{padding:26px 40px 90px;min-width:0;max-width:830px}
main h1{font-size:28px;margin:0 0 18px;letter-spacing:-.01em}
main h2{font-size:20px;margin:32px 0 10px;padding-bottom:6px;border-bottom:1px solid var(--rule)}
main h3{font-size:16px;margin:22px 0 8px;color:var(--accent)}
main a{color:var(--accent)}
main table{border-collapse:collapse;width:100%;margin:12px 0 20px;font-size:13.5px}
main th{background:var(--accent);color:#fff;text-align:left;padding:7px 9px}
main td{padding:6px 9px;border:1px solid var(--rule);vertical-align:top}
main tbody tr:nth-child(even) td{background:#f8fafd}
main pre{background:var(--code);border:1px solid var(--rule);border-left:3px solid var(--accent);
padding:10px 12px;border-radius:5px;overflow-x:auto;font-size:12.5px}
main code{background:var(--code);padding:1px 5px;border-radius:3px}
main pre code{background:none;padding:0}
main img{max-width:100%}
.admonitionblock td.content{border-left:3px solid var(--accent);padding-left:12px;background:var(--code)}
.note{background:#fff8e6;border:1px solid #e8d9a8;border-radius:5px;padding:9px 13px;
font-size:13px;color:#6b5518;margin:0 0 20px}
.pager{display:flex;justify-content:space-between;gap:16px;margin-top:44px;
padding-top:18px;border-top:1px solid var(--rule);font-size:14px}
.pager a{text-decoration:none;color:var(--accent);max-width:46%}
.pager span{display:block;font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
@media(max-width:1000px){.shell{grid-template-columns:250px minmax(0,1fr)}nav.toc{display:none}}
@media(max-width:720px){.shell{grid-template-columns:1fr}aside.left{display:none}}
"""



# Searches the whole site: both books' section headings and the text under
# them, and the schema reference's elements and attributes. Each part's index
# is fetched on the first keystroke; a part that is missing (a book built on
# its own) is skipped. Matches in a heading or name rank above matches in text.
SEARCH_PARTS = (
    ('specification', 'Specification'),
    ('guidelines', 'Guidelines'),
    ('reference', None),
)

JS = """(function(){
var box=document.getElementById('q'),out=document.getElementById('r'),idx=null,sel=-1;
if(!box)return;
var parts=%s;
function load(){if(idx)return idx;
idx=Promise.all(parts.map(function(p){
return fetch('../'+p[0]+'/search-index.json').then(function(r){return r.ok?r.json():[]})
.catch(function(){return []}).then(function(d){return d.map(function(e){
return {u:'../'+p[0]+'/'+e.u,t:e.t,s:e.s||'',x:e.x||'',b:e.b||'',
k:p[1]||(e.k==='a'?'attribute':'element')}})})})).then(function(all){
return [].concat.apply([],all)});return idx}
function esc(s){return s.replace(/[&<>"]/g,function(c){
return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function run(){var q=box.value.trim().toLowerCase();
if(q.length<2){out.classList.remove('open');out.innerHTML='';sel=-1;return}
load().then(function(d){
if(box.value.trim().toLowerCase()!==q)return;
var hits=[];
d.forEach(function(e){var t=e.t.toLowerCase().replace(/^[\\d.]+\\s*/,'').replace(/^[<@]/,''),
p=t.indexOf(q);
if(p>-1)hits.push({e:e,s:p===0?0:1});
else if(e.x.toLowerCase().indexOf(q)>-1||e.b.indexOf(q)>-1||e.s.toLowerCase().indexOf(q)>-1)
hits.push({e:e,s:2})});
hits.sort(function(a,b){return a.s-b.s||a.e.t.length-b.e.t.length});
hits=hits.slice(0,30);sel=-1;
if(!hits.length){out.innerHTML='<div class="none">No match for &ldquo;'+esc(q)+'&rdquo;</div>';
out.classList.add('open');return}
out.innerHTML=hits.map(function(h){var e=h.e;
return '<a href="'+esc(e.u)+'" title="'+esc(e.t+(e.s?' — '+e.s:''))+'">'+
'<span class="kind">'+esc(e.k)+'</span><span class="t">'+esc(e.t)+'</span>'+
'<span class="x">'+esc(e.s||e.x.slice(0,100))+'</span></a>'}).join('');
out.classList.add('open')})}
box.addEventListener('input',run);
box.addEventListener('keydown',function(e){
var links=out.querySelectorAll('a');
if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();
if(!links.length)return;
if(sel>-1)links[sel].classList.remove('sel');
sel=e.key==='ArrowDown'?(sel+1)%%links.length:(sel<=0?links.length-1:sel-1);
links[sel].classList.add('sel');links[sel].scrollIntoView({block:'nearest'})}
else if(e.key==='Enter'){var go=links[sel>-1?sel:0];if(go){e.preventDefault();go.click()}}
else if(e.key==='Escape'){out.classList.remove('open');box.blur()}});
document.addEventListener('click',function(e){
if(!e.target.closest('.search'))out.classList.remove('open')});
document.addEventListener('keydown',function(e){
if(e.key==='/'&&document.activeElement!==box){e.preventDefault();box.focus()}});
})();""" % json.dumps(SEARCH_PARTS)


def _top_bar(docname, version):
    links = ''.join(
        '<a href="%s"%s>%s</a>'
        % (href, ' class="here"' if label == docname else '', label)
        for label, href in TOP_LINKS)
    return ('<header class="top"><div class="brand">NewsML-G2 <span>%s</span></div>'
            '<nav>%s</nav><div class="search"><input id="q" type="search" '
            'placeholder="Press / to search the documentation" autocomplete="off" '
            'spellcheck="false" aria-label="Search the documentation">'
            '<div class="results" id="r"></div></div></header>'
            % (html.escape(version), links))


def _left_index(chapters, current, docname):
    """
    Chapters, with the current one expanded to show its sections.

    The section level is h3, not h2: the chapter title is the only h2 in both
    documents, so expanding h2 would show a single entry repeating the title.
    """
    out = ['<aside class="left"><h2>%s</h2>' % html.escape(docname)]
    for chapter in chapters:
        here = chapter is current
        if here:
            out.append('<div class="grp">')
        out.append('<a href="%s.html"%s>%s</a>'
                   % (chapter['file'], ' class="here"' if here else '',
                      html.escape(chapter['title'])))
        if here:
            for level, anchor, text in chapter['heads']:
                if level == '3':
                    out.append('<a class="sub" href="#%s">%s</a>'
                               % (anchor, html.escape(text)))
            out.append('</div>')
    out.append('</aside>')
    return ''.join(out)


def _right_toc(chapter):
    out = ['<nav class="toc"><h2>On this page</h2>']
    for level, anchor, text in chapter['heads']:
        out.append('<a class="l%s" href="#%s">%s</a>'
                   % ('2' if level == '3' else '3', anchor, html.escape(text)))
    out.append('</nav>')
    return ''.join(out)


def _pager(chapters, index):
    previous = ('<a href="%s.html"><span>Previous</span>%s</a>'
                % (chapters[index-1]['file'],
                   html.escape(chapters[index-1]['title']))) if index else '<span></span>'
    following = ('<a href="%s.html" style="text-align:right"><span>Next</span>%s</a>'
                 % (chapters[index+1]['file'],
                    html.escape(chapters[index+1]['title']))) if index < len(chapters)-1 else '<span></span>'
    return '<div class="pager">%s%s</div>' % (previous, following)


def write_pages(chapters, output_dir, docname, version='', stem=''):
    """
    Write one page per chapter. Returns the paths written.

    `stem` is the book's MathJax markup, added only to chapters that use it.
    """
    os.makedirs(output_dir, exist_ok=True)
    written = []
    for index, chapter in enumerate(chapters):
        body = ('%s<div class="shell">%s<main><p class="note">%s</p>'
                '<h1 id="%s">%s</h1>%s%s</main>%s</div>'
                % (_top_bar(docname, version), _left_index(chapters, chapter, docname),
                   BANNER, chapter['anchor'], html.escape(chapter['title']),
                   chapter['body'],
                   _pager(chapters, index), _right_toc(chapter)))
        page = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1">'
                '<title>%s</title><style>%s</style></head><body>%s<script>%s</script>%s'
                '</body></html>'
                % (html.escape(chapter['title']), CSS, body, JS,
                   stem if chapter.get('stem') else ''))
        path = os.path.join(output_dir, chapter['file'] + '.html')
        with open(path, 'w', encoding='utf-8') as handle:
            handle.write(page)
        written.append(path)
    return written


# The hash never reaches the server, so the old single-page links can only be
# redirected in the browser. Anchors not in the map (the old page's own chrome,
# such as #toc) land on the first chapter.
INDEX_SCRIPT = """var pages=%s,anchor=location.hash.slice(1),page=pages[anchor];
try{if(!page)page=pages[decodeURIComponent(anchor)]}catch(e){}
location.replace((page||%s)+'.html'+(page&&anchor?'#'+anchor:''));"""


def write_index(chapters, anchors, output_dir, docname):
    """
    Write the book's index.html, which forwards links into the old single page.

    `anchors` is the book's anchor map (split.anchor_map). A link such as
    `specification/#introduction-to-eventsml-g2` was written for the single-page
    book; that section is now on its own chapter page, and this sends the reader
    there. Without script, it lists the chapters.
    """
    pages = json.dumps(anchors, separators=(',', ':'), sort_keys=True)
    links = ''.join('<li><a href="%s.html">%s</a></li>'
                    % (chapter['file'], html.escape(chapter['title']))
                    for chapter in chapters)
    page = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<title>NewsML-G2 %s</title><script>%s</script></head>'
            '<body><h1>NewsML-G2 %s</h1><ul>%s</ul></body></html>'
            % (html.escape(docname),
               INDEX_SCRIPT % (pages.replace('</', '<\\/'),
                               json.dumps(chapters[0]['file'])),
               html.escape(docname), links))
    path = os.path.join(output_dir, 'index.html')
    with open(path, 'w', encoding='utf-8') as handle:
        handle.write(page)
    return path
