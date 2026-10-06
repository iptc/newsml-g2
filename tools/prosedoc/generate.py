#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 International Press Telecommunications Council (IPTC)
# The MIT License — see LICENSE in the repository root.

"""
Build the Specification and Guidelines into the shared documentation shell.

    tools/prosedoc/generate.py --all
    tools/prosedoc/generate.py --book ../newsml-g2-specification/index.html \
                               --name Specification --output build/docs/specification
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
    ('Specification', '../newsml-g2-specification/index.html', 'specification'),
    ('Guidelines', '../newsml-g2-guidelines/index.html', 'guidelines'),
)


def build_book(path, name, output_dir, verbose=False):
    if not os.path.isfile(path):
        print('not found: %s' % path)
        print('  This tool reads the built single-page HTML, which is produced '
              'by asciidoctor-to-html.sh in that repository. Run it there first.')
        return 1
    chapters = split.group_front_matter(split.split_book(path))
    if not chapters:
        print('no chapters found in %s' % path)
        return 1
    written = render.write_pages(chapters, output_dir, name)
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
    parser.add_argument('--output', default=os.path.join(REPO_ROOT, 'build', 'docs'))
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args(argv)

    if not (args.book or args.all):
        parser.print_help()
        return 2

    if args.all:
        status = 0
        for name, relative, folder in BOOKS:
            path = os.path.normpath(os.path.join(REPO_ROOT, relative))
            status |= build_book(path, name,
                                 os.path.join(args.output, folder), args.verbose)
        return status

    return build_book(args.book, args.name,
                      os.path.join(args.output, args.name.lower()), args.verbose)


if __name__ == '__main__':
    sys.exit(main())
