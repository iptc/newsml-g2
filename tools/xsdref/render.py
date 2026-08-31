# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 International Press Telecommunications Council (IPTC)
# The MIT License — see LICENSE in the repository root.

"""
Emit one AsciiDoc reference page per element name.

Two deliberate choices, both aimed at the failure mode of the current
XMLSpy-generated documentation (the NewsItem page alone is 12.4 MB):

* Inherited attributeGroups are referenced, never expanded inline. Expanding
  the closure would make roughly 240 pages 90% identical boilerplate and would
  bloat the site search index.

* The content model is rendered as an indented text tree rather than a diagram.
  It answers the actual question ("what can go inside `<contentMeta>`?"), it is
  searchable and diffable in review, it is accessible, and it needs no
  rendering dependency. No Kroki backend reproduces XMLSpy's box notation, and
  a bespoke renderer for it would not be maintained.
"""

from __future__ import annotations

import os

from .schema import XS, documentation as schema_documentation

XS_ELEMENT = XS + 'element'

def _group_label(path):
    """
    The named model group a run of children arrived through, if any.

    G2 readers know these by name — ItemManagementGroup,
    DescriptiveMetadataCoreGroup — so naming the group is more useful than
    describing the nesting that produced it.
    """
    for step in reversed(path):
        if step.startswith('group:'):
            return step.split(':', 1)[1]
    return None


def _runs(children):
    """
    Split a declaration's children into consecutive runs sharing a compositor
    path. Each run is one `xs:sequence` or `xs:choice` as an author wrote it.

    This is the unit a reader needs. A choice is a relationship between
    siblings, so marking members individually says nothing about which
    alternatives are being chosen between — and `contentMeta` alone has two
    separate choices that a per-element marker renders identically.
    """
    runs = []
    for particle in children:
        if runs and runs[-1][0] == particle.path:
            runs[-1][1].append(particle)
        else:
            runs.append((particle.path, [particle]))
    return runs


def _element_link(name):
    return 'xref:%s.adoc[`<%s>`]' % (name, name)


def content_tree(schema, declaration, depth=2):
    """
    Indented tree of the children of one declaration.

    `depth` is capped because the schema is recursive — `group` contains
    `groupSet` contains `group` — and because a reader wants this element's
    shape, not the whole document.
    """
    lines = []

    def walk(particles, indent, seen):
        for particle in particles:
            marker = occurrence_marker(particle)
            lines.append('%s%s%s  %s%s' % (
                '  ' * indent,
                '<' + particle.child + '>',
                marker,
                particle.occurs,
                '' if particle.compositor == 'sequence' else ', %s' % particle.compositor,
            ))
            if indent + 1 >= depth or particle.child in seen:
                continue
            child = schema.elements.get(particle.child)
            if child is None or not child.declarations:
                continue
            walk(child.declarations[0].children, indent + 1, seen | {particle.child})

    walk(declaration.children, 0, {declaration.name})
    return lines


def _escape(text):
    """Keep AsciiDoc from interpreting cell content in a table."""
    if text is None:
        return ''
    return text.replace('|', '\\|')


