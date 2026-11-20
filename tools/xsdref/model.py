# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 International Press Telecommunications Council (IPTC)
# The MIT License — see LICENSE in the repository root.

"""
Data model for the NewsML-G2 schema reference.

The unit of reference is an element *name*, not a global declaration. 84 of the
206 element names in the 2.35 Power schema exist only as local declarations
(`bit`, `remoteContent`, `hop`, `eventStatus`, …), and several names are
declared more than once with different content models — `contentMeta` is
declared six times, once under each Item type. A model keyed on global
declarations would omit most of what a reader looks up.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field


def format_occurs(lo, hi):
    """
    Render a cardinality pair the way a reader expects to see it.
    """
    hi_text = '∞' if hi == math.inf else str(hi)
    if lo == hi:
        return str(lo)
    return '%s..%s' % (lo, hi_text)


@dataclass(frozen=True)
class Attribute:
    """An attribute declaration, as it applies to some element."""

    name: str
    type_ref: str = None
    use: str = 'optional'
    default: str = None
    doc: str = None
    # Name of the attributeGroup it arrived through, or None if declared
    # directly on the element's own type.
    via_group: str = None
    # Name of the base type it was inherited from, or None if declared at the
    # element's own level.
    via_base: str = None

    @property
    def is_local(self):
        return self.via_group is None and self.via_base is None


@dataclass(frozen=True)
class Particle:
    """
    One parent/child edge in the instance-document graph.

    `parent` and `child` are always element names as they appear in an instance
    document. Named groups are inlined before particles are built, so a group
    name never appears here — reporting `itemClass`'s parent as
    `ItemManagementGroup` would name something that appears in no document.

    `lo`/`hi` are *effective* cardinality, computed by climbing the compositor
    ancestry rather than read off the declaration. Most local particles in this
    schema carry no minOccurs/maxOccurs and so default to 1..1, but sit inside
    `<xs:choice minOccurs="0" maxOccurs="unbounded">`; reporting them as 1..1
    would be normatively wrong.
    """

    parent: str
    child: str
    lo: int
    hi: object          # int, or math.inf for unbounded
    compositor: str     # sequence | choice | all
    # Raw XSD ancestry, kept for debugging the group/extension flattening.
    path: tuple = ()

    @property
    def occurs(self):
        return format_occurs(self.lo, self.hi)

    @property
    def is_repeatable(self):
        return self.hi == math.inf or self.hi > 1

    @property
    def is_optional(self):
        return self.lo == 0


@dataclass
class Declaration:
    """
    One declaration of an element name. A name may have several of these.
    """

    name: str
    kind: str = 'element'       # element | attribute
    scope: str = None           # containing element name; None if global
    doc: str = None
    type_ref: str = None
    # Set when the content model is an extension of a named type.
    base_type: str = None
    children: list = field(default_factory=list)        # list[Particle]
    attributes: list = field(default_factory=list)      # list[Attribute]
    attribute_groups: list = field(default_factory=list)
    # True when the content model carries an xs:any wildcard.
    has_extension_point: bool = False

    @property
    def is_global(self):
        return self.scope is None


@dataclass
class ElementRef:
    """
    Everything known about one element *name*, across all its declarations.
    """

    name: str
    declarations: list = field(default_factory=list)     # list[Declaration]
    parents: list = field(default_factory=list)          # list[Particle]

    @property
    def doc(self):
        for decl in self.declarations:
            if decl.doc:
                return decl.doc
        return None

    @property
    def is_global(self):
        return any(decl.is_global for decl in self.declarations)

    @property
    def context_count(self):
        return len(self.declarations)

    @property
    def is_deprecated(self):
        """
        True when any declaration's documentation marks the construct
        deprecated. The hand-built spreadsheet carried this by appending
        "(deprecated)" to the element name; it is recoverable from the schema,
        so it is reported rather than dropped.
        """
        return any(
            decl.doc and 'deprecat' in decl.doc.lower()
            for decl in self.declarations
        )

    @property
    def has_varying_doc(self):
        """
        True when declarations of the same name carry different
        `xs:documentation`. 19 of the 206 names in 2.35 do, so showing only the
        first declaration's definition would misdescribe the others —
        `contentMeta` is defined six times and four of those differ.
        """
        docs = {decl.doc for decl in self.declarations if decl.doc}
        return len(docs) > 1

    @property
    def has_varying_content(self):
        """
        True when the name is declared more than once with content models that
        actually differ, which is what the reader needs warning about.
        """
        if len(self.declarations) < 2:
            return False
        shapes = {
            (
                tuple(sorted(p.child for p in decl.children)),
                tuple(sorted(a.name for a in decl.attributes)),
                tuple(sorted(decl.attribute_groups)),
            )
            for decl in self.declarations
        }
        return len(shapes) > 1
