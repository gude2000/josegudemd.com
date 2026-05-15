#!/usr/bin/env python3
"""
Build PDF and EPUB editions of the Synthesis essay from the-evidence.html.
Output goes into /Users/josegudem2/Desktop/josegudemd_website/dist/
"""
import os
import re
import sys
from pathlib import Path
from html.parser import HTMLParser
from datetime import date

ROOT = Path(__file__).parent
SITE_BASE = "https://josegudemd.com"
DIST = ROOT / "dist"
DIST.mkdir(exist_ok=True)


# ---- 1. Extract the <main> content from the source HTML ----

def extract_main(html_path: Path) -> str:
    text = html_path.read_text(encoding="utf-8")
    m = re.search(r"<main[^>]*>(.*?)</main>", text, re.S)
    if not m:
        raise SystemExit(f"No <main> block found in {html_path}")
    body = m.group(1)
    return body


def rewrite_relative_links(html: str, base: str) -> str:
    """Turn relative href="foo.html" into absolute https://josegudemd.com/foo.html
    so the PDF/EPUB links go somewhere when clicked from a reader."""
    def repl(m):
        url = m.group(2)
        # leave anchors, mailto, and absolute URLs alone
        if url.startswith(("http://", "https://", "mailto:", "#")):
            return m.group(0)
        return f'{m.group(1)}="{base}/{url}"'
    return re.sub(r'(href|src)="([^"]+)"', repl, html)


def split_into_sections(body_html: str):
    """Return (hero_html, [(section_num, title, html), ...], closing_dim_html)."""
    sections = re.findall(r"<section[^>]*>(.*?)</section>", body_html, re.S)
    if not sections:
        raise SystemExit("No <section> blocks")
    hero_html = sections[0]
    chapters = []
    closing = None
    for s in sections[1:]:
        h2_m = re.search(r"<h2[^>]*>(.*?)</h2>", s, re.S)
        if h2_m:
            title_raw = h2_m.group(1).strip()
            num_m = re.match(r"^\s*(\d+)\.\s*(.*)$", re.sub(r"<[^>]+>", "", title_raw))
            if num_m:
                num = int(num_m.group(1))
                title_clean = num_m.group(2).strip()
            else:
                num = None
                title_clean = re.sub(r"<[^>]+>", "", title_raw).strip()
            chapters.append((num, title_clean, s))
        else:
            # the trailing "If you have read this far" dim section
            closing = s
    return hero_html, chapters, closing


# ---- 2. Build a print-ready HTML doc (6×9 trim) for weasyprint ----

PRINT_CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Inter:wght@400;600&display=swap');

