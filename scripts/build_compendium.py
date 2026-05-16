#!/usr/bin/env python3
"""
build_compendium.py — generate a printable PDF of the full bibliography
from reading.html. Run from the repo root:

    python3 scripts/build_compendium.py

Outputs: assets/compendium.pdf
"""
from __future__ import annotations
import re
import sys
import html
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString, Tag
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether,
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import date

# ---------- font registration ----------
# Helvetica (the default) is Latin-1 only — no φ, no ↗, no chord glyphs. We
# register DejaVu Sans (Unicode-capable, ships with most Linux/Mac systems)
# so the bibliography renders correctly.

FONT_CANDIDATES = {
    "regular": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/DejaVuSans.ttf",
        "/Library/Fonts/DejaVuSans.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ],
    "bold": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/DejaVuSans-Bold.ttf",
        "/Library/Fonts/DejaVuSans-Bold.ttf",
    ],
    "italic": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
        "/System/Library/Fonts/Supplemental/DejaVuSans-Oblique.ttf",
        "/Library/Fonts/DejaVuSans-Oblique.ttf",
    ],
    "bolditalic": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf",
        "/System/Library/Fonts/Supplemental/DejaVuSans-BoldOblique.ttf",
        "/Library/Fonts/DejaVuSans-BoldOblique.ttf",
    ],
}


def _pick(paths):
    for p in paths:
        if Path(p).exists():
            return p
    return None


def register_fonts():
    reg = _pick(FONT_CANDIDATES["regular"])
    bold = _pick(FONT_CANDIDATES["bold"])
    italic = _pick(FONT_CANDIDATES["italic"])
    bi = _pick(FONT_CANDIDATES["bolditalic"])
    if not reg:
        print("[warn] DejaVu Sans not found — falling back to Helvetica (Unicode glyphs will render as boxes)", file=sys.stderr)
        return ("Helvetica", "Helvetica-Bold", "Helvetica-Oblique", "Helvetica-BoldOblique")
    pdfmetrics.registerFont(TTFont("BodySans", reg))
    pdfmetrics.registerFont(TTFont("BodySans-Bold", bold or reg))
    pdfmetrics.registerFont(TTFont("BodySans-Italic", italic or reg))
    pdfmetrics.registerFont(TTFont("BodySans-BoldItalic", bi or italic or reg))
    pdfmetrics.registerFontFamily(
        "BodySans",
        normal="BodySans",
        bold="BodySans-Bold",
        italic="BodySans-Italic",
        boldItalic="BodySans-BoldItalic",
    )
    return ("BodySans", "BodySans-Bold", "BodySans-Italic", "BodySans-BoldItalic")

# ---------- paths ----------
ROOT = Path(__file__).resolve().parent.parent
READING_HTML = ROOT / "reading.html"
OUT_PDF = ROOT / "assets" / "compendium.pdf"

# ---------- color palette (matches site) ----------
GOLD = HexColor("#daa055")
GOLD_SOFT = HexColor("#c48c42")
CREAM = HexColor("#2c2820")  # darker for print legibility
CREAM_DIM = HexColor("#5a5448")
RULE = HexColor("#a89980")
LINK = HexColor("#8a6a30")


# ---------- HTML → ReportLab paragraph markup ----------
def to_reportlab_inline(node) -> str:
    """Convert a BeautifulSoup tree (or string) to ReportLab inline markup.
    Supports <a>, <em>, <i>, <strong>, <b>, &middot;, &amp;. Strips footnote
    arrows and the per-entry 'Read the explainer' tails (those link to
    site-relative pages that won't resolve in a PDF)."""
    if isinstance(node, NavigableString):
        return html.escape(str(node))
    out = []
    for child in node.children:
        if isinstance(child, NavigableString):
            out.append(html.escape(str(child)))
        elif isinstance(child, Tag):
            name = child.name.lower()
            inner = to_reportlab_inline(child)
            if name == "a":
                href = child.get("href", "")
                # Drop site-internal explainer links; keep external (http/https) ones
                if href.startswith("http"):
                    out.append(f'<a href="{html.escape(href)}" color="#8a6a30">{inner}</a>')
                else:
                    # internal site link — keep the visible text only
                    out.append(inner)
            elif name in ("em", "i"):
                out.append(f"<i>{inner}</i>")
            elif name in ("strong", "b"):
                out.append(f"<b>{inner}</b>")
            elif name == "br":
                out.append("<br/>")
            else:
                out.append(inner)
    return "".join(out)


def strip_explainer_tail(text: str) -> str:
    """Remove the 'Read the explainer →' style tails that are site-internal."""
    # The note typically ends with a sentence linking to a per-entry page.
    # Cut off at "Read the explainer" / "→" patterns.
    cut_patterns = [
        r"\s*Read the explainer.*?→\s*$",
        r"\s*Read the explainer.*?$",
    ]
    for pat in cut_patterns:
        text = re.sub(pat, "", text, flags=re.S)
    return text.strip()