def element_page(schema, name, notes_by_target):
    """Render the reference page for one element name."""
    ref = schema.elements[name]
    out = []

    out.append('= <%s>' % name)
    out.append(':xsd-version: %s' % schema.version)
    out.append('')

    if ref.has_varying_doc:
        # Declarations of this name are documented differently in the schema, so
        # there is no single definition to show.
        out.append('The schema defines this element differently in each context '
                   'it is declared in.')
        out.append('')
        for declaration in ref.declarations:
            out.append('%s:: %s' % (
                'In `<%s>`' % declaration.scope if declaration.scope else 'As a document root',
                declaration.doc or '(no documentation in the schema)',
            ))
        out.append('')
    elif ref.doc:
        out.append(ref.doc)
        out.append('')
    else:
        out.append('[NOTE]')
        out.append('====')
        out.append('This element carries no `xs:documentation` in the schema.')
        out.append('====')
        out.append('')

    if not ref.is_global:
        out.append('Declared locally only; it is not a valid document root.')
        out.append('')

    out.extend(_notes_block(notes_by_target, 'element', name))

    if ref.context_count > 1:
        out.append('== Declared in %d contexts' % ref.context_count)
        out.append('')
        if ref.has_varying_content:
            out.append('The content model differs between these contexts.')
        else:
            out.append('The content model is the same in each context.')
        out.append('')
        for particle in ref.parents:
            out.append('* inside xref:%s.adoc[<%s>] — %s' % (
                particle.parent, particle.parent, particle.occurs))
        out.append('')

    # An attribute name may reach a page through several groups; only the
    # first occurrence carries the anchor, so ids stay unique per page.
    seen_anchors = set()

    for index, declaration in enumerate(ref.declarations):
        suffix = ''
        if ref.context_count > 1:
            suffix = ' (%s)' % (declaration.scope or 'global')

        if declaration.children:
            out.append('== Content model%s' % suffix)
            out.append('')
            out.extend(content_model(declaration))
        elif index == 0:
            out.append('== Content model%s' % suffix)
            out.append('')
            out.append('No child elements.')
            out.append('')

        out.extend(attribute_table(schema, declaration, suffix, seen_anchors))

        if declaration.has_extension_point:
            out.append('This element is an extension point: properties from '
                       'other XML namespaces may be added.')
            out.append('')

    if ref.parents and ref.context_count == 1:
        out.append('== Used by')
        out.append('')
        for particle in ref.parents:
            out.append('* xref:%s.adoc[<%s>] — %s%s' % (
                particle.parent, particle.parent, particle.occurs,
                '' if particle.compositor == 'sequence' else ', in any order (%s)' % particle.compositor,
            ))
        out.append('')
    elif not ref.parents:
        out.append('== Used by')
        out.append('')
        out.append('Nothing — this is a document root.')
        out.append('')

    return '\n'.join(out).rstrip() + '\n'


def attribute_group_page(schema, name, notes_by_target=None):
    """Render the page an element's `Also carries` list points at."""
    attributes = schema._expand_attribute_group(name)
    out = ['= %s' % name, ':xsd-version: %s' % schema.version, '']
    out.append('An attribute group. Elements listing it carry every attribute below.')
    out.append('')
    out.extend(_notes_block(notes_by_target, 'attributeGroup', name))
    # An attribute documented in §14.8 that is not itself a group — orientation
    # is the only one — belongs on the page of the group that carries it.
    for attribute in attributes:
        out.extend(_notes_block(notes_by_target, 'attribute', attribute.name))
    out.append('[cols="1,1,1,3",options="header"]')
    out.append('|===')
    out.append('| Attribute | Type | Use | Description')
    for attr in attributes:
        out.append('| `%s` | %s | %s a| %s' % (
            attr.name,
            '`%s`' % attr.type_ref if attr.type_ref else '',
            attr.use,
            _escape(attr.doc),
        ))
    out.append('|===')
    out.append('')

    users = sorted(
        name_
        for name_, ref in schema.elements.items()
        if any(name in decl.attribute_groups for decl in ref.declarations)
    )
    if users:
        out.append('== Carried by')
        out.append('')
        out.append(', '.join('xref:%s.adoc[<%s>]' % (u, u) for u in users))
        out.append('')
    return '\n'.join(out).rstrip() + '\n'


