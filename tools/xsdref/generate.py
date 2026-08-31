#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 International Press Telecommunications Council (IPTC)
# The MIT License — see LICENSE in the repository root.

"""
Generate the NewsML-G2 schema reference from the XML Schema.

Replaces the hand-run Altova XMLSpy step (MAINTENANCE.md step 13) and the
hand-maintained Structure Matrix spreadsheet.

    # report §14 annotations that no longer match the schema (exit 1 if any)
    tools/xsdref/generate.py --check

    # regenerate the Structure Matrix for every version in releases/
    tools/xsdref/generate.py --matrix --all-versions

    # write the AsciiDoc reference pages
    tools/xsdref/generate.py --pages --output build/reference
"""

from __future__ import annotations

import argparse
import glob
import os
import sys

if __package__ in (None, ''):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from xsdref import matrix, notes, preview, render, schema as schema_module
else:
    from . import matrix, notes, preview, render
    from . import schema as schema_module

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DEFAULT_SCHEMA_GLOB = os.path.join(
    REPO_ROOT, 'specification', 'NewsML-G2_*-spec-All-Power.xsd'
)

# The specification lives in a sibling repository, so its location is a flag
# rather than an assumption. --check is skipped with a clear message when it is
# not present, instead of failing a build for something outside this repo.
DEFAULT_SPEC_CHAPTER = os.path.join(
    REPO_ROOT, os.pardir, 'newsml-g2-specification',
    '_includes', 'chapters', '14_Specification_Reference.adoc',
)


def default_schema():
    candidates = sorted(glob.glob(DEFAULT_SCHEMA_GLOB))
    if not candidates:
        raise SystemExit('no Power schema found at %s' % DEFAULT_SCHEMA_GLOB)
    return candidates[-1]


def release_schemas():
    """Every released Power schema in the repository, oldest first."""
    pattern = os.path.join(
        REPO_ROOT, 'releases', '*', 'specification',
        'NewsML-G2_*-spec-All-Power.xsd',
    )
    found = {}
    for path in glob.glob(pattern):
        version = os.path.basename(os.path.dirname(os.path.dirname(path)))
        found[version] = path
    return [found[key] for key in sorted(found, key=_version_key)]


def _version_key(version):
    try:
        return tuple(int(part) for part in version.split('.'))
    except ValueError:
        return (0,)


