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

MARKERS = {
    # (optional, repeatable) -> AsciiDoc-safe marker
    (False, False): '',
    (True, False): '?',
    (False, True): '+',
    (True, True): '*',
}


def occurrence_marker(particle):
    return MARKERS[(particle.is_optional, particle.is_repeatable)]


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

    # Hand-written guidance from Specification §14 — the part that cannot be
    # generated, merged in beside the generated material.
    for note in notes_by_target.get(name, []):
        heading = 'Usage note'
        if note.context:
            heading = 'Usage note (%s)' % note.context
        out.append('[NOTE]')
        out.append('.%s' % heading)
        out.append('====')
        out.append(note.body)
        out.append('====')
        out.append('')

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

    for index, declaration in enumerate(ref.declarations):
        suffix = ''
        if ref.context_count > 1:
            suffix = ' (%s)' % (declaration.scope or 'global')

        if declaration.children:
            out.append('== Content model%s' % suffix)
            out.append('')
            out.append('[source,text]')
            out.append('----')
            out.extend(content_tree(schema, declaration))
            out.append('----')
            out.append('')
            out.append('`?` optional, `+` one or more, `*` zero or more.')
            out.append('')
        elif index == 0:
            out.append('== Content model%s' % suffix)
            out.append('')
            out.append('No child elements.')
            out.append('')

        local = [attr for attr in declaration.attributes if attr.is_local]
        inherited = [attr for attr in declaration.attributes if attr.via_base]

        if local:
            out.append('=== Attributes declared on this element%s' % suffix)
            out.append('')
            out.append('[cols="1,1,1,3",options="header"]')
            out.append('|===')
            out.append('| Attribute | Type | Use | Description')
            for attr in local:
                out.append('| `%s` | %s | %s a| %s' % (
                    attr.name,
                    '`%s`' % attr.type_ref if attr.type_ref else '',
                    attr.use,
                    _escape(attr.doc),
                ))
            out.append('|===')
            out.append('')

        if declaration.base_type or declaration.attribute_groups or inherited:
            out.append('=== Also carries%s' % suffix)
            out.append('')
            if declaration.base_type:
                out.append('* extends `%s`%s' % (
                    declaration.base_type,
                    ' (%s)' % ', '.join('`%s`' % a.name for a in inherited) if inherited else '',
                ))
            for group in declaration.attribute_groups:
                out.append('* xref:attgroup-%s.adoc[`%s`]' % (group, group))
            out.append('')

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


def attribute_group_page(schema, name):
    """Render the page an element's `Also carries` list points at."""
    attributes = schema._expand_attribute_group(name)
    out = ['= %s' % name, ':xsd-version: %s' % schema.version, '']
    out.append('An attribute group. Elements listing it carry every attribute below.')
    out.append('')
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

    notes_by_target = {}
    for note in notes:
        if note.kind == 'element':
            notes_by_target.setdefault(note.target, []).append(note)

    written = []
    for name in schema.element_names():
        path = os.path.join(output_dir, '%s.adoc' % name)
        with open(path, 'w', encoding='utf-8') as page:
            page.write(element_page(schema, name, notes_by_target))
        written.append(path)

    for group in sorted(schema.attribute_groups):
        path = os.path.join(output_dir, 'attgroup-%s.adoc' % group)
        with open(path, 'w', encoding='utf-8') as page:
            page.write(attribute_group_page(schema, group))
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
    with open(path, 'w', encoding='utf-8') as nav:
        nav.write('\n'.join(out) + '\n')
