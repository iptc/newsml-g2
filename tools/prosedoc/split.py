# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 International Press Telecommunications Council (IPTC)
# The MIT License — see LICENSE in the repository root.

"""
Split a rendered NewsML-G2 book into per-chapter fragments.

The input is the single-page HTML that `asciidoctor-to-html.sh` already
produces in the specification and guidelines repositories, not the AsciiDoc
sources. That is a deliberate, and temporary, choice — see README.md.

Working from the rendered book keeps the section numbering IPTC documents cite
(2.6.1 and so on) byte for byte, because it is the same string Asciidoctor
produced. Reconstructing it from chapter sources would mean reimplementing
Asciidoctor's numbering and hoping the two agree.
"""

from __future__ import annotations

import re

from lxml import html as LH

NUMBERED = re.compile(r'^\d+\.')


def slug(anchor):
    """
    Collapse the runs of hyphens the original Word conversion left behind:
    `representing-news---newsitem` becomes `representing-news-newsitem`.
    """
    return re.sub(r'-{2,}', '-', anchor or '').strip('-')


def split_book(path):
    """
    Parse the book into chapters. Returns a list of dicts.

    Parsed rather than sliced. Asciidoctor wraps each chapter in
    `<div class="sect1"><h2>…</h2><div class="sectionbody">…</div></div>`, so
    cutting the HTML string at heading positions severs those wrappers: each
    chunk then carries a stray closing tag and lacks its opening one. The div
    counts still balance across the chunk, so that damage does not show up in a
    tag count — it shows up in the browser, which reparents whatever follows.
    """
    root = LH.parse(path).getroot()
    content = root.get_element_by_id('content')
    chapters = []
    for sect in content.xpath('./div[@class="sect1"]'):
        heading = sect.find('h2')
        if heading is None:
            continue
        anchor = heading.get('id') or ''
        heads = [(sub.tag[1], sub.get('id') or '',
                  ' '.join(sub.text_content().split()))
                 for sub in sect.xpath('.//h3|.//h4')]
        title = ' '.join(heading.text_content().split())
        sect.remove(heading)
        chapters.append({
            'file': slug(anchor),
            'anchor': anchor,
            'title': title,
            'heads': heads,
            'body': ''.join(LH.tostring(child, encoding='unicode')
                            for child in sect),
        })
    return chapters


def group_front_matter(chapters):
    """
    Fold the unnumbered sections that open a document into one Preface page.

    Only the leading run. The Guidelines close with an unnumbered "Additional
    Resources", which is a section in its own right rather than front matter.

    Folded sections keep their headings, demoted one level, so the Preface
    behaves like any other chapter: its sections appear in the left navigation
    and their sub-headings on the right.
    """
    lead = []
    for chapter in chapters:
        if NUMBERED.match(chapter['title']):
            break
        lead.append(chapter)
    if len(lead) < 2:
        return chapters

    body, heads = [], []
    for chapter in lead:
        demoted = re.sub(r'<(/?)h4\b', r'<\g<1>h5', chapter['body'])
        demoted = re.sub(r'<(/?)h3\b', r'<\g<1>h4', demoted)
        body.append('<h3 id="%s">%s</h3>%s' % (chapter['anchor'],
                                               chapter['title'], demoted))
        heads.append(('3', chapter['anchor'], chapter['title']))
        heads.extend(('4', a, t) for level, a, t in chapter['heads']
                     if level == '3')

    preface = {'file': 'preface', 'anchor': 'preface', 'title': 'Preface',
               'heads': heads, 'body': ''.join(body)}
    return [preface] + chapters[len(lead):]


ID_RE = re.compile(r'\bid="([^"]+)"')
HREF_RE = re.compile(r'href="([^"]*)"')

# Unversioned links between the two documents. Versioned ones such as
# /std/NewsML-G2/2.35/specification/ point at a release's schema folder, not at
# a book, and are left alone.
BOOK_URL = re.compile(
    r'^https?://(?:www\.)?iptc\.org/std/NewsML-G2/(specification|guidelines)/?'
    r'(?:index\.html)?(?:#(.*))?$')


def anchor_map(chapters):
    """Every id in a split book, mapped to the chapter file that now holds it."""
    found = {}
    for chapter in chapters:
        found[chapter['anchor']] = chapter['file']
        for anchor in ID_RE.findall(chapter['body']):
            found.setdefault(anchor, chapter['file'])
    return found


def book_href(folder, anchors, anchor, here=None):
    """
    The relative link to `anchor` in a book written to `../folder/`.

    `here` is the folder of the page the link sits on, so a link within the
    same book stays a sibling filename rather than climbing out and back.
    """
    target = anchors.get(anchor) if anchor else None
    page = (target or 'preface') + '.html'
    if target and anchor != target:
        page += '#' + anchor
    return page if folder == here else '../%s/%s' % (folder, page)


def rewrite_links(chapters, folder, maps):
    """
    Point cross-references at the split pages instead of the single-page book.

    `maps` holds the anchor map of every book in the site, keyed by output
    folder. In the single-page book, `#the-data-model` is on the same page
    wherever it is linked from; once split, it is only on one page, so the link
    has to name it. Links to the published books on iptc.org become links to
    the local pages, so a reader stays inside the build they are reviewing.
    """
    own = maps[folder]

    def fix(match):
        href = match.group(1)
        if href.startswith('#'):
            anchor = href[1:]
            if anchor in own:
                return 'href="%s"' % book_href(folder, own, anchor, here=folder)
            return match.group(0)
        book = BOOK_URL.match(href)
        if book and book.group(1) in maps:
            return 'href="%s"' % book_href(book.group(1), maps[book.group(1)],
                                           book.group(2), here=folder)
        return match.group(0)

    for chapter in chapters:
        chapter['body'] = HREF_RE.sub(fix, chapter['body'])
    return chapters


REVNUMBER = re.compile(r'<span id="revnumber">[^<\d]*([\d.]+)')


def book_version(path):
    """The standard version a rendered book states in its header, e.g. 2.35."""
    with open(path, encoding='utf-8') as handle:
        match = REVNUMBER.search(handle.read())
    return match.group(1) if match else ''
