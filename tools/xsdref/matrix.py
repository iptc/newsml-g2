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


# Column fills carried over from the hand-built spreadsheet, which colour-coded
# the attribute columns by the group they arrive through.
GROUP_FILLS = (
    ('commonPowerAttributes', 'CCCCFF'),
    ('i18nAttributes', 'CC99FF'),
    ('flexAttributes', 'FFCC99'),
)

CATEGORY_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'assets', 'element-categories.csv')


def element_categories():
    """
    The editorial grouping of elements — "concept details", "text markup",
    "rights expressions" and so on — recovered from the 2.29 spreadsheet.

    This is the one part of that spreadsheet that is not derivable from the
    schema: someone decided what each element is *for*, and the only record of
    it was a background colour in a binary file. Retiring the spreadsheet
    without carrying this forward would have lost it.

    Elements added since 2.29 have no category until one is assigned here.
    """
    if not os.path.isfile(CATEGORY_FILE):
        return {}
    with open(CATEGORY_FILE, encoding='utf-8') as handle:
        return {row['element']: (row['category'], row['colour'].lstrip('#'),
                                 int(row['order']))
                for row in csv.DictReader(handle)}


# A parent element implies a category for the elements declared directly
# beneath it. Measured against the 201 categories recovered from the 2.29
# spreadsheet, this is right 79% of the time when it fires and declines to
# guess on 44% of elements — good enough to propose a category for something
# newly added, nowhere near good enough to overwrite an editorial decision
# somebody already made. It suggests; a human confirms.
PARENT_CATEGORY = {
    'itemMeta': 'item management',
    'contentMeta': 'content metadata',
    'partMeta': 'content metadata',
    'rightsInfo': 'rights expressions',
    'eventDetails': 'event details',
    'newsCoverage': 'news coverage',
    'planning': 'news coverage',
    'concept': 'concept details',
    'conceptSet': 'concept details',
    'contentSet': 'content structure',
    'header': 'news message',
    'catalogContainer': 'catalogItem content',
}


def suggest_category(schema, name):
    """
    Propose a category for an element from the elements that contain it.

    Deliberately conservative: only direct parents count. Following
    containment transitively reaches almost everything from almost
    everywhere — nine of the anchors above reach 33 elements in common — and
    accuracy collapses from 79% to 74% while the abstentions disappear, which
    is the worst combination: confident and wrong.
    """
    ref = schema.elements.get(name)
    if ref is None:
        return None
    votes = {}
    for particle in ref.parents:
        category = PARENT_CATEGORY.get(particle.parent)
        if category:
            votes[category] = votes.get(category, 0) + 1
    if not votes:
        return None
    return max(sorted(votes), key=votes.get)


