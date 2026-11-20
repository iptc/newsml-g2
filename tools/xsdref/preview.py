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

The page frame, stylesheet, script, fonts and logo are shared with the
Specification and Guidelines (tools/sitestyle) and written to the output's
assets/ folder. No CDN: it has to work offline on a laptop in a meeting.
"""

from __future__ import annotations

import csv
import html
import json
import os
import re
import shutil
import subprocess

import sitestyle

# The document roots, listed first because they are where a reader starts.
ITEM_TYPES = (
    'newsItem', 'packageItem', 'conceptItem', 'knowledgeItem',
    'planningItem', 'catalogItem', 'newsMessage',
)

# The schema version the pages describe, set by build(). Every page carries it
# in the header, and a hard-coded value went stale the first time the tool was
# run against a newer schema.
VERSION = ''

# Which navigation groups roll up into which headline figure on the landing
# page. A group absent from here is reported nowhere, which is how 77 datatype
# pages came to be missing from the reference's own summary; the build now
# refuses rather than quietly under-reporting.
STAT_GROUPS = (
    ('elements', ('Item types', 'Elements')),
    ('datatypes', ('Datatypes',)),
    ('attribute groups', ('Attribute groups',)),
)


def landing_stats(groups, page_count, search_count):
    """
    The landing page's headline figures, with the counts that produced them.

    Kept in one place and derived from the same data the navigation is built
    from. The figures drifted once already: page count was taken from the
    search index, which stopped being one-entry-per-page the moment attributes
    were indexed, so the page claimed 785 pages when there were 301.
    """
    counts = {heading: len(names) for heading, names, _ in groups}
    reported = {group for _, sources in STAT_GROUPS for group in sources}
    unreported = sorted(set(counts) - reported)
    if unreported:
        raise SystemExit(
            'navigation group(s) %s appear in the left index but in no '
            'landing-page figure.\nAdd them to STAT_GROUPS in preview.py, or '
            'fold them into an existing figure.' % ', '.join(unreported))

    stats = [('pages', page_count)]
    for label, sources in STAT_GROUPS:
        stats.append((label, sum(counts.get(source, 0) for source in sources)))
    stats.append(('searchable names', search_count))
    return stats


# Filled in during build(), for the landing page's counts.
SEARCH_COUNT = [0]

HEADING_RE = re.compile(
    r'<h([23])\s+id="([^"]+)"[^>]*>(.*?)</h\1>', re.S)
TAG_RE = re.compile(r'<[^>]+>')
TITLE_RE = re.compile(r'<h1[^>]*>(.*?)</h1>', re.S)


def _text(fragment):
    return html.unescape(TAG_RE.sub('', fragment)).strip()


def _source_title(pages_dir, name):
    """The `= Title` line of the AsciiDoc page, which --embedded drops."""
    source = os.path.join(pages_dir, name + '.adoc')
    if not os.path.isfile(source):
        return None
    with open(source, encoding='utf-8') as handle:
        for line in handle:
            if line.startswith('= '):
                return line[2:].strip()
            if line.strip() and not line.startswith(':'):
                break
    return None


def _label_text(name):
    """Last resort: the filename without its page-kind prefix."""
    for prefix in ('attgroup-', 'type-'):
        if name.startswith(prefix):
            return name[len(prefix):]
    return name


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


def _copy_matrix(pages_dir, schema, matrix_dir):
    """
    Ship the Structure Matrix for this schema version alongside the pages.

    Copied in rather than linked to GitHub so the preview stays usable
    offline, which is the same reason the logo is a file here rather than a
    remote URL. Returns the filename, or None if there is no matrix to ship.
    """
    if schema is None or not matrix_dir or not os.path.isdir(matrix_dir):
        return None
    shipped = {}
    for kind in ('xlsx', 'csv'):
        name = 'NewsML-G2_%s-structure-matrix.%s' % (schema.version, kind)
        source = os.path.join(matrix_dir, name)
        if os.path.isfile(source):
            shutil.copyfile(source, os.path.join(pages_dir, name))
            shipped[kind] = name
            shipped[kind + '_path'] = source
    return shipped or None


def classify(names):
    """
    Group pages for the left index.

    A flat list of 224 entries is technically complete and practically
    unusable. Item types come first because they are document roots and the
    place a reader starts; attribute groups are separated because they are a
    different kind of thing from an element.
    """
    items, attribute_groups, datatypes, elements = [], [], [], []
    for name in names:
        if name == 'index':
            continue
        if name.startswith('attgroup-'):
            attribute_groups.append(name)
        elif name.startswith('type-'):
            datatypes.append(name)
        elif name in ITEM_TYPES:
            items.append(name)
        else:
            elements.append(name)
    items.sort(key=lambda n: ITEM_TYPES.index(n))
    return [
        ('Item types', items, True),
        ('Elements', sorted(elements, key=str.lower), False),
        ('Attribute groups', attribute_groups, False),
        ('Datatypes', sorted(datatypes, key=str.lower), False),
    ]


def _label(name):
    if name.startswith('attgroup-'):
        return name[len('attgroup-'):]
    if name.startswith('type-'):
        return name[len('type-'):]
    return '&lt;%s&gt;' % name


def _csv_shape(path):
    """Data rows and columns in a matrix CSV, for the caption on its link."""
    with open(path, encoding='utf-8', newline='') as handle:
        rows = list(csv.reader(handle))
    return len(rows) - 1, len(rows[0]) if rows else 0


def build(output_dir, schema=None, matrix_dir=None):
    global VERSION
    VERSION = schema.version if schema is not None else ''
    pages_dir = os.path.join(output_dir, 'pages')
    names = render_fragments(pages_dir)
    sitestyle.write_assets(output_dir)
    matrix = _copy_matrix(pages_dir, schema, matrix_dir)
    groups = classify(names)
    index = []

    for name in names:
        if name == 'index':
            continue
        path = os.path.join(pages_dir, name + '.html')
        with open(path, encoding='utf-8') as handle:
            fragment = handle.read()

        # `asciidoctor --embedded` omits the document title, so it has to come
        # from the source. Falling back to the filename looked right only for
        # elements, where the two coincide; every datatype and attribute-group
        # page was titled `type-QCodeType` or `attgroup-commonPowerAttributes`
        # in its heading, its tab and its search result.
        title_match = TITLE_RE.search(fragment)
        if title_match:
            title = _text(title_match.group(1))
        else:
            title = _source_title(pages_dir, name) or _label_text(name)
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

    # Count pages before the index grows attribute entries: these are two
    # different quantities and conflating them reported 785 pages when there
    # are 301.
    page_count = len(index)

    if schema is not None:
        index.extend(attribute_index(schema))

    SEARCH_COUNT[0] = len(index)
    with open(os.path.join(pages_dir, 'search-index.json'), 'w',
              encoding='utf-8') as handle:
        json.dump(index, handle, separators=(',', ':'))

    with open(os.path.join(pages_dir, 'index.html'), 'w',
              encoding='utf-8') as handle:
        handle.write(landing_html(groups, page_count, schema, matrix))

    return len(index)


def _sidebar(groups, current=None):
    out = []
    for heading, names, _ in groups:
        if not names:
            continue
        out.append('<p class="nav-part">%s</p>' % heading)
        for name in names:
            cls = ' class="active"' if name == current else ''
            out.append('<a href="%s.html"%s><code>%s</code></a>'
                       % (name, cls, _label(name)))
    return '\n'.join(out)


def _page(title, sidebar, article, headings=()):
    body = sitestyle.frame('Schema reference', VERSION, sidebar,
                           '<article>%s</article>' % article, sitestyle.toc(headings))
    return sitestyle.document(title, body, 'NewsML-G2 Schema reference')


def page_html(name, title, body, headings, groups):
    article = ('<p class="kicker">NewsML-G2 schema reference</p><h1>%s</h1>\n%s'
               % (html.escape(title), body))
    return _page(title, _sidebar(groups, current=name), article, headings)


def _architecture(schema):
    """
    The News Architecture family, generated rather than drawn.

    The Guidelines carry this as a PNG (images/G2FamilyGenes.png). Deriving it
    from the schema instead means every box links to its page, the definitions
    are the schema's own and cannot drift from it, and it stays legible at any
    size. It also shows what the drawing leaves out: newsMessage, which is not
    an Item at all.

    The relationship is real and checkable — all six Item types declare
    AnyItemType as their base, and newsMessage declares none.
    """
    if schema is None:
        return ''

    derived, envelope = [], []
    for name in ITEM_TYPES:
        ref = schema.elements.get(name)
        if ref is None:
            continue
        declaration = ref.declarations[0]
        card = (name, ref.doc or '', len(declaration.children),
                declaration.base_type)
        (derived if declaration.base_type == 'AnyItemType' else envelope).append(card)

    def cards(items, full_width=False):
        out = []
        for name, doc, children, _ in items:
            out.append(
                '<a class="item%s" href="%s.html">'
                '<code>&lt;%s&gt;</code>'
                '<span class="d">%s</span>'
                '<span class="n">%d child elements</span></a>'
                % (' wide' if full_width else '', name, name,
                   html.escape(doc), children))
        return ''.join(out)

    return """
