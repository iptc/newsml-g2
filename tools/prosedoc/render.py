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
import os

TOP_LINKS = (
    ('Specification', 'specification/preface.html'),
    ('Guidelines', 'guidelines/preface.html'),
    ('Schema reference', '../reference/pages/index.html'),
    ('Examples', 'https://github.com/iptc/newsml-g2/tree/main/examples'),
    ('Schemas', 'https://github.com/iptc/newsml-g2/tree/main/specification'),
)

BANNER = ('<strong>Preview.</strong> Built from the published NewsML-G2 '
          'documents by <code>tools/prosedoc</code>. This layout is a harness '
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
header.top .search input{width:300px;padding:6px 10px;border-radius:5px;
border:1px solid #2c456b;background:#1a3358;color:#fff;font-size:13px}
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



def _top_bar(docname):
    links = ''.join(
        '<a href="%s"%s>%s</a>'
        % (href, ' class="here"' if label == docname else '', label)
        for label, href in TOP_LINKS)
    return ('<header class="top"><div class="brand">NewsML-G2 <span>2.35</span></div>'
            '<nav>%s</nav><div class="search"><input type="search" '
            'placeholder="Press / to search the %s"></div></header>'
            % (links, docname.lower()))


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


def write_pages(chapters, output_dir, docname):
    """Write one page per chapter. Returns the paths written."""
    os.makedirs(output_dir, exist_ok=True)
    written = []
    for index, chapter in enumerate(chapters):
        body = ('%s<div class="shell">%s<main><p class="note">%s</p>'
                '<h1>%s</h1>%s%s</main>%s</div>'
                % (_top_bar(docname), _left_index(chapters, chapter, docname),
                   BANNER, html.escape(chapter['title']), chapter['body'],
                   _pager(chapters, index), _right_toc(chapter)))
        page = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1">'
                '<title>%s</title><style>%s</style></head><body>%s</body></html>'
                % (html.escape(chapter['title']), CSS, body))
        path = os.path.join(output_dir, chapter['file'] + '.html')
        with open(path, 'w', encoding='utf-8') as handle:
            handle.write(page)
        written.append(path)
    return written
