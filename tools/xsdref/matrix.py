# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 International Press Telecommunications Council (IPTC)
# The MIT License — see LICENSE in the repository root.

"""
Generate the NewsML-G2 Structure Matrix — which attributes apply to which
elements, and which Item types each element can appear in.

This replaces `documentation/NewsML-G2_2.26-structMatrix_1.xls` and the copies
of it labelled 2.27 to 2.29. Those were maintained by hand and had drifted: the
2.27, 2.28 and 2.29 spreadsheets are identical cell for cell, differing only in
file metadata and, for 2.29, a renamed sheet. Only seven cells changed between
2.26 and 2.27. So the matrix was republished three times without its content
being revisited, and by 2.29 it was missing constructs the schema had gained.

Output is CSV so it diffs in review and can be regenerated for any version whose
schema is in the repository, rather than being edited cell by cell.

Not derivable from the schema, and therefore not reproduced here: the "value
type", "data type of list items" and codehint columns of the original
spreadsheet, which carry editorial and other-project metadata.
"""

from __future__ import annotations

import csv
import os

# The document roots the original matrix reported membership for.
ITEM_ROOTS = (
    'newsItem',
    'packageItem',
    'planningItem',
    'conceptItem',
    'knowledgeItem',
    'catalogItem',
    'newsMessage',
)

USE_CODES = {
    'required': 'r',
    'optional': 'o',
    'prohibited': '-',
}

# An element name declared in more than one context does not necessarily carry
# the same attributes in each. Rather than the spreadsheet's approach of
# splitting those into separate rows with invented names (`nar:channelXxNMSG`,
# `nar:channelXxREMCONT` — names that appear in no document), one row is kept
# per name and cells that do not hold everywhere are parenthesised.
#
#   r      required in every context the element is declared in
#   o      permitted in every context
#   -      prohibited
#   (r)    required, but only in some of its contexts
#   (o)    permitted, but only in some of its contexts
#   empty  not permitted in any context
#
# The `contexts` column gives the number of declarations, so a parenthesised
# cell can be read against it.
PARTIAL = '(%s)'


def _cell(present, declaration_count):
    """
    Render one element/attribute cell from the declarations that carry it.
    """
    if not present:
        return ''
    uses = {attr.use for attr in present}
    if uses == {'prohibited'}:
        code = USE_CODES['prohibited']
    elif uses == {'required'}:
        code = USE_CODES['required']
    else:
        code = USE_CODES['optional']
    if len(present) < declaration_count:
        return PARTIAL % code
    return code


def reachable_from(schema, root):
    """
    Every element name reachable from `root` in an instance document.

    Walks the flattened particle table, so group references and extension
    chains are already resolved. Iterative with a seen-set because the schema
    is recursive (`group` contains `groupSet` contains `group`).
    """
    if root not in schema.elements:
        return set()

    seen = set()
    pending = [root]
    while pending:
        name = pending.pop()
        if name in seen:
            continue
        seen.add(name)
        ref = schema.elements.get(name)
        if ref is None:
            continue
        for decl in ref.declarations:
            for particle in decl.children:
                if particle.child not in seen:
                    pending.append(particle.child)
    return seen


def build(schema):
    """
    Return (header, rows) for the matrix.
    """
    element_names = schema.element_names()
    attribute_names = schema.all_attribute_names()

    membership = {root: reachable_from(schema, root) for root in ITEM_ROOTS}

    header = (
        ['element', 'global', 'deprecated', 'contexts']
        + ['in:%s' % root for root in ITEM_ROOTS]
        + ['@%s' % name for name in attribute_names]
    )

    rows = []
    for name in element_names:
        ref = schema.elements[name]
        per_declaration = schema.attribute_closure_by_declaration(name)
        count = len(per_declaration)
        cells = {}
        for attribute in attribute_names:
            present = [
                found[attribute] for found in per_declaration
                if attribute in found
            ]
            cells[attribute] = _cell(present, count)
        rows.append(
            ['nar:%s' % name,
             'Y' if ref.is_global else 'N',
             'Y' if ref.is_deprecated else 'N',
             str(ref.context_count)]
            + ['Y' if name in membership[root] else 'N' for root in ITEM_ROOTS]
            + [cells[attribute] for attribute in attribute_names]
        )

    return header, rows


def write_csv(schema, path):
    header, rows = build(schema)
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)
    return len(rows), len(header)


def verify_csv(schema, path):
    """
    Check a committed matrix still matches the schema it was generated from.

    This is the gate that the hand-maintained spreadsheet never had. The `.xls`
    published as 2.29 was byte-identical to the 2.27 one and omitted ten
    attributes and five elements that the 2.29 schema had added — a change
    nobody noticed for six releases. Regenerating and comparing makes that
    failure impossible rather than merely unlikely.

    Returns a list of human-readable differences; empty means up to date.
    """
    if not os.path.isfile(path):
        return ['%s is missing — run with --matrix to create it' % path]

    header, rows = build(schema)
    expected = [header] + rows

    with open(path, encoding='utf-8', newline='') as handle:
        actual = list(csv.reader(handle))

    if actual == expected:
        return []

    differences = []
    if actual and actual[0] != header:
        missing = [column for column in header if column not in actual[0]]
        extra = [column for column in actual[0] if column not in header]
        if missing:
            differences.append('columns in the schema but not the CSV: %s'
                               % ', '.join(missing))
        if extra:
            differences.append('columns in the CSV but not the schema: %s'
                               % ', '.join(extra))

    expected_elements = {row[0] for row in rows}
    actual_elements = {row[0] for row in actual[1:]}
    if expected_elements - actual_elements:
        differences.append('elements missing from the CSV: %s'
                           % ', '.join(sorted(expected_elements - actual_elements)))
    if actual_elements - expected_elements:
        differences.append('elements in the CSV but not the schema: %s'
                           % ', '.join(sorted(actual_elements - expected_elements)))

    if not differences:
        differences.append('cell values differ; regenerate with --matrix')

    return differences


def summarise(schema):
    """Counts worth printing after a generation run."""
    header, rows = build(schema)
    attribute_columns = [column for column in header if column.startswith('@')]
    filled = sum(
        1 for row in rows for cell in row[4 + len(ITEM_ROOTS):] if cell
    )
    return {
        'version': schema.version,
        'elements': len(rows),
        'attributes': len(attribute_columns),
        'element_attribute_pairs': filled,
    }
