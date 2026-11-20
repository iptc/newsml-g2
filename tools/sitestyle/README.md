# sitestyle — the look of the NewsML-G2 documentation site

The Specification and Guidelines (`tools/prosedoc`) and the schema reference
(`tools/xsdref`) are written by different tools but read as one site. This
package holds what they share:

| File | Purpose |
|---|---|
| `__init__.py` | The page frame: draft bar, top bar with the parts and search, sidebar, "On this page" column, footer |
| `assets/site.css` | The stylesheet for every page, including Asciidoctor's markup and the reference's tables |
| `assets/site.js` | Site-wide search and the "On this page" highlight |
| `assets/fonts/` | Montserrat and Lora (SIL Open Font License 1.1; see the `OFL-*.txt` files) |
| `assets/iptc-logo.svg` | The IPTC mark, from iptc.org/about-iptc/logos-and-design-assets/ |

The house style is the IPTC one used by the
[Media Provenance guide](https://media-provenance-guide.iptc.org/):
Montserrat headings, Lora text, navy and blue with green accents. Change it in
`site.css` and every page follows.

Every page sits one folder below the site root (`specification/`,
`guidelines/`, `reference/`) and links the assets as `../assets/`.
`write_assets(site_root)` copies them there; both tools call it, so a book or
the reference built on its own is styled too.
