# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 International Press Telecommunications Council (IPTC)
# The MIT License — see LICENSE in the repository root.

"""
Read the hand-written annotations in Specification §14 and bind each one to the
schema construct it describes.

§14 is an annotation layer over the schema, not a duplicate of it — its own
preamble says "Elements not requiring such additional information are not listed
here". So these notes are the part that cannot be generated, and the generated
reference has to merge them in rather than replace them.

Binding is done once, here, rather than by regex at render time. Entry headings
are `Human Readable Name <separator> constructName`, but the separator is an
en-dash 77 times and an ASCII hyphen 18 times, five headings in §14.6 have no
parseable name at all, and the §14.7 headings are bare type names. A
build-time regex would fail on those forever; an explicit table is checked once
and then stays correct.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

# Which §14 subsection an entry sits in determines what kind of construct it
# describes. Sections not listed here hold prose, not per-construct notes.
SECTION_KINDS = {
    'Element specifications': 'element',
    'Datatype specifications': 'type',
    'Attribute (Group) Specifications': 'attributeGroup',
}

# Headings that cannot be parsed into a name by rule, mapped by hand.
# Two `address` notes exist because the element is declared in more than one
# context and the guidance differs between them.
HEADING_OVERRIDES = {
    'Event Confirmation': [('confirmation', 'element', None)],
    'Postal Address': [('address', 'element', 'contact')],
    'Postal Address of a Point of Interest – address (in POI structure)':
        [('address', 'element', 'POI')],
    'Recurrence Group': [('RecurrenceGroup', 'group', None)],
    'Registration registration': [('registration', 'element', None)],
    'DateOptTimePropType and DateOptTimeType':
        [('DateOptTimePropType', 'type', None), ('DateOptTimeType', 'type', None)],
    'TruncatedDateTimePropType and TruncatedDateTimeType':
        [('TruncatedDateTimePropType', 'type', None),
         ('TruncatedDateTimeType', 'type', None)],
    # The note covers the whole Flex*PropType family; FlexPropType is its root.
    'FlexPropType (multiple)': [('FlexPropType', 'type', None)],
    # Declared as an xs:attribute, not an attributeGroup, despite sitting in
    # the "Attribute (Group)" section.
    'Orientation Attribute - orientation': [('orientation', 'attribute', None)],
}

HEADING_RE = re.compile(r'^(?P<label>.*?)\s*[–—-]\s*(?P<name>\S+)\s*$')

INCLUDE_RE = re.compile(r'^include::(?P<target>[^\[]+)\[(?P<attrs>[^\]]*)\]\s*$', re.M)


def _inline_includes(body, chapter_path, depth=0):
    """
    Replace `include::` directives in a note body with the file's content.

    Note bodies pull in shared table fragments, e.g. the `remoteContent` note
    ends with `include::{includedir}/../../tables/dimension-unit-defaults.adoc[]`.
    Those paths are relative to the specification repository, which is not where
    the generated reference is written, so they are resolved here and the
    reference comes out self-contained.

    The paths in the chapters are convoluted (`{includedir}/../../tables/…`
    happens to resolve back to `_includes/tables/…`), so resolution is by
    filename under the specification repository rather than by path arithmetic.
    """
    if depth > 3 or 'include::' not in body:
        return body

    spec_root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(chapter_path))))

    def resolve(match):
        target = match.group('target').strip()
        wanted = os.path.basename(target)
        for base, _dirs, files in os.walk(os.path.join(spec_root, '_includes')):
            if wanted in files:
                with open(os.path.join(base, wanted), encoding='utf-8') as included:
                    return _inline_includes(
                        included.read().strip(), chapter_path, depth + 1
                    )
        # Leave a visible marker rather than a broken directive, so a missing
        # fragment shows up in review instead of failing the site build.
        return '// unresolved include: %s' % target

    return INCLUDE_RE.sub(resolve, body)


@dataclass
class Note:
    """One §14 annotation, bound to the construct(s) it describes."""

    heading: str
    label: str
    target: str
    kind: str
    body: str
    line: int
    section: str
    # Set when the note applies to one declaration context of a name that is
    # declared more than once.
    context: str = None

    @property
    def slug(self):
        base = self.target
        if self.context:
            base = '%s-%s' % (self.target, self.context)
        return base


@dataclass
class Problem:
    """A §14 note that does not bind to anything in the schema."""

    note: Note
    reason: str
    suggestion: str = None
    note_path: str = None

    def __str__(self):
        text = '%s:%d  §14 documents %s "%s" — %s' % (
            os.path.basename(self.note_path or '§14'), self.note.line,
            self.note.kind, self.note.target, self.reason,
        )
        if self.suggestion:
            text += ' (did you mean "%s"?)' % self.suggestion
        return text


def _setext_headings(lines, rule_char):
    """Yield (line_number, title) for underline-style headings."""
    found = []
    for index in range(len(lines) - 1):
        title = lines[index].strip()
        underline = lines[index + 1]
        if title and underline and set(underline) == {rule_char}:
            found.append((index, title))
    return found


def parse(path):
    """
    Parse §14 into Notes. Returns (notes, unbound_headings).

    `unbound_headings` are entries in a note-bearing section whose heading could
    neither be parsed nor found in HEADING_OVERRIDES — a signal that the
    override table needs updating, not something to guess at.
    """
    with open(path, encoding='utf-8') as source:
        lines = source.read().split('\n')

    sections = _setext_headings(lines, '~')
    entries = _setext_headings(lines, '^')

    def section_for(line_number):
        current = None
        for section_line, title in sections:
            if section_line < line_number:
                current = title
            else:
                break
        return current

    notes = []
    unbound = []

    for position, (line_number, heading) in enumerate(entries):
        section = section_for(line_number)
        if section not in SECTION_KINDS:
            continue

        end = entries[position + 1][0] - 1 if position + 1 < len(entries) else len(lines)
        body = '\n'.join(lines[line_number + 2:end]).strip()
        # Drop trailing anchors belonging to the next entry.
        body = re.sub(r'\n*\[\[[^\]]+\]\]\s*$', '', body).strip()
        body = _inline_includes(body, path)

        targets = HEADING_OVERRIDES.get(heading)
        if targets is None:
            match = HEADING_RE.match(heading)
            if match:
                targets = [(match.group('name'), SECTION_KINDS[section], None)]
                label = match.group('label')
            elif section == 'Datatype specifications':
                # §14.7 headings are bare type names.
                targets = [(heading, 'type', None)]
                label = heading
            else:
                unbound.append((line_number, heading, section))
                continue
        else:
            label = HEADING_RE.match(heading).group('label') if HEADING_RE.match(heading) else heading

        for name, kind, context in targets:
            notes.append(Note(
                heading=heading,
                label=label.strip() or name,
                target=name,
                kind=kind,
                body=body,
                line=line_number + 1,
                section=section,
                context=context,
            ))

    return notes, unbound


def _exists(schema, name, kind):
    if kind == 'element':
        return name in schema.elements
    if kind == 'type':
        return name in schema.complex_types or name in schema.simple_types
    if kind == 'group':
        return name in schema.groups
    if kind == 'attributeGroup':
        return name in schema.attribute_groups
    if kind == 'attribute':
        return name in schema.all_attribute_names()
    return False


def _find_any_kind(schema, name):
    for kind in ('element', 'type', 'group', 'attributeGroup', 'attribute'):
        if _exists(schema, name, kind):
            return kind
    return None


def _closest(schema, name, kind):
    """
    Suggest a construct whose name differs only by case or by a short edit —
    which is what the known §14 defects look like.
    """
    import difflib

    pools = {
        'element': schema.elements.keys(),
        'type': list(schema.complex_types) + list(schema.simple_types),
        'group': schema.groups.keys(),
        'attributeGroup': schema.attribute_groups.keys(),
        'attribute': schema.all_attribute_names(),
    }
    candidates = list(pools.get(kind) or [])
    # Case-only differences first: they are the commonest defect and an exact
    # case-insensitive hit is far more trustworthy than a fuzzy one.
    for candidate in candidates:
        if candidate.lower() == name.lower():
            return candidate
    # Then across every kind, still case-insensitively.
    for pool in pools.values():
        for candidate in pool:
            if candidate.lower() == name.lower():
                return candidate
    everything = [item for pool in pools.values() for item in pool]

    # A shared stem catches the other shape these defects take: a documented
    # name that has drifted by a suffix rather than by case — "hashvalue" for
    # `hash`, "RecurrenceRuleType" for `recurrenceRuleAttributes`. Edit-distance
    # scores both of those below any cutoff that is safe to use.
    lowered = name.lower()
    best = None
    best_shared = 0
    for candidate in everything:
        shared = len(os.path.commonprefix([lowered, candidate.lower()]))
        if shared >= 4 and shared > best_shared:
            best, best_shared = candidate, shared
    if best is not None:
        return best

    matches = difflib.get_close_matches(name, candidates, n=1, cutoff=0.75)
    if matches:
        return matches[0]
    matches = difflib.get_close_matches(name, everything, n=1, cutoff=0.8)
    return matches[0] if matches else None


def check(schema, notes, source_path=None):
    """
    Report every §14 note that does not bind to the schema.

    Nothing checks this today, and nothing could: the specification prose and
    the schema live in separate repositories with no shared tooling.
    """
    problems = []
    for note in notes:
        if _exists(schema, note.target, note.kind):
            continue

        actual_kind = _find_any_kind(schema, note.target)
        if actual_kind:
            problem = Problem(
                note=note,
                reason='it exists as %s, not %s' % (actual_kind, note.kind),
            )
        else:
            problem = Problem(
                note=note,
                reason='no such %s in schema %s' % (note.kind, schema.version),
                suggestion=_closest(schema, note.target, note.kind),
            )
        problem.note_path = source_path
        problems.append(problem)

    return problems


def write_partials(notes, output_dir):
    """
    Write one AsciiDoc partial per note, carrying an explicit binding key.

    The key is committed rather than inferred from the filename so that renaming
    a file cannot silently detach a note from its construct.
    """
    os.makedirs(output_dir, exist_ok=True)
    written = []
    for note in notes:
        path = os.path.join(output_dir, '%s.adoc' % note.slug)
        with open(path, 'w', encoding='utf-8') as partial:
            partial.write('// Generated from Specification §14 (%s), line %d.\n'
                          '// Edit this file, not the chapter.\n'
                          ':note-applies-to: %s\n'
                          ':note-kind: %s\n'
                          % (note.section, note.line, note.target, note.kind))
            if note.context:
                partial.write(':note-context: %s\n' % note.context)
            partial.write('\n%s\n' % note.body)
        written.append(path)
    return written
