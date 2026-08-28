# xsdref — schema reference generator

Generates NewsML-G2 reference documentation from the XML Schema, replacing two
hand-run steps in the release process:

- **`MAINTENANCE.md` step 13** — "Use XML Spy to create XML Schema documentation".
  The only GUI step in an 18-step release, and the reason the repository carries
  an XMLSpy licence.
- **The Structure Matrix spreadsheet** in `documentation/`, last genuinely
  updated for 2.27.

The schema is the only machine-readable source of truth NewsML-G2 has: 898
`xs:documentation` strings, 412 of 415 attributes documented, and only 2 of 241
element declarations undocumented.

## Usage

Requires `lxml`, already pinned in `tests/requirements.txt`.

```sh
# Check Specification §14 annotations still match the schema. Exits 1 on a
# mismatch. Needs the newsml-g2-specification repo checked out alongside this
# one; skips with a message if it is not there.
tools/xsdref/generate.py --check

# Regenerate the committed Structure Matrix for every version in releases/
tools/xsdref/generate.py --matrix --all-versions

# Fail if a committed matrix has drifted from its schema (this runs in CI)
tools/xsdref/generate.py --verify-matrix --all-versions

# Write the AsciiDoc reference pages and the §14 note partials
tools/xsdref/generate.py --pages --partials --output build/reference
```

## What it produces

| Output | Where | Notes |
|---|---|---|
| Structure Matrix | `documentation/structure-matrix/*.csv` | Committed and CI-verified. One file per released version. |
| Reference pages | `build/reference/pages/*.adoc` | One page per element name, plus one per attributeGroup. |
| §14 note partials | `build/reference/partials/notes/*.adoc` | One file per annotation, each carrying an explicit binding key. |
| Navigation | `build/reference/nav.adoc` | Generated, never hand-authored, so it cannot drift from the pages. |

## Three things this gets right that a few XPath expressions would not

**Named groups are inlined transitively before parent/child edges are built.**
`itemMeta` contains `<xs:group ref="ItemManagementGroup"/>`, which contains
`<xs:element ref="itemClass"/>`. Without inlining, `itemClass`'s parent is
reported as `ItemManagementGroup` — a name that appears in no instance document
and means nothing to a reader.

**Effective cardinality is computed by climbing the compositor ancestry.** Most
local particles carry no `minOccurs`/`maxOccurs` and so default to 1..1, but sit
inside `<xs:choice minOccurs="0" maxOccurs="unbounded">` — the standard G2 "any
of these, in any order, any number" pattern. 890 particles in 2.35 would be
reported as 1..1 by a naive reader, which in a normative reference is a defect,
not a cosmetic issue.

**The unit of reference is an element name, not a global declaration.** 84 of
206 element names exist only as local declarations — `bit`, `remoteContent`,
`hop`, `eventStatus`, `assignedTo` — and those are precisely what §14 writes
about. `contentMeta` is declared six times with four different definitions and
differing content models; 19 element names are documented differently depending
on where they are declared.

## Design choices worth knowing

**Inherited attributeGroups are referenced, never expanded inline.** Expanding
the closure would make roughly 240 pages 90% identical boilerplate. That is
exactly why the XMLSpy `NewsItem` page is 12 MB; the largest page here is 59 KB.

**Content models render as an indented text tree, not a diagram.** It answers
the question a reader actually has ("what can go inside `<contentMeta>`?"), it is
searchable and diffable in review, it is accessible, and it needs no rendering
dependency. No Kroki backend reproduces XMLSpy's box notation, and a bespoke
renderer for it would not be maintained.

**§14 annotations are bound once, here, not by regex at render time.** Entry
headings are `Human Readable Name <separator> constructName`, but the separator
is an en-dash 77 times and an ASCII hyphen 18 times, five §14.6 headings have no
parseable name, and the §14.7 headings are bare type names. `HEADING_OVERRIDES`
in `notes.py` maps those by hand; `--check` reports any heading it cannot bind so
the table cannot silently rot.

**Note bodies have their `include::` directives resolved inline**, because they
pull in table fragments by paths relative to the specification repository, and
the generated reference is written elsewhere.

## Files

| File | Purpose |
|---|---|
| `model.py` | Dataclasses: `Declaration`, `Particle`, `Attribute`, `ElementRef` |
| `schema.py` | XSD parsing: group inlining, extension chains, cardinality, attribute closure |
| `notes.py` | Parses Specification §14, binds annotations to constructs, `--check` |
| `matrix.py` | Structure Matrix generation and freshness verification |
| `render.py` | AsciiDoc page and navigation emission |
| `generate.py` | Command-line entry point |
