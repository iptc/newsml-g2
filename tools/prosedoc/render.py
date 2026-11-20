# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 International Press Telecommunications Council (IPTC)
# The MIT License — see LICENSE in the repository root.

"""
Render split chapters into the documentation site's page frame.

The frame, stylesheet and script are shared with the schema reference (see
tools/sitestyle): parts and search across the top, the book's chapters down
the left with the current chapter's sections expanded, and the sub-headings of
the current chapter on the right.
"""

from __future__ import annotations

import html
import json
import os
import re

import sitestyle

CHAPTER_NUMBER = re.compile(r'^(\d+)\.\s+(.*)$')


def _numbered(title):
    """Split "2. Representing News" into ("2", "Representing News")."""
    match = CHAPTER_NUMBER.match(title)
    return match.groups() if match else ('', title)


def _sidebar(chapters, current, docname):
    """
    Chapters, with the current one expanded to show its sections.

    The section level is h3, not h2: the chapter title is the only h2 in both
    documents, so expanding h2 would show a single entry repeating the title.
    """
    out = ['<p class="nav-part">%s</p>' % html.escape(docname)]
    for chapter in chapters:
        number, text = _numbered(chapter['title'])
        here = chapter is current
        out.append('<a href="%s.html"%s><span class="n">%s</span>%s</a>'
                   % (chapter['file'], ' class="active"' if here else '',
                      number, html.escape(text)))
        if here:
            subs = ['<a href="#%s">%s</a>' % (anchor, html.escape(text))
                    for level, anchor, text in chapter['heads'] if level == '3']
            if subs:
                out.append('<div class="subs">%s</div>' % ''.join(subs))
    return '\n'.join(out)


def _pagenav(chapters, index):
    out = []
    if index:
        out.append('<a href="%s.html"><span>Previous</span>%s</a>'
                   % (chapters[index-1]['file'], html.escape(chapters[index-1]['title'])))
    if index < len(chapters) - 1:
        out.append('<a class="next" href="%s.html"><span>Next</span>%s</a>'
                   % (chapters[index+1]['file'], html.escape(chapters[index+1]['title'])))
    return '<nav class="pagenav">%s</nav>' % ''.join(out)


def write_pages(chapters, output_dir, docname, version='', stem=''):
    """
    Write one page per chapter. Returns the paths written.

    `stem` is the book's MathJax markup, added only to chapters that use it.
    """
    os.makedirs(output_dir, exist_ok=True)
    written = []
    for index, chapter in enumerate(chapters):
        number, text = _numbered(chapter['title'])
        article = ('<article class="book"><p class="kicker">NewsML-G2 %s</p>'
                   '<h1 id="%s">%s%s</h1>%s</article>%s'
                   % (html.escape(docname), chapter['anchor'],
                      '<span class="chnum">%s</span>' % number if number else '',
                      html.escape(text), chapter['body'], _pagenav(chapters, index)))
        heads = [(('2' if level == '3' else '3'), anchor, text)
                 for level, anchor, text in chapter['heads']]
        body = sitestyle.frame(docname, version, _sidebar(chapters, chapter, docname),
                               article, sitestyle.toc(heads))
        if chapter.get('stem'):
            body += stem
        page = sitestyle.document(chapter['title'], body, 'NewsML-G2 %s' % docname)
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
