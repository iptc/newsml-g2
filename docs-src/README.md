# NewsML-G2 Specification and Guidelines sources

The AsciiDoc sources of the two NewsML-G2 books. Edit them here.

| Folder | Master document | Moved from |
|---|---|---|
| `specification/` | `IPTC-G2-Specification.adoc` | [iptc/newsml-g2-specification](https://github.com/iptc/newsml-g2-specification) at `97c19b5` (2.36, 2026-11-08) |
| `guidelines/` | `IPTC-G2-Implementation_Guide.adoc` | [iptc/newsml-g2-guidelines](https://github.com/iptc/newsml-g2-guidelines) at `6fb0dda` (2.35, 2026-10-09) |

The history of each file before the move is in those repositories. Only what
the NewsML-G2 books use was moved: the SportsML and Trust Indicators documents
stay in `newsml-g2-guidelines`, and images that no chapter references were left
behind.

## Building

The whole documentation site (both books, split into chapter pages, plus the
schema reference) is built from these sources by

```bash
tools/docsite.py
```

which writes `build/site/`. CI runs the same build on every push. Needs
`asciidoctor` on `PATH`; see `tools/prosedoc/README.md`.

To preview one book as a single page while editing, run Asciidoctor on its
master document as before, for example:

```bash
cd docs-src/specification && asciidoctor -o /tmp/spec.html IPTC-G2-Specification.adoc
```

## Layout

Each book keeps the layout it had in its own repository, so that every
`include::` and `image::` path still resolves unchanged:

- `_includes/` holds the chapters, tables and (Guidelines) code examples.
- `images/` holds the figures.
- `stylesheets/` is used only by the single-page preview; the site build uses
  its own styling.
- `NML-G2-annual-maint.sh`, `sed-script` and `NMLG2_tables4spec1.py` are the
  annual version-bump and table-generation helpers each repository carried.
