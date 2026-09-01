# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 International Press Telecommunications Council (IPTC)
# The MIT License — see LICENSE in the repository root.

"""
Split a rendered NewsML-G2 book into per-chapter fragments.

The input is the single-page HTML that `asciidoctor-to-html.sh` already
produces in the specification and guidelines repositories, not the AsciiDoc
sources. That is a deliberate, and temporary, choice — see README.md.

Working from the rendered book keeps the section numbering people cite
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