def run_check(schema, spec_chapter, verbose=False):
    """Report §14 annotations that do not bind to the schema."""
    if not os.path.isfile(spec_chapter):
        print('skipping --check: specification chapter not found at\n  %s'
              % spec_chapter)
        print('Pass --spec-chapter to point at it.')
        return 0

    parsed, unbound = notes.parse(spec_chapter)

    for line, heading, section in unbound:
        print('UNBOUND  %s:%d  cannot bind heading %r (%s).'
              % (os.path.basename(spec_chapter), line + 1, heading, section))
        print('         Add it to HEADING_OVERRIDES in tools/xsdref/notes.py.')

    problems = notes.check(schema, parsed, spec_chapter)
    for problem in problems:
        print('MISMATCH %s' % problem)

    if verbose:
        print('\n%d annotations parsed from §14, %d bound cleanly.'
              % (len(parsed), len(parsed) - len(problems)))

    total = len(problems) + len(unbound)
    if total:
        print('\n%d problem(s). The specification and the schema disagree.' % total)
    else:
        print('All %d §14 annotations match schema %s.' % (len(parsed), schema.version))
    return 1 if total else 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Generate the NewsML-G2 schema reference.',
    )
    parser.add_argument('--schema', help='path to an All-Power XSD')
    parser.add_argument('--spec-chapter', default=DEFAULT_SPEC_CHAPTER,
                        help='path to 14_Specification_Reference.adoc')
    parser.add_argument('--check', action='store_true',
                        help='verify §14 annotations against the schema')
    parser.add_argument('--matrix', action='store_true',
                        help='write the Structure Matrix as CSV')
    parser.add_argument('--pages', action='store_true',
                        help='write the AsciiDoc reference pages')
    parser.add_argument('--partials', action='store_true',
                        help='write §14 annotations as per-construct partials')
    parser.add_argument('--verify-matrix', action='store_true',
                        help='fail if a committed Structure Matrix is out of '
                             'date with its schema (for CI)')
    parser.add_argument('--all-versions', action='store_true',
                        help='with --matrix or --verify-matrix, apply to every '
                             'released schema')
    parser.add_argument('--matrix-dir',
                        default=os.path.join(REPO_ROOT, 'documentation', 'structure-matrix'),
                        help='where committed Structure Matrix CSVs live')
    parser.add_argument('--output', default=os.path.join(REPO_ROOT, 'build', 'reference'),
                        help='output directory')
    parser.add_argument('--xlsx', action='store_true',
                        help='also write the Structure Matrix as a styled '
                             'workbook (needs openpyxl)')
    parser.add_argument('--preview', action='store_true',
                        help='render the pages to a browsable HTML preview '
                             '(implies --pages; needs asciidoctor on PATH)')
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args(argv)

    if args.preview:
        args.pages = True

    if not any([args.check, args.matrix, args.pages, args.partials,
                args.verify_matrix, args.xlsx]):
        parser.error('nothing to do: pass --check, --matrix, --verify-matrix, '
                     '--pages or --partials')

    exit_code = 0

    def matrix_path(version):
        return os.path.join(
            args.matrix_dir, 'NewsML-G2_%s-structure-matrix.csv' % version
        )

    if args.matrix and args.all_versions:
        paths = release_schemas()
        if not paths:
            print('no released schemas found under releases/')
        for path in paths:
            loaded = schema_module.load(path)
            target = matrix_path(loaded.version)
            rows, columns = matrix.write_csv(loaded, target)
            print('%s  %d elements x %d columns  -> %s'
                  % (loaded.version, rows, columns, os.path.relpath(target, REPO_ROOT)))
        if not (args.check or args.pages or args.partials or args.verify_matrix):
            return exit_code

    if args.xlsx:
        targets = release_schemas() if args.all_versions else [
            args.schema or default_schema()]
        for target in targets:
            loaded_x = schema_module.load(target)
            out = os.path.join(
                args.matrix_dir,
                'NewsML-G2_%s-structure-matrix.xlsx' % loaded_x.version)
            count, uncategorised = matrix.write_xlsx(loaded_x, out)
            print('%-5s %3d elements -> %s'
                  % (loaded_x.version, count, os.path.relpath(out, REPO_ROOT)))
            if uncategorised:
                print('      no category yet — add to '
                      'tools/xsdref/assets/element-categories.csv:')
                for item in uncategorised:
                    print('        %s' % item)
        if not (args.check or args.pages or args.partials or args.verify_matrix
                or args.matrix):
            return exit_code

    if args.verify_matrix:
        targets = release_schemas() if args.all_versions else [
            args.schema or default_schema()
        ]
        stale = 0
        for path in targets:
            loaded = schema_module.load(path)
            differences = matrix.verify_csv(loaded, matrix_path(loaded.version))
            if differences:
                stale += 1
                print('STALE %s Structure Matrix:' % loaded.version)
                for difference in differences:
                    print('      %s' % difference)
            elif args.verbose:
                print('%s Structure Matrix up to date.' % loaded.version)
        if stale:
            print('\n%d Structure Matrix file(s) out of date. '
                  'Regenerate with --matrix --all-versions.' % stale)
            exit_code |= 1
        else:
            print('All %d Structure Matrix file(s) up to date.' % len(targets))
        if not (args.check or args.pages or args.partials or args.matrix):
            return exit_code

    schema_path = args.schema or default_schema()
    loaded = schema_module.load(schema_path)
    if args.verbose:
        print('schema %s (%s)\n' % (loaded.version, os.path.relpath(schema_path, REPO_ROOT)))

    if args.check:
        exit_code |= run_check(loaded, args.spec_chapter, args.verbose)

    if args.matrix and not args.all_versions:
        target = matrix_path(loaded.version)
        rows, columns = matrix.write_csv(loaded, target)
        print('Structure Matrix: %d elements x %d columns -> %s'
              % (rows, columns, os.path.relpath(target, REPO_ROOT)))

    parsed = []
    if args.pages or args.partials:
        if os.path.isfile(args.spec_chapter):
            parsed, _ = notes.parse(args.spec_chapter)
        else:
            print('note: §14 annotations not merged (chapter not found at %s)'
                  % args.spec_chapter)

    if args.partials:
        target = os.path.join(args.output, 'partials', 'notes')
        written = notes.write_partials(parsed, target)
        print('§14 partials: %d -> %s'
              % (len(written), os.path.relpath(target, REPO_ROOT)))

    if args.pages or args.check:
        dangling = loaded.dangling_references()
        if dangling:
            for kind, name, where in dangling:
                print('UNRESOLVED %s ref="%s" in %s' % (kind, name, where))
            print('\n%d unresolved reference(s). Generated pages would be '
                  'silently incomplete.' % len(dangling))
            exit_code |= 1

    if args.pages:
        target = os.path.join(args.output, 'pages')
        written = render.write_pages(loaded, parsed, target)
        render.write_nav(loaded, os.path.join(args.output, 'nav.adoc'))
        print('reference pages: %d -> %s'
              % (len(written), os.path.relpath(target, REPO_ROOT)))

    if args.preview:
        count = preview.build(args.output, schema=loaded,
                              matrix_dir=args.matrix_dir)
        print('html preview:   %d pages -> %s'
              % (count, os.path.relpath(target, REPO_ROOT)))
        print('                open %s'
              % os.path.join(os.path.relpath(target, REPO_ROOT), 'index.html'))

    return exit_code


if __name__ == '__main__':
    sys.exit(main())
