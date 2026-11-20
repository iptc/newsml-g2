# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 International Press Telecommunications Council (IPTC)
# The MIT License — see LICENSE in the repository root.

"""
The look shared by every page of the NewsML-G2 documentation site.

The Specification and Guidelines (tools/prosedoc) and the schema reference
(tools/xsdref) are written by different tools but are one site, so the page
frame — draft bar, top bar, sidebar, footer — and the stylesheet, script, fonts
and logo live here. The house style is the IPTC one the Media Provenance guide
uses (media-provenance-guide.iptc.org).

Every page sits one folder below the site root (specification/, guidelines/,
reference/), so the assets are linked as ../assets/ and written there by
write_assets().
"""

from __future__ import annotations

import html
import os
import shutil

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')

# Relative to a page. The books and the reference are sibling folders of one
# site (see tools/docsite.py). True marks an off-site link.
TOP_LINKS = (
    ('Specification', '../specification/preface.html', False),
    ('Guidelines', '../guidelines/preface.html', False),
    ('Schema reference', '../reference/index.html', False),
    ('Examples', 'https://github.com/iptc/newsml-g2/tree/main/examples', True),
    ('Schemas', 'https://github.com/iptc/newsml-g2/tree/main/specification', True),
)

DRAFT_NOTE = 'NewsML-G2 %s documentation — preview, not the published site'


def write_assets(site_root):
    """Copy the stylesheet, script, fonts and logo to `site_root`/assets."""
    target = os.path.join(site_root, 'assets')
    shutil.copytree(ASSETS, target, dirs_exist_ok=True)
    return target


def document(title, body, site_title='NewsML-G2'):
    """A whole page: head, `body` markup, and the site script."""
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            '<title>%s — %s</title>\n'
            '<link rel="stylesheet" href="../assets/site.css">\n'
            '</head>\n<body>\n%s\n<script src="../assets/site.js"></script>\n'
            '</body></html>\n' % (html.escape(title), html.escape(site_title), body))


def header(here, version):
    """
    The draft bar and top bar. `here` is the label of the current part.

    The menu checkbox follows the header so that the stylesheet can open the
    sidebar on small screens with `#navtoggle:checked ~ .layout`.
    """
    links = []
    for label, href, external in TOP_LINKS:
        classes = (['here'] if label == here else []) + (['ext'] if external else [])
        links.append('<a href="%s"%s%s>%s</a>' % (
            href, ' class="%s"' % ' '.join(classes) if classes else '',
            ' target="_blank" rel="noopener"' if external else '', label))
    return """<div class="draftbar">%s</div>
<header class="topbar">
  <a class="brand" href="../specification/preface.html">
    <img src="../assets/iptc-logo.svg" alt="IPTC" class="logo">
    <span class="brand-text"><strong>NewsML-G2</strong><span class="for">Documentation%s</span></span>
  </a>
  <nav class="parts">%s</nav>
  <div class="search">
    <input id="q" type="search" placeholder="Press / to search the documentation"
           autocomplete="off" spellcheck="false" aria-label="Search the documentation">
    <div class="results" id="r"></div>
  </div>
  <label class="menu-toggle" for="navtoggle">Menu</label>
</header>
<input type="checkbox" id="navtoggle" hidden>""" % (
        html.escape(DRAFT_NOTE % version if version else DRAFT_NOTE.replace(' %s', '')),
        ' · version %s' % html.escape(version) if version else '',
        ''.join(links))


def frame(here, version, sidebar, main, toc=''):
    """Header, the three-column layout, and the footer."""
    return """%s
<div class="layout">
<nav class="sidebar">%s</nav>
<main>%s</main>
%s
</div>
<footer>
  <p>© 2026 International Press Telecommunications Council (IPTC). Licensed under
     <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>.</p>
  <p><a rel="external" href="https://iptc.org/standards/newsml-g2/">NewsML-G2</a>
     is a standard of the IPTC.</p>
</footer>""" % (header(here, version), sidebar, main,
                toc or '<nav class="toc"></nav>')


def toc(headings):
    """The "On this page" column from (level, anchor, text); level '3' is indented."""
    if not headings:
        return ''
    out = ['<nav class="toc"><h2>On this page</h2>']
    for level, anchor, text in headings:
        out.append('<a href="#%s"%s>%s</a>' % (
            html.escape(anchor), ' class="l3"' if level == '3' else '', html.escape(text)))
    out.append('</nav>')
    return ''.join(out)