<h2>The News Architecture family</h2>
<p>Pick the one that matches what you are sending and follow its content model
down. <code>&lt;newsMessage&gt;</code> is the transport envelope: it carries
Items rather than content of its own.</p>
<div class="arch">%s%s</div>
""" % (cards(derived), cards(envelope, full_width=True))


def landing_html(groups, page_count, schema=None, matrix=None):
    article = """<p class="kicker">NewsML-G2 %s</p>
<h1>Schema Reference</h1>
<p>Generated from <code>NewsML-G2_%s-spec-All-Power.xsd</code>. Every element
name in the schema has a page giving its definition, the contexts it is
declared in, its content model and its attributes, with any User Note or
Implementation Note from Specification &sect;14 merged in.</p>
<div class="stats">%s</div>
%s
%s
<h2>Finding things</h2>
<p>Press <kbd>/</kbd> to search. Both elements and attributes are indexed, so
<code>@residref</code> finds the attribute and <code>residref</code> finds
everything mentioning it; each result says where it is declared, because a name
like <code>@role</code> appears in many places with different meanings. The
search also covers the Specification and Guidelines.</p>
""" % (html.escape(VERSION), html.escape(VERSION),
       ''.join('<span class="stat"><b>%d</b><span>%s</span></span>'
               % (value, label)
               for label, value in landing_stats(
                   groups, page_count, SEARCH_COUNT[0])),
       _architecture(schema), _matrix_section(matrix, schema))
    return _page('Schema Reference', _sidebar(groups), article)


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


def _matrix_section(matrix, schema):
    """
    Point at the Structure Matrix, and say what it is for.

    Useful for the attributes that reach many elements through a group. An
    attribute declared on a single element is already answered by that
    element's page; `@creator` arrives on 195 elements through
    commonPowerAttributes, and no page lists them.
    """
    if not matrix:
        return ''
    version = schema.version if schema is not None else ''
    links = []
    if matrix.get('xlsx'):
        links.append('<a class="dl" href="%s"><b>NewsML-G2 %s structure matrix</b>'
                     '<span>Excel workbook &middot; shaded by attribute group and '
                     'element category</span></a>' % (matrix['xlsx'], version))
    if matrix.get('csv'):
        rows, columns = _csv_shape(matrix['csv_path'])
        links.append('<a class="dl" href="%s"><b>Same data in CSV format</b>'
                     '<span>%d elements &times; %d columns &middot; for scripts '
                     'and diffs</span></a>' % (matrix['csv'], rows, columns))
    return """
<h2>Structure matrix</h2>
<p>Every element against every attribute. The pages above answer &ldquo;what
can this element carry?&rdquo;; the matrix answers it in bulk, and records which
document roots each element is reachable from. Most useful for the attributes
that arrive through a group &mdash; <code>@creator</code> reaches 195 elements
through <code>commonPowerAttributes</code>. It replaces the spreadsheet that was
maintained by hand and last revised for 2.27.</p>
<p class="dls">%s</p>
<p>Matrices for 2.28 onwards are generated from each released schema and
committed alongside them in
<a href="https://github.com/iptc/newsml-g2/tree/main/documentation/structure-matrix"
   target="_blank" rel="noopener">documentation/structure-matrix</a>.</p>
""" % ''.join(links)
