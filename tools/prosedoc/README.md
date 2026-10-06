# prosedoc — Specification and Guidelines in the shared shell

Renders the two prose documents into the same three-part frame as the schema
reference: artefact links and search across the top, chapters down the left
with the current chapter's sections expanded, sub-headings on the right.

```sh
# both books, from the sibling repositories
tools/prosedoc/generate.py --all

# one book, explicitly
tools/prosedoc/generate.py --book ../newsml-g2-specification/index.html \
                           --name Specification
```

Output goes to `build/docs/`, which is gitignored. Serve it with
`python3 -m http.server` from there.

## This is provisional, and here is exactly why

**It reads the built HTML, not the AsciiDoc sources.** The input is
`index.html` from the specification and guidelines repositories — the file
`asciidoctor-to-html.sh` produces when somebody runs it by hand. So the build
depends on a working copy of two other repositories being checked out next
door and up to date. That is the least maintainable thing here and the first
thing to fix.

It is a deliberate trade rather than an oversight. Rendering chapter files
individually loses everything the master document supplies — above all the
section numbering, which other specifications cite. Reconstructing `2.6.1`
from chapter sources means reimplementing Asciidoctor's numbering and hoping
the two agree. Splitting the rendered book keeps those strings byte for byte.

**The layout is a review harness, not a design.** The published site is a
Phase 3 decision and will use the IPTC design system. What is worth settling
now is the information architecture — how chapters divide, what each
navigation level carries — because that is renderer-independent.

**Nothing checks the output.** No link checking, no comparison against the
source document, no CI. The schema reference has all three; this does not yet.

## What it gets right, and why those were not obvious

**It parses; it does not slice.** Asciidoctor wraps each chapter in
`<div class="sect1"><h2>…</h2><div class="sectionbody">…</div></div>`.
Splitting the HTML string at heading positions severs those wrappers: every
chunk then carries a stray closing tag and lacks its opening one. Tag *counts*
still balance, so the damage is invisible to a count and obvious in a browser,
which reparents whatever follows — in this case swallowing the right-hand
navigation into the body text.

**Section numbering comes from the rendered book.** Other documents cite
NewsML-G2 by section number, so those strings are load-bearing.

**Sections are `h3`, not `h2`.** Both documents use exactly one `h2` per
chapter — the chapter title. Expanding `h2` in the navigation shows a single
entry repeating the title, which is what an earlier draft did.

**Filenames come from each chapter's own anchor.** Those anchors are already
the target of every cross-reference in the sources, so `link:#x[]` maps to
`x.html` mechanically rather than through a hand-maintained lookup.

**Front matter is folded into one Preface page.** Only the leading unnumbered
run: the Guidelines close with an unnumbered "Additional Resources", which is
a section rather than front matter. Without this the Specification's Preface
file — which holds four top-level sections — was silently titled after the
first of them.

## Files

| File | Purpose |
|---|---|
| `split.py` | Parse a rendered book into chapters; fold front matter |
| `render.py` | Emit the page shell, navigation and styling |
| `generate.py` | Command line entry point |
