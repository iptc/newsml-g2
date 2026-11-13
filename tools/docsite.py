#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 International Press Telecommunications Council (IPTC)
# The MIT License — see LICENSE in the repository root.

"""
Assemble the Specification, Guidelines and schema reference into one site.

    tools/docsite.py
    tools/docsite.py --schema specification/NewsML-G2_2.36-spec-All-Power.xsd \
                     --output build/site

The result is flat static HTML with only relative links between its parts:

    index.html              redirects to the Specification
    specification/*.html    one page per chapter
    guidelines/*.html       one page per chapter
    reference/*.html        one page per element, datatype and attribute group,
                            plus the search index and the Structure Matrix

so the folder can be copied as-is to any path on any web server. (Opened from
disk the pages read fine, but the reference search needs HTTP.) Everything is
built from this repository: the schema in specification/ and the book sources
in docs-src/. Needs asciidoctor on PATH.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prosedoc import generate as prose, split                          # noqa: E402
from xsdref import matrix, notes, preview, render                      # noqa: E402
from xsdref import schema as schema_module                             # noqa: E402
from xsdref.generate import default_schema                             # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMMITTED_MATRICES = os.path.join(REPO_ROOT, 'documentation', 'structure-matrix')
SPEC_CHAPTER = os.path.join(REPO_ROOT, 'docs-src', 'specification', '_includes',
                            'chapters', '14_Specification_Reference.adoc')
PARTS = ('specification', 'guidelines', 'reference')
IMG_SRC_RE = re.compile(r'(?<=<img )src="([^"]+)"')

INDEX = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta http-equiv="refresh" content="0; url=specification/preface.html">
<title>NewsML-G2 documentation</title></head>
<body><p><a href="specification/preface.html">NewsML-G2 Specification</a></p></body></html>
"""


def build_reference(loaded, spec_chapter, work, target):
    """Generate the reference pages into `work`, then copy the HTML to `target`."""
    parsed, _ = notes.parse(spec_chapter)
    notes.write_partials(parsed, os.path.join(work, 'partials', 'notes'))
    pages = os.path.join(work, 'pages')
    render.write_pages(loaded, parsed, pages)

    # A released version has its matrix committed. An unreleased one does not,
    # so generate it here rather than ship a reference without one.
    matrix_dir = COMMITTED_MATRICES
    stem = 'NewsML-G2_%s-structure-matrix' % loaded.version
    if not os.path.isfile(os.path.join(matrix_dir, stem + '.csv')):
        matrix_dir = os.path.join(work, 'matrix')
        matrix.write_csv(loaded, os.path.join(matrix_dir, stem + '.csv'))
        try:
            matrix.write_xlsx(loaded, os.path.join(matrix_dir, stem + '.xlsx'))
        except SystemExit as error:
            print('note: no .xlsx matrix (%s)' % str(error).split('\n')[0])

    count = preview.build(work, schema=loaded, matrix_dir=matrix_dir)
    os.makedirs(target)
    for name in os.listdir(pages):
        if not name.endswith('.adoc'):
            shutil.copyfile(os.path.join(pages, name), os.path.join(target, name))
    return count


def link_reference_to_books(target, maps):
    """
    Point the reference's links and images into the books at the local pages.

    §14 notes are rendered on reference pages, but their cross-references were
    written for the single-page Specification: `#the-data-model` names an
    anchor that is not on the reference page. Anchors that are on the page are
    left alone.
    """
    spec = maps['specification']
    spec_images = os.path.join(os.path.dirname(target), 'specification', 'images')
    rewritten = 0
    local_files = set(os.listdir(target))
    for name in sorted(local_files):
        if not name.endswith('.html'):
            continue
        path = os.path.join(target, name)
        with open(path, encoding='utf-8') as handle:
            page = handle.read()
        local = set(split.ID_RE.findall(page))

        def fix(match):
            href = match.group(1)
            if href.startswith('#') and href[1:] not in local and href[1:] in spec:
                return 'href="%s"' % split.book_href('specification', spec, href[1:])
            book = split.BOOK_URL.match(href)
            if book and book.group(1) in maps:
                return 'href="%s"' % split.book_href(
                    book.group(1), maps[book.group(1)], book.group(2))
            return match.group(0)

        def fix_image(match):
            # §14 notes can include Specification tables with images (the
            # orientation values), written relative to the book's imagesdir.
            # The Specification build has already copied them.
            src = match.group(1)
            if (src not in local_files and '/' not in src
                    and os.path.isfile(os.path.join(spec_images, src))):
                return 'src="../specification/images/%s"' % src
            return match.group(0)

        fixed = split.HREF_RE.sub(fix, page)
        fixed = IMG_SRC_RE.sub(fix_image, fixed)
        if fixed != page:
            with open(path, 'w', encoding='utf-8') as handle:
                handle.write(fixed)
            rewritten += 1
    return rewritten


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.strip().split('\n')[0])
    parser.add_argument('--schema', help='path to an All-Power XSD '
                                         '(default: the one in specification/)')
    parser.add_argument('--output', default=os.path.join(REPO_ROOT, 'build', 'site'))
    args = parser.parse_args(argv)

    # Only the parts this tool writes are cleared, so pointing --output at a
    # folder that holds anything else does not destroy it.
    for part in PARTS:
        shutil.rmtree(os.path.join(args.output, part), ignore_errors=True)
    os.makedirs(args.output, exist_ok=True)

    loaded = schema_module.load(args.schema or default_schema())
    with tempfile.TemporaryDirectory() as work:
        count = build_reference(loaded, SPEC_CHAPTER,
                                work, os.path.join(args.output, 'reference'))
    print('Reference      %3d pages    -> reference/ (schema %s)'
          % (count, loaded.version))

    books = [(name, os.path.join(REPO_ROOT, relative), folder)
             for name, relative, folder in prose.BOOKS]
    maps = prose.build_books(books, args.output)
    print('Reference pages linked into the books: %d'
          % link_reference_to_books(os.path.join(args.output, 'reference'), maps))

    with open(os.path.join(args.output, 'index.html'), 'w', encoding='utf-8') as handle:
        handle.write(INDEX)
    print('Site -> %s' % args.output)
    return 0


if __name__ == '__main__':
    sys.exit(main())
