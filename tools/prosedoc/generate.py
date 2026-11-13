#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 International Press Telecommunications Council (IPTC)
# The MIT License — see LICENSE in the repository root.

"""
Build the Specification and Guidelines into the shared documentation shell.

    tools/prosedoc/generate.py --all
    tools/prosedoc/generate.py --book docs-src/specification/IPTC-G2-Specification.adoc \
                               --name Specification --output build/site

Each book is rendered from its AsciiDoc master document in docs-src/, split
into chapters, and written with the images it uses. Needs asciidoctor on PATH.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

try:
    from prosedoc import render, split
except ImportError:                                   # run as a script
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from prosedoc import render, split

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BOOKS = (
    ('Specification', 'docs-src/specification/IPTC-G2-Specification.adoc', 'specification'),
    ('Guidelines', 'docs-src/guidelines/IPTC-G2-Implementation_Guide.adoc', 'guidelines'),
)


def render_master(source, work):
    """
    Render a book's master document to single-page HTML in `work`.

    The whole book, not chapter by chapter: the master document is what
    numbers the sections. Any Asciidoctor warning — an include or image that
    does not resolve, a duplicate anchor — fails the build, so a broken source
    cannot slip into the site.
    """
    target = os.path.join(work, os.path.splitext(os.path.basename(source))[0] + '.html')
    try:
        subprocess.run(
            ['asciidoctor', '--failure-level', 'WARN',
             '-o', target, os.path.basename(source)],
            cwd=os.path.dirname(os.path.abspath(source)), check=True,
        )
    except FileNotFoundError:
        raise SystemExit('asciidoctor is not on PATH. Install it with '
                         '`gem install asciidoctor`.')
    except subprocess.CalledProcessError:
        raise SystemExit('asciidoctor reported problems in %s (see above)' % source)
    return target


def load_book(path):
    """Split one rendered book. Returns (chapters, version, stem scripts)."""
    chapters = split.group_front_matter(split.split_book(path))
    if not chapters:
        raise SystemExit('no chapters found in %s' % path)
    return chapters, split.book_version(path), split.stem_scripts(path)


def copy_images(chapters, source_dir, output_dir):
    """Copy the images the chapters use, keeping their relative paths."""
    for src in split.image_paths(chapters):
        origin = os.path.normpath(os.path.join(source_dir, src))
        if not os.path.isfile(origin):
            raise SystemExit('image not found: %s' % origin)
        target = os.path.normpath(os.path.join(output_dir, src))
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copyfile(origin, target)


def build_books(books, output, verbose=False):
    """
    Build several books as sibling folders of one site.

    `books` holds (name, source, folder); a source is a master .adoc, or an
    already rendered single-page .html. Returns the anchor map of every book,
    keyed by folder.

    All are split before any is written, because a link from one book into the
    other can only be resolved once both anchor maps exist.
    """
    loaded = {}
    with tempfile.TemporaryDirectory() as work:
        for name, source, folder in books:
            if not os.path.isfile(source):
                raise SystemExit('not found: %s' % source)
            rendered = (render_master(source, work) if source.endswith('.adoc')
                        else source)
            loaded[folder] = (name, os.path.dirname(os.path.abspath(source)),
                              *load_book(rendered))
    maps = {folder: split.anchor_map(book[2]) for folder, book in loaded.items()}
    for folder, (name, source_dir, chapters, version, stem) in loaded.items():
        split.rewrite_links(chapters, folder, maps)
        output_dir = os.path.join(output, folder)
        written = render.write_pages(chapters, output_dir, name, version, stem)
        copy_images(chapters, source_dir, output_dir)
        print('%-14s %2d chapters -> %s'
              % (name, len(written), os.path.relpath(output_dir, REPO_ROOT)))
        if verbose:
            for chapter in chapters:
                print('   %-46s %s' % (chapter['file'] + '.html', chapter['title']))
    return maps


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.strip().split('\n')[0])
    parser.add_argument('--book', help='a master .adoc, or a rendered single-page .html')
    parser.add_argument('--name', default='Specification')
    parser.add_argument('--all', action='store_true',
                        help='build both books from docs-src/')
    parser.add_argument('--output', default=os.path.join(REPO_ROOT, 'build', 'site'))
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args(argv)

    if not (args.book or args.all):
        parser.print_help()
        return 2

    if args.all:
        books = [(name, os.path.join(REPO_ROOT, relative), folder)
                 for name, relative, folder in BOOKS]
    else:
        books = [(args.name, args.book, args.name.lower())]
    build_books(books, args.output, args.verbose)
    return 0


if __name__ == '__main__':
    sys.exit(main())