@page {
  size: 6in 9in;
  margin: 0.75in 0.7in 0.85in 0.7in;
  @bottom-center {
    content: counter(page);
    font-family: 'Inter', sans-serif;
    font-size: 9pt;
    color: #6f6856;
  }
}
@page :first { @bottom-center { content: ""; } }
@page :left  { margin-left:  0.85in; margin-right: 0.55in; @bottom-left  { content: counter(page); font-family:'Inter',sans-serif; font-size:9pt; color:#6f6856;} @bottom-center{content:""} }
@page :right { margin-left:  0.55in; margin-right: 0.85in; @bottom-right { content: counter(page); font-family:'Inter',sans-serif; font-size:9pt; color:#6f6856;} @bottom-center{content:""} }

html, body {
  font-family: 'Libre Baskerville', 'Iowan Old Style', Georgia, serif;
  font-size: 10.5pt;
  line-height: 1.55;
  color: #1a1a1a;
  background: #fbfaf7;
  margin: 0; padding: 0;
}
p { margin: 0 0 0.55em 0; orphans: 3; widows: 3; text-align: justify; hyphens: auto; }
em { font-style: italic; }
strong { font-weight: 700; }
a { color: #a86b1d; text-decoration: none; border-bottom: 1px dotted #c19056; }
a:hover { color: #6a4413; }
ul { padding-left: 1.2em; margin: 0.6em 0; }
li { margin-bottom: 0.55em; }

h1.book-title {
  font-family: 'Libre Baskerville', serif;
  font-size: 30pt;
  line-height: 1.15;
  font-weight: 400;
  text-align: center;
  margin: 2.5in 0 0.4in 0;
  letter-spacing: 0.01em;
}
h2.book-subtitle {
  font-family: 'Libre Baskerville', serif;
  font-style: italic;
  font-size: 14pt;
  text-align: center;
  font-weight: 400;
  margin: 0 0 1.6in 0;
  color: #4a4030;
}
.byline {
  font-family: 'Inter', sans-serif;
  font-size: 11pt;
  text-align: center;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #5a4f3a;
  margin-top: 0.4in;
}
.tagline {
  font-family: 'Libre Baskerville', serif;
  font-style: italic;
  font-size: 10pt;
  text-align: center;
  color: #6f6856;
  margin-top: 0.3in;
}

.title-page, .toc-page, .colophon-page { page-break-after: always; }
.section-page { page-break-before: always; }

.eyebrow {
  font-family: 'Inter', sans-serif;
  font-size: 8.5pt;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #9c7d3a;
  text-align: center;
  margin: 0 0 0.4em 0;
}

h1.hero-h1 {
  font-family: 'Libre Baskerville', serif;
  font-size: 18pt;
  text-align: center;
  font-weight: 400;
  margin: 0.4em 0 0.8em 0;
  line-height: 1.25;
}

.lede {
  font-family: 'Libre Baskerville', serif;
  font-style: italic;
  font-size: 11pt;
  line-height: 1.55;
  color: #2c2820;
  margin: 0 0 1em 0;
  text-align: justify;
  hyphens: auto;
}

.dim {
  color: #5a4f3a;
  font-size: 9.5pt;
  text-align: justify;
  hyphens: auto;
}

h2.section-h2 {
  font-family: 'Libre Baskerville', serif;
  font-size: 15pt;
  font-weight: 700;
  margin: 0 0 1em 0;
  line-height: 1.25;
  color: #1a1a1a;
}
.section-num {
  font-family: 'Inter', sans-serif;
  font-size: 9pt;
  letter-spacing: 0.20em;
  text-transform: uppercase;
  color: #a86b1d;
  margin-bottom: 0.6em;
}

.rule {
  border-top: 1px solid #c19056;
  width: 1.6in;
  margin: 1.2em auto;
}

/* Table of contents */
h2.toc-title {
  font-family: 'Libre Baskerville', serif;
  font-size: 15pt;
  font-weight: 700;
  text-align: center;
  margin: 0 0 1.6em 0;
}
.toc-row {
  display: flex;
  font-size: 11pt;
  line-height: 1.85;
  border-bottom: 1px dotted #d8cdb2;
}
.toc-num { flex: 0 0 1.4em; color: #a86b1d; font-family: 'Inter',sans-serif; font-size: 9pt; padding-top: 4pt;}
.toc-title-text { flex: 1; padding-right: 0.5em; }
.toc-page-num { flex: 0 0 1.4em; text-align: right; color: #5a4f3a; font-family: 'Inter',sans-serif; font-size: 9pt; padding-top: 4pt;}

/* colophon */
.colophon-page {
  text-align: center;
  padding-top: 3in;
  color: #5a4f3a;
}
.colophon-page .seal {
  font-family: 'Inter', sans-serif;
  font-size: 9pt;
  letter-spacing: 0.20em;
  text-transform: uppercase;
  color: #a86b1d;
  margin-bottom: 0.5em;
}
.colophon-page p { text-align: center; font-size: 10pt; line-height: 1.5; }
"""


def build_print_html(chapters, hero_html, closing_html, base_url, cfg):
    """Return HTML string for weasyprint."""
    # title page
    parts = []
    parts.append(f"<!doctype html><html lang='{cfg['lang_iso']}'><head>")
    parts.append("<meta charset='utf-8'>")
    parts.append(f"<title>{cfg['title']} — {('The Field Trilogy Synthesis' if cfg['lang_iso']=='en' else 'La Trilogía del Campo · Síntesis')}</title>")
    parts.append(f"<style>{PRINT_CSS}</style>")
    parts.append("</head><body>")

    # Title page: split on space at midpoint for visual balance
    title_words = cfg["title"].split(" ")
    half = len(title_words) // 2
    title_line1 = " ".join(title_words[:half])
    title_line2 = " ".join(title_words[half:])
    parts.append(f'''
      <div class="title-page">
        <h1 class="book-title">{title_line1}<br>{title_line2}</h1>
        <h2 class="book-subtitle">{cfg["subtitle"]}</h2>
        <p class="byline">{cfg["byline"]}</p>
        <p class="tagline">{cfg["tagline"]}</p>
      </div>
    ''')

    # TOC
    parts.append('<div class="toc-page">')
    parts.append(f'<h2 class="toc-title">{cfg["toc_label"]}</h2>')
    for num, title, _ in chapters:
        n = f"{num}." if num else "—"
        parts.append(f'''
          <div class="toc-row">
            <div class="toc-num">{n}</div>
            <div class="toc-title-text"><a href="#section-{num}" style="color:inherit;border:none;">{title}</a></div>
            <div class="toc-page-num"></div>
          </div>
        ''')
    parts.append('</div>')

    # Hero / preface
    hero_clean = rewrite_relative_links(hero_html, base_url)
    # adapt classes for print: eyebrow → .eyebrow, h1 → .hero-h1, p.lede → .lede
    hero_clean = re.sub(r'<p class="eyebrow"[^>]*>', '<p class="eyebrow">', hero_clean)
    hero_clean = re.sub(r'<h1[^>]*>', '<h1 class="hero-h1">', hero_clean)
    hero_clean = re.sub(r'<p class="lede"[^>]*>', '<p class="lede">', hero_clean)
    hero_clean = re.sub(r'<p class="dim"[^>]*>', '<p class="dim">', hero_clean)
    parts.append(f'<div class="section-page">{hero_clean}<div class="rule"></div></div>')

    # Each numbered section starts on a new page
    for num, title, body in chapters:
        body_clean = rewrite_relative_links(body, base_url)
        # extract content after the <h2>
        body_clean = re.sub(r"<h2[^>]*>.*?</h2>", "", body_clean, count=1, flags=re.S)
        # promote class adjustments
        body_clean = re.sub(r'<p class="dim"[^>]*>', '<p class="dim">', body_clean)
        n_str = f"{num}" if num else ""
        anchor = f"section-{num}" if num else ""
        parts.append(f'''
          <div class="section-page">
            <div id="{anchor}" class="section-num">{cfg["section_label"]} {n_str}</div>
            <h2 class="section-h2">{title}</h2>
            {body_clean}
          </div>
        ''')

    # Closing dim
    if closing_html:
        closing_clean = rewrite_relative_links(closing_html, base_url)
        closing_clean = re.sub(r'<p class="dim"[^>]*>', '<p class="dim">', closing_clean)
        # strip the read-more arrow link at the end since it's a site-only widget
        closing_clean = re.sub(r'<a [^>]*class="read-more"[^>]*>.*?</a>', '', closing_clean, flags=re.S)
        parts.append(f'<div class="section-page">{closing_clean}</div>')

    # Colophon
    colophon_intro_filled = cfg["colophon_intro"].format(base=base_url)
    parts.append(f'''
      <div class="colophon-page">
        <p class="seal">{cfg["colophon_seal"]}</p>
        <p>{colophon_intro_filled}</p>
        <p>{cfg["colophon_set"]}</p>
        <p>{cfg["colophon_hdr"]}</p>
        <p>{cfg["colophon_companion"]}</p>
        <p style="margin-top:1.5em;">© {date.today().year} José Gude, MD · Boise, Idaho</p>
      </div>
    ''')
    parts.append("</body></html>")
    return "".join(parts)


# ---- 3. Render PDF via weasyprint ----

def build_pdf(html_str: str, out_path: Path):
    from weasyprint import HTML
    HTML(string=html_str, base_url=str(ROOT)).write_pdf(str(out_path))
    print(f"PDF written: {out_path}  ({out_path.stat().st_size/1024:.1f} KB)")


# ---- 4. Build EPUB via ebooklib ----

EPUB_CSS = """
@namespace epub "http://www.idpf.org/2007/ops";
body { font-family: Georgia, 'Iowan Old Style', serif; line-height: 1.55; padding: 0; }
h1 { font-size: 1.6em; line-height: 1.2; text-align: left; margin: 1em 0 0.6em 0; font-weight: normal; }
h2 { font-size: 1.25em; line-height: 1.2; margin: 1.4em 0 0.7em 0; font-weight: bold; }
p { margin: 0 0 0.6em 0; text-align: justify; }
em { font-style: italic; }
strong { font-weight: bold; }
a { color: #a86b1d; text-decoration: none; }
ul { padding-left: 1.2em; margin: 0.6em 0; }
li { margin-bottom: 0.5em; }
.eyebrow { font-family: 'Helvetica Neue', sans-serif; font-size: 0.8em; letter-spacing: 0.14em; text-transform: uppercase; color: #9c7d3a; margin-bottom: 0.5em; }
.lede { font-style: italic; font-size: 1.05em; }
.dim { color: #5a4f3a; font-size: 0.95em; }
.section-num { font-family: 'Helvetica Neue', sans-serif; font-size: 0.78em; letter-spacing: 0.20em; text-transform: uppercase; color: #a86b1d; margin: 0 0 0.4em 0; }
.rule { border-top: 1px solid #c19056; width: 30%; margin: 1.2em auto; }
.title-block { text-align: center; padding: 2em 0 1em 0; }
.title-block h1 { font-size: 2em; text-align: center; }
.title-block .sub { font-style: italic; color: #4a4030; }
.title-block .byline { font-family: 'Helvetica Neue', sans-serif; letter-spacing: 0.14em; text-transform: uppercase; font-size: 0.85em; color: #5a4f3a; margin-top: 1em; }
"""


def build_epub(chapters, hero_html, closing_html, base_url, out_path: Path, cfg):
    from ebooklib import epub
    book = epub.EpubBook()
    book.set_identifier(cfg["ident"])
    full_title = f'{cfg["title"]} — {("The Field Trilogy Synthesis" if cfg["lang_iso"]=="en" else "La Trilogía del Campo · Síntesis")}'
    book.set_title(full_title)
    book.set_language(cfg["lang_iso"])
    book.add_author("José Gude, MD")
    book.add_metadata("DC", "description", cfg["metadata_desc"])
    book.add_metadata("DC", "subject", "Consciousness studies")
    book.add_metadata("DC", "subject", "Philosophy of mind")
    book.add_metadata("DC", "subject", "Quantum foundations")
    book.add_metadata("DC", "rights", f"© {date.today().year} José Gude MD")

    css = epub.EpubItem(uid="style", file_name="style/main.css",
                       media_type="text/css", content=EPUB_CSS)
    book.add_item(css)

    items = []

    # Title page
    title_words = cfg["title"].split(" ")
    half = len(title_words) // 2
    t1 = " ".join(title_words[:half])
    t2 = " ".join(title_words[half:])
    title_html = f"""<html xmlns="http://www.w3.org/1999/xhtml"><head><link rel="stylesheet" href="style/main.css"/><title>Title</title></head>
<body>
<div class="title-block">
  <h1>{t1}<br/>{t2}</h1>
  <p class="sub">{cfg["subtitle"]}</p>
  <p class="byline">{cfg["byline"]}</p>
  <div class="rule"></div>
  <p class="dim">{cfg["tagline"]}</p>
</div>
</body></html>"""
    title_item = epub.EpubHtml(title="Title", file_name="title.xhtml", lang=cfg["lang_iso"])
    title_item.content = title_html
    title_item.add_item(css)
    book.add_item(title_item)
    items.append(title_item)

    # Preface (the hero block)
    hero_clean = rewrite_relative_links(hero_html, base_url)
    hero_clean = re.sub(r'<h1[^>]*>(.*?)</h1>', r'<h1>\1</h1>', hero_clean, flags=re.S)
    preface = epub.EpubHtml(title=cfg["preface_title"], file_name="preface.xhtml", lang=cfg["lang_iso"])
    preface.content = f"""<html xmlns="http://www.w3.org/1999/xhtml"><head><link rel="stylesheet" href="style/main.css"/><title>{cfg["preface_title"]}</title></head>
<body>{hero_clean}<div class="rule"></div></body></html>"""
    preface.add_item(css)
    book.add_item(preface)
    items.append(preface)

    # Each numbered section as a chapter
    section_items = []
    for num, title, body in chapters:
        body_clean = rewrite_relative_links(body, base_url)
        body_clean = re.sub(r"<h2[^>]*>.*?</h2>", "", body_clean, count=1, flags=re.S)
        n = f"{num}" if num else ""
        chap = epub.EpubHtml(title=f"{num}. {title}" if num else title,
                            file_name=f"chap_{num:02d}.xhtml" if num else "chap_x.xhtml",
                            lang=cfg["lang_iso"])
        chap.content = f"""<html xmlns="http://www.w3.org/1999/xhtml"><head><link rel="stylesheet" href="style/main.css"/><title>{num}. {title}</title></head>
<body>
<div class="section-num">{cfg["section_label"]} {n}</div>
<h2>{title}</h2>
{body_clean}
</body></html>"""
        chap.add_item(css)
        book.add_item(chap)
        section_items.append(chap)

    # Closing
    closing_item = None
    if closing_html:
        closing_clean = rewrite_relative_links(closing_html, base_url)
        closing_clean = re.sub(r'<a [^>]*class="read-more"[^>]*>.*?</a>', '', closing_clean, flags=re.S)
        closing_item = epub.EpubHtml(title=cfg["closing_title"],
                                     file_name="closing.xhtml", lang=cfg["lang_iso"])
        closing_item.content = f"""<html xmlns="http://www.w3.org/1999/xhtml"><head><link rel="stylesheet" href="style/main.css"/><title>{cfg["closing_title"]}</title></head>
<body><h2>{cfg["closing_title"]}</h2>{closing_clean}</body></html>"""
        closing_item.add_item(css)
        book.add_item(closing_item)

    # navigation
    sections_label = "Sections" if cfg["lang_iso"] == "en" else "Secciones"
    book.toc = [
        epub.Link("preface.xhtml", cfg["preface_title"], "preface"),
        (epub.Section(sections_label),
         tuple(epub.Link(it.file_name, it.title, f"chap{num}")
               for (num, _, _), it in zip(chapters, section_items)))
    ]
    if closing_item:
        book.toc.append(epub.Link(closing_item.file_name, cfg["closing_title"], "closing"))

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    spine = ["nav", title_item, preface] + section_items
    if closing_item:
        spine.append(closing_item)
    book.spine = spine

    epub.write_epub(str(out_path), book)
    print(f"EPUB written: {out_path}  ({out_path.stat().st_size/1024:.1f} KB)")


# ---- main ----

EDITIONS = {
    "en": {
        "source": "the-evidence.html",
        "base_url": SITE_BASE,
        "pdf_name": "field-trilogy-synthesis.pdf",
        "epub_name": "field-trilogy-synthesis.epub",
        "html_name": "field-trilogy-synthesis.print.html",
        "title": "What the Evidence Shows So Far",
        "subtitle": "— in the Context of <em>The Field Trilogy</em>",
        "byline": "José Gude, MD",
        "tagline": "A synthesis essay · physics · biology · computation",
        "toc_label": "Contents",
        "section_label": "Section",
        "colophon_intro": 'This pamphlet collects the synthesis essay from <a href="{base}/the-evidence.html">josegudemd.com</a> in a single typeset volume.',
        "colophon_set": "Set in Libre Baskerville at 10.5 pt over 1.55, on a 6 × 9 inch trim.",
        "colophon_hdr": "Section headings and footnote markers in Inter.",
        "colophon_companion": "Companion to <em>The Field Trilogy</em>: <em>Anima</em> · <em>Numen</em> · <em>Limen</em>, and the standalone <em>Fragile Light</em>.",
        "colophon_seal": "Colophon",
        "ident": "josegudemd-synthesis-2026-en",
        "lang_iso": "en",
        "preface_title": "Preface",
        "closing_title": "If you have read this far",
        "metadata_desc": "A synthesis essay: how quantum foundations, Planck-scale physics, anomalous neurology, and information theory converge on the central thesis of The Field Trilogy.",
    },
    "es": {
        "source": "es/the-evidence.html",
        "base_url": SITE_BASE + "/es",
        "pdf_name": "trilogia-del-campo-sintesis.pdf",
        "epub_name": "trilogia-del-campo-sintesis.epub",
        "html_name": "trilogia-del-campo-sintesis.print.html",
        "title": "Lo que la evidencia muestra hasta ahora",
        "subtitle": "— en el contexto de <em>La Trilogía del Campo</em>",
        "byline": "José Gude, MD",
        "tagline": "Un ensayo de síntesis · física · biología · computación",
        "toc_label": "Índice",
        "section_label": "Sección",
        "colophon_intro": 'Este folleto reúne el ensayo de síntesis publicado en <a href="{base}/the-evidence.html">josegudemd.com</a> en un único volumen tipográfico.',
        "colophon_set": "Compuesto en Libre Baskerville a 10,5 pt sobre 1,55, en formato 6 × 9 pulgadas.",
        "colophon_hdr": "Titulares de sección y marcadores en Inter.",
        "colophon_companion": "Acompaña a <em>La Trilogía del Campo</em>: <em>Anima</em> · <em>Numen</em> · <em>Limen</em>, y a la novela autónoma <em>Luz Frágil</em>.",
        "colophon_seal": "Colofón",
        "ident": "josegudemd-sintesis-2026-es",
        "lang_iso": "es",
        "preface_title": "Prefacio",
        "closing_title": "Si has llegado hasta aquí",
        "metadata_desc": "Un ensayo de síntesis: cómo los fundamentos cuánticos, la física a escala de Planck, la neurología anómala y la teoría de la información convergen en la tesis central de La Trilogía del Campo.",
    }
}


def build_edition(cfg):
    src = ROOT / cfg["source"]
    if not src.exists():
        print(f"  [skip] source missing: {src}")
        return
    body = extract_main(src)
    hero_html, chapters, closing = split_into_sections(body)

    print(f"[{cfg['lang_iso']}] hero + {len(chapters)} sections + {'closing' if closing else 'no closing'}")

    print_html = build_print_html(chapters, hero_html, closing, cfg["base_url"], cfg)
    pdf_out = DIST / cfg["pdf_name"]
    build_pdf(print_html, pdf_out)
    html_out = DIST / cfg["html_name"]
    html_out.write_text(print_html, encoding="utf-8")
    print(f"  print HTML: {html_out}")

    epub_out = DIST / cfg["epub_name"]
    build_epub(chapters, hero_html, closing, cfg["base_url"], epub_out, cfg)


def main():
    for lang, cfg in EDITIONS.items():
        build_edition(cfg)


if __name__ == "__main__":
    main()