def write_pages(schema, notes, output_dir):
    """Write every reference page. Returns the list of paths written."""
    os.makedirs(output_dir, exist_ok=True)

    # Keyed by (kind, target). Previously only element notes were collected,
    # which left the §14.7 datatype notes and the §14.8 attribute-group notes
    # with nowhere to appear — 17 of the 112 notes rendered on no page at all.
    notes_by_target = {}
    for note in notes:
        notes_by_target.setdefault((note.kind, note.target), []).append(note)

    # A note on a model group has no page of its own to live on: named groups
    # are inlined before parentage is computed precisely because they name
    # nothing in an instance document. Attach it to each element the group
    # contributes, which is who the guidance is actually about — the
    # RecurrenceGroup note describes rDate, rRule, exDate and exRule.
    for (kind, target), group_notes in list(notes_by_target.items()):
        if kind != 'group' or target not in schema.groups:
            continue
        members = {node.get('ref') or node.get('name')
                   for node in schema.groups[target].iter(XS_ELEMENT)}
        for member in sorted(m for m in members if m in schema.elements):
            notes_by_target.setdefault(('element', member), []).extend(group_notes)

    written = []
    for name in schema.element_names():
        path = os.path.join(output_dir, '%s.adoc' % name)
        with open(path, 'w', encoding='utf-8') as page:
            page.write(element_page(schema, name, notes_by_target))
        written.append(path)

    for group in sorted(schema.attribute_groups):
        path = os.path.join(output_dir, 'attgroup-%s.adoc' % group)
        with open(path, 'w', encoding='utf-8') as page:
            page.write(attribute_group_page(schema, group, notes_by_target))
        written.append(path)

    for name in schema.type_names():
        path = os.path.join(output_dir, 'type-%s.adoc' % name)
        with open(path, 'w', encoding='utf-8') as page:
            page.write(datatype_page(schema, name, notes_by_target))
        written.append(path)

    return written


def write_nav(schema, path):
    """
    Generate the navigation file rather than hand-authoring it, so it cannot
    drift from the pages that exist.
    """
    out = ['* Element reference', '']
    for name in schema.element_names():
        out.append('** xref:%s.adoc[<%s>]' % (name, name))
    out.append('')
    out.append('* Attribute groups')
    out.append('')
    for group in sorted(schema.attribute_groups):
        out.append('** xref:attgroup-%s.adoc[%s]' % (group, group))
    out.append('')
    out.append('* Datatypes')
    out.append('')
    for name in schema.type_names():
        out.append('** xref:type-%s.adoc[%s]' % (name, name))
    with open(path, 'w', encoding='utf-8') as nav:
        nav.write('\n'.join(out) + '\n')


def content_model(declaration):
    """
    Render one declaration's content model as grouped, linked AsciiDoc.

    Emitted as prose and lists rather than a preformatted block, so every
    element name links to its own page. The previous rendering was a
    `[source,text]` block, which made linking impossible and forced a legend
    for sigils that only repeated the occurrence range beside them.
    """
    out = []
    runs = _runs(declaration.children)

    for path, particles in runs:
        label = _group_label(path)
        is_choice = path and path[-1] == 'choice'

        if is_choice:
            occurs = {particle.occurs for particle in particles}
            if len(occurs) == 1:
                shape = 'Any of these, in any order, each %s' % occurs.pop()
            else:
                shape = 'Any of these, in any order'
        else:
            shape = 'These, in this order'

        if label:
            heading = '%s — from `%s`' % (shape, label)
        else:
            heading = shape

        out.append('*%s:*' % heading)
        out.append('')

        if is_choice and len({p.occurs for p in particles}) == 1:
            # Cardinality is stated once in the heading, so the members read as
            # a list of alternatives rather than a column of identical ranges.
            out.append(' +\n'.join(
                _element_link(particle.child) for particle in particles
            ))
        else:
            for particle in particles:
                out.append('* %s — %s' % (
                    _element_link(particle.child), particle.occurs))
        out.append('')

    if declaration.has_extension_point:
        out.append('Also accepts elements from other namespaces '
                   '(extension point).')
        out.append('')

    return out


