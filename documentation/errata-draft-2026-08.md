# Draft errata entries — NewsML-G2 Specification

For addition to https://iptc.org/std/NewsML-G2/NewsML-G2-spec-errata.html,
whose last entry is number 6, dated 2020-12-11. Numbering continues from there.

These are drafts for review, not published errata. The corresponding schema
changes are on the `schema-errata-roleuri-contentmeta` branch and require a
Change Request and Standards Committee approval before release.

---

## Erratum number 7

**Entry date** — 2026-08-22

**Issue** — In the NewsML-G2 XML Schemas from version 2.18 to 2.35, the URI
sibling of the `role` attribute on `<altLoc>` is misspelled `roleruri` instead
of `roleuri`. Every other QCode attribute in the schema follows the documented
convention of appending "uri" to the QCode attribute name, and `roleuri` is
spelled correctly in the 24 other places it appears. The misspelled attribute
is declared immediately after `role`, is of type `IRIType`, and carries the
documentation "A refinement of the semantics or business purpose of the
property - expressed by a URI", so its intent is unambiguous.

The practical effect is that the URI alternative to `role` on this property
cannot be used under the name the convention predicts, and a document using
`roleuri` there is invalid.

**Planned correction** — Rename the attribute to `roleuri`. Will be applied in
the next annual Public Release.

**Note** — This is a breaking change for any implementation that has used
`roleruri`, which has been present since 2.18. Documents using `roleruri` will
cease to validate. Given that the attribute cannot be discovered by following
the naming convention, and that it appears in none of the IPTC example
documents, the number of affected implementations is expected to be very small.
Providers who have used it should move to `roleuri` at the same release.

---

## Erratum number 8

**Entry date** — 2026-08-22

**Issue** — In the NewsML-G2 XML Schemas up to and including version 2.35, the
`<contentMeta>` child of `<catalogItem>` is documented as "Content Metadata for
a Planning Item". This is a copy of the documentation for the `<contentMeta>`
child of `<planningItem>` and describes the wrong Item type.

This affects the `xs:documentation` annotation only. The content model is
correct: the element is of type `ContentMetadataCatType`, which is the Catalog
Item content metadata type.

**Planned correction** — Change the documentation to "Content Metadata for a
Catalog Item". Will be applied in the next annual Public Release.

**Note** — Documentation only. No effect on validation, and no implementation
impact.

---

## How these were found

Both were surfaced by `tools/xsdref`, which generates the schema reference and
the Structure Matrix from the XSD. `roleruri` appeared as an attribute column
with a single occupied cell against 24 for `roleuri`; the `<catalogItem>`
documentation appeared on the generated `contentMeta` page, which lists each of
that element's six declarations with its own definition side by side, making the
duplicate visible.