def write_xlsx(schema, path):
    """
    Write the matrix as a styled workbook, in the shape the published
    spreadsheet used: a legend sheet, frozen panes, rotated attribute headings,
    and colour coding by attribute group and element category.

    The CSV remains the version-controlled form — it diffs in review, which a
    binary cannot. This is the form for reading.
    """
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Font, PatternFill
        from openpyxl.utils import get_column_letter
    except ImportError:
        raise SystemExit(
            'openpyxl is needed to write the .xlsx form of the matrix.\n'
            'Install it with `pip install openpyxl`, or use --matrix for CSV.')

    header, rows = build(schema)
    categories = element_categories()

    # The spreadsheet grouped elements by category rather than alphabetically,
    # which is what makes the colour bands contiguous and readable. That order
    # is editorial too, so it is carried in the categories file alongside the
    # colours. The CSV stays alphabetical: it is the form that gets diffed.
    rows.sort(key=lambda row: categories.get(
        row[0].split(':', 1)[-1], ('', '', 10**6))[2])
    attribute_start = header.index('@%s' % schema.all_attribute_names()[0])

    fills = {}
    for group, colour in GROUP_FILLS:
        for attr in schema._expand_attribute_group(group):
            fills.setdefault('@%s' % attr.name, colour)

    book = Workbook()
    legend = book.active
    legend.title = 'Legend'
    legend.column_dimensions['A'].width = 26
    legend.column_dimensions['B'].width = 96
    bold = Font(bold=True)

    def note(label, text='', fill=None):
        row = legend.max_row + 1 if legend.max_row > 1 or legend['A1'].value else 1
        legend.cell(row=row, column=1, value=label).font = bold
        cell = legend.cell(row=row, column=2, value=text)
        cell.alignment = Alignment(wrap_text=True, vertical='top')
        if fill:
            legend.cell(row=row, column=1).fill = PatternFill(
                'solid', start_color=fill, end_color=fill)

    note('NewsML-G2 %s' % schema.version, 'Structure Matrix. Generated from the '
         'XML Schema by tools/xsdref; do not edit by hand.')
    note('Rows 1-2', 'Group headings for the columns below them.')
    note('Row 3', 'Column headings. Attribute names are in alphabetical order.')
    note('Column A', 'QName of the element, shaded by the category it belongs to.')
    note('global', 'Y when the element is declared at the top level of the schema.')
    note('deprecated', 'Y when the schema documentation marks it deprecated.')
    note('contexts', 'How many times the name is declared. Where that is more '
                     'than one, a bracketed cell means the attribute applies in '
                     'some of those contexts but not all.')
    note('in:*', 'Y when the element is reachable from that document root.')
    note('', '')
    note('Attribute cells', 'r = required, o = optional, - = prohibited, '
                            '(r)/(o) = applies in some contexts only, blank = not permitted.')
    note('', '')
    note('Attribute columns', 'Shaded by the group the attribute arrives through:')
    for group, colour in GROUP_FILLS:
        note(group, '', colour)
    note('', '')
    note('Element categories', 'Carried over from the spreadsheet published up to 2.29:')
    for category, colour in sorted({(v[0], v[1]) for v in categories.values()}):
        note(category, '', colour)

    sheet = book.create_sheet('NewsML-G2 %s' % schema.version)

    # Widths, row height and banding follow the published spreadsheet, read off
    # the 2.29 file: column A 30.7 characters, every other column 3.33, heading
    # row 181pt with headings rotated upright. Fills band the whole column
    # rather than the heading alone — that is what makes an attribute group
    # legible across 200-odd rows.
    ITEM_BAND = 'CCFFCC'
    band = {}
    for index, title in enumerate(header, start=1):
        if title.startswith('in:'):
            band[index] = ITEM_BAND
        elif title.startswith('@') and title in fills:
            band[index] = fills[title]
    palette = set(band.values()) | {colour for _, colour, _ in categories.values()}
    pattern = {colour: PatternFill('solid', start_color=colour, end_color=colour)
               for colour in palette}

    sheet.cell(row=1, column=5, value='Items, News Message').font = bold
    sheet.cell(row=2, column=attribute_start + 1,
               value='Attributes, in alphabetical order').font = bold

    upright = Alignment(textRotation=90, vertical='bottom', horizontal='center')
    centred = Alignment(horizontal='center')

    for index, title in enumerate(header, start=1):
        cell = sheet.cell(row=3, column=index, value=title)
        cell.font = bold
        cell.alignment = Alignment(vertical='bottom') if index == 1 else upright
        if index in band:
            cell.fill = pattern[band[index]]

    for offset, row in enumerate(rows, start=4):
        category = categories.get(row[0].split(':', 1)[-1])
        # A deprecated element is shaded right across its row in the published
        # spreadsheet, overriding the column bands; every other category shades
        # the name cell only.
        row_fill = (pattern[category[1]]
                    if category and category[0] == 'deprecated' else None)
        for index, value in enumerate(row, start=1):
            # "contexts" is a count. Written as text it renders with Excel's
            # number-stored-as-text warning on every row.
            if header[index - 1] == 'contexts':
                value = int(value)
            cell = sheet.cell(row=offset, column=index, value=value)
            if index > 1:
                cell.alignment = centred
            if row_fill is not None and index <= attribute_start:
                cell.fill = row_fill
            elif index in band:
                cell.fill = pattern[band[index]]
        if category:
            sheet.cell(row=offset, column=1).fill = pattern[category[1]]

    sheet.freeze_panes = 'B4'
    sheet.column_dimensions['A'].width = 30.7
    for index in range(2, len(header) + 1):
        sheet.column_dimensions[get_column_letter(index)].width = 3.33
    sheet.row_dimensions[3].height = 181

    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    book.save(path)
    uncategorised = []
    for row in rows:
        name = row[0].split(':', 1)[-1]
        if name in categories:
            continue
        suggestion = suggest_category(schema, name)
        uncategorised.append(
            '%s (suggest: %s)' % (name, suggestion) if suggestion else name)
    return len(rows), uncategorised