# ---------- styles ----------
def make_styles(reg, bold, italic, bi):
    base = getSampleStyleSheet()
    return {
        "TitleBig": ParagraphStyle(
            "TitleBig", parent=base["Title"],
            fontName=bold, fontSize=28, leading=34,
            textColor=GOLD, alignment=TA_CENTER, spaceAfter=10,
        ),
        "Subtitle": ParagraphStyle(
            "Subtitle", parent=base["Normal"],
            fontName=reg, fontSize=12, leading=16,
            textColor=CREAM_DIM, alignment=TA_CENTER, spaceAfter=4,
        ),
        "TitleMeta": ParagraphStyle(
            "TitleMeta", parent=base["Normal"],
            fontName=italic, fontSize=10, leading=14,
            textColor=CREAM_DIM, alignment=TA_CENTER,
        ),
        "TOCEntry": ParagraphStyle(
            "TOCEntry", parent=base["Normal"],
            fontName=reg, fontSize=11, leading=18,
            textColor=CREAM, leftIndent=12,
        ),
        "SectionH": ParagraphStyle(
            "SectionH", parent=base["Heading2"],
            fontName=bold, fontSize=14, leading=18,
            textColor=GOLD_SOFT, spaceBefore=12, spaceAfter=4,
        ),
        "SectionIntro": ParagraphStyle(
            "SectionIntro", parent=base["Italic"],
            fontName=italic, fontSize=10, leading=14,
            textColor=CREAM_DIM, spaceAfter=10,
        ),
        "EntryTitle": ParagraphStyle(
            "EntryTitle", parent=base["Normal"],
            fontName=bold, fontSize=10.5, leading=14,
            textColor=CREAM, spaceBefore=8, spaceAfter=1,
        ),
        "EntryAuthor": ParagraphStyle(
            "EntryAuthor", parent=base["Normal"],
            fontName=italic, fontSize=10, leading=13,
            textColor=CREAM_DIM, spaceAfter=2,
        ),
        "EntryNote": ParagraphStyle(
            "EntryNote", parent=base["Normal"],
            fontName=reg, fontSize=10, leading=13.5,
            textColor=CREAM, alignment=TA_JUSTIFY, spaceAfter=4,
            leftIndent=10,
        ),
    }


# ---------- page chrome ----------
def on_page(canvas_obj: canvas.Canvas, doc):
    canvas_obj.saveState()
    w, h = LETTER
    footer_font = "BodySans" if "BodySans" in pdfmetrics.getRegisteredFontNames() else "Helvetica"
    canvas_obj.setFont(footer_font, 8)
    canvas_obj.setFillColor(CREAM_DIM)
    # left footer: site
    canvas_obj.drawString(0.75 * inch, 0.5 * inch,
                          "josegudemd.com  ·  Reading & References compendium")
    # right footer: page number
    canvas_obj.drawRightString(w - 0.75 * inch, 0.5 * inch,
                               f"{doc.page}")
    canvas_obj.restoreState()


# ---------- build ----------
def build():
    soup = BeautifulSoup(READING_HTML.read_text(encoding="utf-8"), "lxml")
    sections = soup.select("section.ref-section")
    if not sections:
        print("No ref-sections found. Aborting.", file=sys.stderr)
        sys.exit(1)

    reg, bold, italic, bi = register_fonts()
    styles = make_styles(reg, bold, italic, bi)
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT_PDF),
        pagesize=LETTER,
        leftMargin=0.85 * inch,
        rightMargin=0.85 * inch,
        topMargin=0.85 * inch,
        bottomMargin=0.85 * inch,
        title="Reading & References — Field Trilogy Compendium",
        author="José Gude MD",
        subject="Bibliography for the Field Trilogy (Anima, Numen, Limen, Fragile Light)",
    )

    story = []

    # ---- Title page ----
    story.append(Spacer(1, 1.6 * inch))
    story.append(Paragraph("Reading &amp; References", styles["TitleBig"]))
    story.append(Paragraph("A compendium for the Field Trilogy", styles["Subtitle"]))
    story.append(Spacer(1, 0.25 * inch))
    story.append(Paragraph(
        "Anima &nbsp;·&nbsp; Numen &nbsp;·&nbsp; Limen &nbsp;·&nbsp; Fragile Light",
        styles["Subtitle"]))
    story.append(Spacer(1, 1.8 * inch))
    story.append(Paragraph(
        f"Compiled {date.today():%B %Y} &nbsp;·&nbsp; josegudemd.com",
        styles["TitleMeta"]))
    story.append(PageBreak())

    # ---- Contents ----
    story.append(Paragraph("Contents", styles["SectionH"]))
    story.append(Spacer(1, 6))
    for idx, sec in enumerate(sections, 1):
        h3 = sec.find("h3")
        if not h3:
            continue
        title_html = to_reportlab_inline(h3)
        story.append(Paragraph(f"{idx}.&nbsp;&nbsp;{title_html}", styles["TOCEntry"]))
    story.append(PageBreak())

    # ---- Sections ----
    for idx, sec in enumerate(sections, 1):
        h3 = sec.find("h3")
        if not h3:
            continue
        title_html = to_reportlab_inline(h3)
        story.append(Paragraph(f"{idx}.&nbsp;&nbsp;{title_html}", styles["SectionH"]))

        # Optional intro paragraph immediately after h3
        intro = h3.find_next_sibling()
        if intro and intro.name == "p" and "dim" in (intro.get("class") or []):
            story.append(Paragraph(to_reportlab_inline(intro), styles["SectionIntro"]))

        for li in sec.select("ul.ref-list > li"):
            title_span = li.find("span", class_="ref-title")
            author_span = li.find("span", class_="ref-author")
            note_div = li.find("div", class_="ref-note")

            parts = []
            if title_span:
                parts.append(Paragraph(to_reportlab_inline(title_span),
                                       styles["EntryTitle"]))
            if author_span:
                parts.append(Paragraph(to_reportlab_inline(author_span),
                                       styles["EntryAuthor"]))
            if note_div:
                note_html = to_reportlab_inline(note_div)
                note_html = strip_explainer_tail(note_html)
                parts.append(Paragraph(note_html, styles["EntryNote"]))

            if parts:
                # KeepTogether so an entry doesn't split awkwardly across pages
                story.append(KeepTogether(parts))

        story.append(Spacer(1, 12))

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"Wrote {OUT_PDF}  ({OUT_PDF.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    build()
