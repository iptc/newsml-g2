# prosedoc — Specification and Guidelines in the shared shell

Renders the two prose documents into the same three-part frame as the schema
reference: artefact links and search across the top, chapters down the left
with the current chapter's sections expanded, sub-headings on the right.

```sh
# both books, from their AsciiDoc sources in docs-src/
tools/prosedoc/generate.py --all

# one book, explicitly (a master .adoc, or an already rendered .html)
tools/prosedoc/generate.py --book docs-src/specification/IPTC-G2-Specification.adoc \
                           --name Specification
```

Output goes to `build/site/`, which is gitignored. To build the books together
with the schema reference as one site, with every link between them local, use
`tools/docsite.py` instead; serve the result with `python3 -m http.server`.
CI runs `tools/docsite.py` on every pull request and keeps the site as a build
artifact.

Each book is rendered from its master document by Asciidoctor, split into
chapters, and written with the images it uses. Cross-references are rewritten
as the books are split: `#the-data-model` becomes
`introduction.html#the-data-model`, and links to the published books on
iptc.org become links to the local pages. Chapters with STEM (maths) content
get the book's MathJax scripts back, which splitting would otherwise drop.

Needs `asciidoctor` on PATH. CI pins the version (see `.github/workflows/ci.yml`),
because the splitter reads Asciidoctor's HTML; upgrade it deliberately and
check the output. Any Asciidoctor warning, such as an include or image that
does not resolve, fails the build.

## Old links into the single-page books

Outside documents link to section anchors on the single-page books — the
ninjs Guidelines link to `specification/#introduction-to-eventsml-g2` — and
once split, that section is on its own page. The fragment never reaches the
web server, so this cannot be a server redirect. Instead each book folder gets
an `index.html` holding the book's anchor map, which sends the reader on to
the chapter page with the anchor: `specification/#introduction-to-eventsml-g2`
becomes `specification/introduction-to-eventsml-g2.html#introduction-to-eventsml-g2`.
An anchor the map does not know lands on the Preface.

Every anchor in the published 2.36 Specification and 2.35 Guidelines is in the
map, apart from the old page's own chrome (`#toc`, `#header` and so on), and
lands on a page that has it. For the old URLs to reach these pages,
`/std/NewsML-G2/specification/` and `/guidelines/` must serve the new book
folders when the site is published; today the Specification URL is a server
redirect to the versioned single-page file, which keeps the fragment.

## Still to do

**The layout is a review harness, not a design.** The published site is a
Phase 3 decision and will use the IPTC design system. What is worth settling
now is the information architecture — how chapters divide, what each
navigation level carries — because that is renderer-independent.

**No link check.** The build fails on a broken include or image, but nothing
yet checks the links in the finished site. A dozen cross-references are
already broken in the sources (e.g. `#_bookmark911` in §14).

## What it gets right, and why those were not obvious

**It parses; it does not slice.** Asciidoctor wraps each chapter in
`<div class="sect1"><h2>…</h2><div class="sectionbody">…</div></div>`.
Splitting the HTML string at heading positions severs those wrappers: every
chunk then carries a stray closing tag and lacks its opening one. Tag *counts*
still balance, so the damage is invisible to a count and obvious in a browser,
which reparents whatever follows — in this case swallowing the right-hand
navigation into the body text.

**It renders the whole book, then splits it.** IPTC's own documents cite
NewsML-G2 by section number (the errata page, for one), and the master document
is what numbers the sections. Rendering each chapter file on its own loses that
numbering; reconstructing `2.6.1` would mean reimplementing Asciidoctor's
numbering and hoping the two agree. Splitting the rendered book keeps those
strings byte for byte.

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
| `split.py` | Parse a rendered book into chapters; fold front matter; find images and STEM |
| `render.py` | Emit the page shell, navigation and styling |
| `generate.py` | Render the master documents; command line entry point |
