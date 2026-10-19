#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 International Press Telecommunications Council (IPTC)
# The MIT License — see LICENSE in the repository root.

"""
Build the Specification and Guidelines into the shared documentation shell.

    tools/prosedoc/generate.py --all
    tools/prosedoc/generate.py --book ../newsml-g2-specification/index.html \
                               --name Specification --output build/site
"""

from __future__ import annotations

import argparse
import os
import sys

try:
    from prosedoc import render, split
except ImportError:                                   # run as a script
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from prosedoc import render, split

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Both documents still live in their own repositories and are still built by a
# hand-run shell script. Until that changes these paths are a guess about the
# working copy next door, which is the single least maintainable thing here.
BOOKS = (
    ('Specification', 'newsml-g2-specification/index.html', 'specification'),
    ('Guidelines', 'newsml-g2-guidelines/index.html', 'guidelines'),
)


def load_book(path):
    """Split one rendered book. Returns (chapters, version), or None if absent."""
    if not os.path.isfile(path):
        print('not found: %s' % path)
        print('  This tool reads the built single-page HTML, which is produced '
              'by asciidoctor-to-html.sh in that repository. Run it there first.')
        return None
    chapters = split.group_front_matter(split.split_book(path))
    if not chapters:
        print('no chapters found in %s' % path)
        return None
    return chapters, split.book_version(path)


def build_books(books, output, verbose=False):
    """
    Build several books as sibling folders of one site.

    All are split before any is written, because a link from one book into the
    other can only be resolved once both anchor maps exist.
    """
    loaded = {}
    for name, path, folder in books:
        book = load_book(path)
        if book is None:
            return 1
        loaded[folder] = (name, book[0], book[1])
    maps = {folder: split.anchor_map(chapters)
            for folder, (_, chapters, _) in loaded.items()}
    for folder, (name, chapters, version) in loaded.items():
        split.rewrite_links(chapters, folder, maps)
        output_dir = os.path.join(output, folder)
        written = render.write_pages(chapters, output_dir, name, version)
        print('%-14s %2d chapters -> %s'
              % (name, len(written), os.path.relpath(output_dir, REPO_ROOT)))
        if verbose:
            for chapter in chapters:
                print('   %-46s %s' % (chapter['file'] + '.html', chapter['title']))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.strip().split('\n')[0])
    parser.add_argument('--book', help='path to a rendered single-page book')
    parser.add_argument('--name', default='Specification')
    parser.add_argument('--all', action='store_true',
                        help='build both books from the sibling repositories')
    parser.add_argument('--repos', default=os.path.dirname(REPO_ROOT),
                        help='folder holding the specification and guidelines '
                             'repositories (default: beside this one)')
    parser.add_argument('--output', default=os.path.join(REPO_ROOT, 'build', 'site'))
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args(argv)

    if not (args.book or args.all):
        parser.print_help()
        return 2

    if args.all:
        books = [(name, os.path.join(args.repos, relative), folder)
                 for name, relative, folder in BOOKS]
        return build_books(books, args.output, args.verbose)

    return build_books([(args.name, args.book, args.name.lower())],
                       args.output, args.verbose)


if __name__ == '__main__':
    sys.exit(main())
