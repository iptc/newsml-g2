# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 International Press Telecommunications Council (IPTC)
# The MIT License — see LICENSE in the repository root.

"""
Read a NewsML-G2 "All-Power" XML Schema into the reference model.

Three things here are easy to get wrong and are the reason this exists rather
than a few XPath expressions:

1. Named groups are inlined transitively before parent/child edges are built.
   `itemMeta` contains `<xs:group ref="ItemManagementGroup"/>`, which contains
   `<xs:element ref="itemClass"/>`. Without inlining, `itemClass`'s parent is
   reported as `ItemManagementGroup` — a name that appears in no instance
   document.

2. Effective cardinality is computed by climbing the compositor ancestry, not
   read off the declaration. Most local particles carry no minOccurs/maxOccurs
   and so default to 1..1, but sit inside
   `<xs:choice minOccurs="0" maxOccurs="unbounded">` — the standard G2 "any of
   these, in any order, any number" pattern. Reporting 1..1 would be wrong in a
   normative reference.

3. Attributes reach elements mostly through attributeGroups and xs:extension.
   The closure is resolved, but attributes declared on the element's own type
   are kept distinct from inherited ones so the renderer can reference the
   groups instead of repeating them on every page.
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass, replace

from lxml import etree

from .model import Attribute, Declaration, ElementRef, Particle

XS = '{http://www.w3.org/2001/XMLSchema}'

COMPOSITORS = ('sequence', 'choice', 'all')


def localname(tag):
    if isinstance(tag, str) and tag.startswith('{'):
        return tag.split('}', 1)[1]
    return tag


def strip_prefix(qname):
    """Drop any namespace prefix. The schema is single-namespace throughout."""
    if qname is None:
        return None
    return qname.split(':', 1)[-1]


def occurs(node):
    lo = int(node.get('minOccurs', '1'))
    raw_hi = node.get('maxOccurs', '1')
    hi = math.inf if raw_hi == 'unbounded' else int(raw_hi)
    return lo, hi


def _mul(a, b):
    """Multiply cardinality bounds, keeping 0 dominant over infinity."""
    if a == 0 or b == 0:
        return 0
    if a == math.inf or b == math.inf:
        return math.inf
    return a * b


def documentation(node):
    if node is None:
        return None
    ann = node.find(XS + 'annotation')
    if ann is None:
        return None
    texts = [
        ' '.join(doc.itertext()).strip()
        for doc in ann.findall(XS + 'documentation')
    ]
    texts = [text for text in texts if text]
    if not texts:
        return None
    return ' '.join(' '.join(texts).split())


@dataclass(frozen=True)
class _Ctx:
    """Accumulated cardinality and compositor context during a content walk."""

    lo: int = 1
    hi: object = 1
    compositor: str = 'sequence'
    in_choice: bool = False
    path: tuple = ()


class Schema:
    """An indexed NewsML-G2 Power schema."""

    def __init__(self, path):
        self.path = path
        self.tree = etree.parse(path)
        self.root = self.tree.getroot()
        self.version = self.root.get('version')

        self.global_elements = {}
        self.complex_types = {}
        self.simple_types = {}
        self.groups = {}
        self.attribute_groups = {}
        self.global_attributes = {}

        for node in self.root:
            name = node.get('name')
            if name is None:
                continue
            tag = localname(node.tag)
            if tag == 'element':
                self.global_elements[name] = node
            elif tag == 'complexType':
                self.complex_types[name] = node
            elif tag == 'simpleType':
                self.simple_types[name] = node
            elif tag == 'group':
                self.groups[name] = node
            elif tag == 'attributeGroup':
                self.attribute_groups[name] = node
            elif tag == 'attribute':
                self.global_attributes[name] = node

        self._elements = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def elements(self):
        """dict of element name -> ElementRef, built once and cached."""
        if self._elements is None:
            self._elements = self._build_elements()
        return self._elements

    def element_names(self):
        return sorted(self.elements)

    def all_attribute_names(self):
        """
        Every attribute name declared anywhere in the schema. Most attributes
        are declared inside attributeGroups or complexTypes rather than
        globally, so a global-only lookup would miss almost all of them.
        """
        return sorted({
            node.get('name')
            for node in self.root.iter(XS + 'attribute')
            if node.get('name')
        })

    def attribute_closure(self, name):
        """
        Every attribute that can appear on `name`, across all its declarations,
        with attributeGroup references expanded. This is what the Structure
        Matrix is built from.
        """
        found = {}
        for decl in self.elements[name].declarations:
            for attr in decl.attributes:
                found.setdefault(attr.name, attr)
            for group in decl.attribute_groups:
                for attr in self._expand_attribute_group(group):
                    found.setdefault(attr.name, attr)
        return [found[key] for key in sorted(found)]

    # ------------------------------------------------------------------
    # Building
    # ------------------------------------------------------------------

    def _build_elements(self):
        elements = {}

        for node in self.root.iter(XS + 'element'):
            name = node.get('name')
            if name is None:
                continue
            decl = self._resolve_element(node, name)
            elements.setdefault(name, ElementRef(name=name)).declarations.append(decl)

        # Parent edges are derived from the resolved content models, so a group
        # name can never appear as a parent.
        for ref in elements.values():
            for decl in ref.declarations:
                for particle in decl.children:
                    child = elements.get(particle.child)
                    if child is not None:
                        child.parents.append(particle)

        for ref in elements.values():
            ref.parents = _dedupe_particles(ref.parents)

        return elements

    def _resolve_element(self, node, name):
        decl = Declaration(
            name=name,
            scope=self._lexical_scope(node),
            doc=documentation(node),
            type_ref=strip_prefix(node.get('type')),
        )

        type_node = self._type_node_for(node)
        if type_node is not None and localname(type_node.tag) == 'complexType':
            self._resolve_complex_type(type_node, decl, name)

        return decl

    def _lexical_scope(self, node):
        """
        Human-readable description of where a declaration sits. Used only for
        display — parentage comes from the particle table.
        """
        parent = node.getparent()
        while parent is not None:
            tag = localname(parent.tag)
            if tag == 'schema':
                return None
            if tag == 'element' and parent.get('name'):
                return parent.get('name')
            if tag == 'group' and parent.get('name'):
                return 'group:' + parent.get('name')
            if tag == 'complexType' and parent.get('name'):
                return 'type:' + parent.get('name')
            parent = parent.getparent()
        return None

    def _type_node_for(self, element_node):
        inline = element_node.find(XS + 'complexType')
        if inline is not None:
            return inline
        type_ref = strip_prefix(element_node.get('type'))
        if type_ref and type_ref in self.complex_types:
            return self.complex_types[type_ref]
        return None

    def _resolve_complex_type(self, ct_node, decl, parent_name, seen_types=frozenset()):
        complex_content = ct_node.find(XS + 'complexContent')
        simple_content = ct_node.find(XS + 'simpleContent')

        if complex_content is not None:
            derivation = complex_content.find(XS + 'extension')
            inherits = derivation is not None
            if derivation is None:
                derivation = complex_content.find(XS + 'restriction')
            if derivation is None:
                return
            base = strip_prefix(derivation.get('base'))
            if decl.base_type is None:
                decl.base_type = base
            # An extension adds to the base's content model; a restriction
            # respecifies it, so only extensions inherit particles.
            if inherits and base in self.complex_types and base not in seen_types:
                self._resolve_complex_type(
                    self.complex_types[base], decl, parent_name, seen_types | {base}
                )
                self._mark_inherited(decl, base)
            self._collect(derivation, decl, parent_name)
            return

        if simple_content is not None:
            derivation = simple_content.find(XS + 'extension')
            if derivation is None:
                derivation = simple_content.find(XS + 'restriction')
            if derivation is not None:
                base = strip_prefix(derivation.get('base'))
                if decl.base_type is None:
                    decl.base_type = base
                if base in self.complex_types and base not in seen_types:
                    self._resolve_complex_type(
                        self.complex_types[base], decl, parent_name, seen_types | {base}
                    )
                    self._mark_inherited(decl, base)
                self._collect(derivation, decl, parent_name)
            return

        self._collect(ct_node, decl, parent_name)

    @staticmethod
    def _mark_inherited(decl, base):
        """Tag everything collected so far as arriving from `base`."""
        decl.attributes[:] = [
            attr if attr.via_base else replace(attr, via_base=base)
            for attr in decl.attributes
        ]

    def _collect(self, node, decl, parent_name):
        """Collect this level's own particles, attributes and group references."""
        self._walk_content(node, _Ctx(), decl, parent_name, frozenset())

        for attr in node.findall(XS + 'attribute'):
            name = attr.get('name') or strip_prefix(attr.get('ref'))
            if name is None:
                continue
            source = attr
            if attr.get('name') is None and name in self.global_attributes:
                source = self.global_attributes[name]
            decl.attributes.append(Attribute(
                name=name,
                type_ref=strip_prefix(source.get('type')),
                use=attr.get('use', 'optional'),
                default=attr.get('default'),
                doc=documentation(source),
            ))

        for group_ref in node.findall(XS + 'attributeGroup'):
            ref = strip_prefix(group_ref.get('ref'))
            if ref and ref not in decl.attribute_groups:
                decl.attribute_groups.append(ref)

        if node.find(XS + 'anyAttribute') is not None:
            decl.has_extension_point = True

    def _walk_content(self, node, ctx, decl, parent_name, seen_groups):
        for child in node:
            tag = localname(child.tag)

            if tag == 'element':
                lo, hi = occurs(child)
                name = child.get('name') or strip_prefix(child.get('ref'))
                if name is None:
                    continue
                decl.children.append(Particle(
                    parent=parent_name,
                    child=name,
                    lo=0 if ctx.in_choice else _mul(ctx.lo, lo),
                    hi=_mul(ctx.hi, hi),
                    compositor=ctx.compositor,
                    path=ctx.path,
                ))

            elif tag in COMPOSITORS:
                clo, chi = occurs(child)
                self._walk_content(
                    child,
                    _Ctx(
                        lo=_mul(ctx.lo, clo),
                        hi=_mul(ctx.hi, chi),
                        compositor=tag,
                        # A branch of a multi-branch choice is individually
                        # optional even when the choice itself is required.
                        in_choice=ctx.in_choice or (
                            tag == 'choice' and _branch_count(child) > 1
                        ),
                        path=ctx.path + (tag,),
                    ),
                    decl, parent_name, seen_groups,
                )

            elif tag == 'group':
                ref = strip_prefix(child.get('ref'))
                if ref is None or ref in seen_groups or ref not in self.groups:
                    continue
                clo, chi = occurs(child)
                self._walk_content(
                    self.groups[ref],
                    _Ctx(
                        lo=_mul(ctx.lo, clo),
                        hi=_mul(ctx.hi, chi),
                        compositor=ctx.compositor,
                        in_choice=ctx.in_choice,
                        path=ctx.path + ('group:' + ref,),
                    ),
                    decl, parent_name, seen_groups | {ref},
                )

            elif tag == 'any':
                decl.has_extension_point = True

    def _expand_attribute_group(self, name, seen=None):
        seen = seen or frozenset()
        if name in seen or name not in self.attribute_groups:
            return []
        node = self.attribute_groups[name]
        found = []
        for attr in node.findall(XS + 'attribute'):
            attr_name = attr.get('name') or strip_prefix(attr.get('ref'))
            if attr_name is None:
                continue
            source = attr
            if attr.get('name') is None and attr_name in self.global_attributes:
                source = self.global_attributes[attr_name]
            found.append(Attribute(
                name=attr_name,
                type_ref=strip_prefix(source.get('type')),
                use=attr.get('use', 'optional'),
                default=attr.get('default'),
                doc=documentation(source),
                via_group=name,
            ))
        for nested in node.findall(XS + 'attributeGroup'):
            found.extend(
                self._expand_attribute_group(
                    strip_prefix(nested.get('ref')), seen | {name}
                )
            )
        return found


def _branch_count(compositor_node):
    """Number of particles directly under a compositor."""
    return sum(
        1 for child in compositor_node
        if localname(child.tag) in ('element', 'group', 'any') + COMPOSITORS
    )


def _dedupe_particles(particles):
    """
    Collapse identical parent/child edges, keeping the most permissive bounds.
    A child reachable by more than one route is available under the union of
    those routes, not the intersection.
    """
    merged = {}
    for particle in particles:
        key = (particle.parent, particle.child)
        existing = merged.get(key)
        if existing is None:
            merged[key] = particle
            continue
        merged[key] = replace(
            existing,
            lo=min(existing.lo, particle.lo),
            hi=max(existing.hi, particle.hi),
        )
    return [merged[key] for key in sorted(merged)]


def load(path):
    if not os.path.isfile(path):
        raise IOError('schema not found: %s' % path)
    return Schema(path)