def attribute_table(schema, declaration, suffix='', seen_anchors=None):
    """
    One table of every attribute that can appear on this declaration, grouped by
    where each arrives from.

    Attributes used to be split between a table of locally declared ones and a
    list of links to attributeGroup pages. That was defensible on size grounds
    but wrong for the reader: finding out what `<remoteContent>` accepts meant
    visiting four more pages and reassembling the answer by hand.

    Expanding them is affordable. Fully expanded, the median page carries 17
    attribute rows and the largest — `related` — carries 81. The 12 MB XMLSpy
    pages were caused by inline diagrams and a whole-schema single document, not
    by attribute expansion.

    Provenance is kept, as a spanning heading row before each group's rows, so a
    reader can still tell an element's own attributes from inherited ones and
    follow the group link when they want its own page.
    """
    if seen_anchors is None:
        seen_anchors = set()

    local = [attr for attr in declaration.attributes if attr.is_local]
    inherited = [attr for attr in declaration.attributes if attr.via_base]
    groups = list(declaration.attribute_groups)

    if not (local or inherited or groups):
        return []

    out = ['=== Attributes%s' % suffix, '']
    out.append('[cols="1,1,1,3",options="header"]')
    out.append('|===')
    out.append('| Attribute | Type | Use | Description')

    def rows(attributes):
        for attr in attributes:
            if attr.name in seen_anchors:
                anchor = ''
            else:
                seen_anchors.add(attr.name)
                anchor = '[[attr-%s]]' % attr.name.replace(':', '-')
            out.append('| %s`%s` | %s | %s a| %s' % (
                anchor,
                attr.name,
                '`%s`' % attr.type_ref if attr.type_ref else '',
                attr.use,
                _escape(attr.doc),
            ))

    if local:
        out.append('4+s| Declared on this element')
        rows(local)

    if inherited and declaration.base_type:
        out.append('4+s| Inherited from `%s`' % declaration.base_type)
        rows(inherited)

    for group in groups:
        expanded = schema._expand_attribute_group(group)
        if not expanded:
            continue
        out.append('4+s| From xref:attgroup-%s.adoc[%s]' % (group, group))
        rows(expanded)

    out.append('|===')
    out.append('')
    return out


def _notes_block(notes_by_target, kind, target):
    """
    Hand-written guidance from Specification §14, beside the generated
    material. This is the part of the reference that cannot be derived, so it
    is the part worth being careful not to lose.
    """
    if not notes_by_target:
        return []
    out = []
    for note in notes_by_target.get((kind, target), []):
        heading = 'Usage note'
        if note.context:
            heading = 'Usage note (%s)' % note.context
        out.extend(['[NOTE]', '.%s' % heading, '====', note.body, '====', ''])
    return out


def datatype_page(schema, name, notes_by_target=None):
    """
    Render the page for one named type.

    Types had no page at all, which left the eleven §14.7 datatype notes with
    nowhere to live and meant a reader meeting `QCodeType` or `FlexPropType` in
    an attribute table could not look it up.
    """
    node = schema.type_node(name)
    is_complex = name in schema.complex_types
    out = ['= %s' % name, ':xsd-version: %s' % schema.version, '']
    out.append('A %s.' % ('complex type' if is_complex else 'simple type'))
    out.append('')

    doc = schema_documentation(node)
    if doc:
        out.extend([doc, ''])

    out.extend(_notes_block(notes_by_target, 'type', name))

    facets = schema.type_facets(name)
    if facets:
        if facets['base']:
            out.extend(['Derived from `%s`.' % facets['base'], ''])
        if facets['pattern']:
            out.extend(['Values must match the pattern:', '',
                        '[source,text]', '----', facets['pattern'], '----', ''])
        if facets['enumerations']:
            out.extend(['== Permitted values', ''])
            out.extend('* `%s`' % value for value in facets['enumerations'])
            out.append('')

    elements, attributes, types = schema.type_users(name)
    if elements or attributes or types:
        out.extend(['== Used by', ''])
        if elements:
            out.append('Elements:: %s' % ', '.join(
                'xref:%s.adoc[<%s>]' % (e, e) for e in elements))
        if attributes:
            # Attributes are where several types are used exclusively —
            # QCodeType types 48 attributes and no element at all.
            shown = attributes[:24]
            more = ' and %d more' % (len(attributes) - len(shown)) if len(attributes) > len(shown) else ''
            out.append('Attributes:: %s%s' % (
                ', '.join('`@%s`' % a for a in shown), more))
        if types:
            out.append('Types:: %s' % ', '.join(
                'xref:type-%s.adoc[%s]' % (t, t) for t in types))
        out.append('')

    return '\n'.join(out).rstrip() + '\n'
