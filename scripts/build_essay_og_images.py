#!/usr/bin/env python3
"""
build_essay_og_images.py — generate per-essay Open Graph / Twitter share
images (1200×630) for the three companion essays. Typographic cards in
the brand palette, with a small symbolic mark.

Outputs:
  assets/img/og-glitches.jpg          assets/img/og-glitches-es.jpg
  assets/img/og-simulation.jpg        assets/img/og-simulation-es.jpg
  assets/img/og-wave.jpg              assets/img/og-wave-es.jpg
"""
from __future__ import annotations
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "assets" / "img"

W, H = 1200, 630
BG       = (10, 14, 26)        # #0a0e1a
GOLD     = (218, 160, 85)      # #daa055
CREAM    = (232, 224, 206)     # #e8e0ce
CREAM_DIM= (185, 176, 155)     # #b9b09b
TEAL     = (95, 175, 175)
WARM     = (224, 180, 110)

ESSAYS = [
    # Glitches in Reality
    {
        "out": "og-glitches.jpg",
        "eyebrow": "T H E   F I E L D   T R I L O G Y   ·   R E A D I N G",
        "title": "Glitches in Reality",
        "subtitle": "Ten anomalies physics cannot explain",
        "tag1": "Double-slit · entanglement · time dilation",
        "tag2": "dark matter · CMB anomalies · black holes",
        "accent": GOLD,
        "mark": "anomaly",
    },
    {
        "out": "og-glitches-es.jpg",
        "eyebrow": "L A   T R I L O G Í A   D E L   C A M P O   ·   L E C T U R A S",
        "title": "Fallos en la realidad",
        "subtitle": "Diez anomalías que la física no puede explicar",
        "tag1": "Doble rendija · entrelazamiento · dilatación del tiempo",
        "tag2": "materia oscura · CMB · agujeros negros",
        "accent": GOLD,
        "mark": "anomaly",
    },
    # Simulation Hypothesis
    {
        "out": "og-simulation.jpg",
        "eyebrow": "T H E   F I E L D   T R I L O G Y   ·   R E A D I N G",
        "title": "The Simulation Hypothesis",
        "subtitle": "The Evidence",
        "tag1": "Holographic principle · Gates' codes · Bostrom",
        "tag2": "Tegmark · Wheeler · the universe as computation",
        "accent": TEAL,
        "mark": "grid",
    },
    {
        "out": "og-simulation-es.jpg",
        "eyebrow": "L A   T R I L O G Í A   D E L   C A M P O   ·   L E C T U R A S",
        "title": "La hipótesis de la simulación",
        "subtitle": "La evidencia",
        "tag1": "Principio holográfico · Gates · Bostrom",
        "tag2": "Tegmark · Wheeler · el universo como computación",
        "accent": TEAL,
        "mark": "grid",
    },
    # What Does the Wave Wave On?
    {
        "out": "og-wave.jpg",
        "eyebrow": "T H E   F I E L D   T R I L O G Y   ·   R E A D I N G",
        "title": "What Does the Wave Wave On?",
        "subtitle": "The medium problem in quantum mechanics",
        "tag1": "Copenhagen · Bohm's pilot wave · Many-Worlds",
        "tag2": "QFT · Tegmark · objective collapse",
        "accent": WARM,
        "mark": "wave",
    },
    {
        "out": "og-wave-es.jpg",
        "eyebrow": "L A   T R I L O G Í A   D E L   C A M P O   ·   L E C T U R A S",
        "title": "¿Sobre qué onda la onda?",
        "subtitle": "El problema del medio en mecánica cuántica",
        "tag1": "Copenhague · onda piloto de Bohm · Muchos Mundos",
        "tag2": "TCC · Tegmark · colapso objetivo",
        "accent": WARM,
        "mark": "wave",
    },
    # Stevenson archive (pre-birth memory)
    {
        "out": "og-stevenson.jpg",
        "eyebrow": "T H E   F I E L D   T R I L O G Y   ·   R E A D I N G",
        "title": "The Stevenson Archive",
        "subtitle": "Pre-birth memory — forty years of cases",
        "tag1": "UVA Division of Perceptual Studies · Tucker",
        "tag2": "2,500 cases · birthmarks · Edwards · Braude",
        "accent": GOLD,
        "mark": "anomaly",
    },
    {
        "out": "og-stevenson-es.jpg",
        "eyebrow": "L A   T R I L O G Í A   D E L   C A M P O   ·   L E C T U R A S",
        "title": "El archivo Stevenson",
        "subtitle": "Memoria prenatal — cuarenta años de casos",
        "tag1": "División de Estudios Perceptuales UVA · Tucker",
        "tag2": "2.500 casos · marcas de nacimiento · Edwards · Braude",
        "accent": GOLD,
        "mark": "anomaly",
    },
    # Eckhart, the Cloud, and the Kabbalah
    {
        "out": "og-eckhart.jpg",
        "eyebrow": "T H E   F I E L D   T R I L O G Y   ·   R E A D I N G",
        "title": "Eckhart, the Cloud, and the Kabbalah",
        "subtitle": "Western contemplative traditions on the divine spark",
        "tag1": "Pseudo-Dionysius · Meister Eckhart · the Cloud",
        "tag2": "Lurianic Kabbalah · the five soul-levels",
        "accent": CREAM,
        "mark": "wave",
    },
    {
        "out": "og-eckhart-es.jpg",
        "eyebrow": "L A   T R I L O G Í A   D E L   C A M P O   ·   L E C T U R A S",
        "title": "Eckhart, la Nube y la Cábala",
        "subtitle": "Tradiciones contemplativas occidentales — la chispa divina",
        "tag1": "Pseudo-Dionisio · Meister Eckhart · la Nube",
        "tag2": "Cábala luriánica · los cinco niveles del alma",
        "accent": CREAM,
        "mark": "wave",
    },
    # Death and Dying
    {
        "out": "og-death-and-dying.jpg",
        "eyebrow": "T H E   F I E L D   T R I L O G Y   ·   R E A D I N G",
        "title": "Death and Dying",
        "subtitle": "A physician's notes on presence at the bedside",
        "tag1": "Quiet presence · attention · honoring the life",
        "tag2": "Withholding judgement · awe · acceptance",
        "accent": TEAL,
        "mark": "wave",
    },
    {
        "out": "og-death-and-dying-es.jpg",
        "eyebrow": "L A   T R I L O G Í A   D E L   C A M P O   ·   L E C T U R A S",
        "title": "Muerte y morir",
        "subtitle": "Notas de un médico sobre la presencia junto a la cabecera",
        "tag1": "Presencia silenciosa · atención · honrar la vida",
        "tag2": "Retener el juicio · asombro · aceptación",
        "accent": TEAL,
        "mark": "wave",
    },
    # A Clinical Life
    {
        "out": "og-a-clinical-life.jpg",
        "eyebrow": "T H E   F I E L D   T R I L O G Y   ·   R E A D I N G",
        "title": "A Clinical Life",
        "subtitle": "Thirty years at the bedside — and the case that opened the door",
        "tag1": "Medical school · internship · residency",
        "tag2": "Moral injury · the art of medicine · Mary Parker",
        "accent": WARM,
        "mark": "anomaly",
    },
    {
        "out": "og-a-clinical-life-es.jpg",
        "eyebrow": "L A   T R I L O G Í A   D E L   C A M P O   ·   L E C T U R A S",
        "title": "Una vida clínica",
        "subtitle": "Treinta años junto a la cabecera — el caso que abrió la puerta",
        "tag1": "Facultad de medicina · internado · residencia",
        "tag2": "Daño moral · el arte de la medicina · Mary Parker",
        "accent": WARM,
        "mark": "anomaly",
    },
    # Terminal Lucidity
    {
        "out": "og-terminal-lucidity.jpg",
        "eyebrow": "T H E   F I E L D   T R I L O G Y   ·   R E A D I N G",
        "title": "Terminal Lucidity",
        "subtitle": "The empirical literature and what the framework reads",
        "tag1": "Nahm · Greyson · Happich · the 2012 collection",
        "tag2": "Chawla · Borjigin · Mashour 2019 · Batthyány",
        "accent": GOLD,
        "mark": "anomaly",
    },
    {
        "out": "og-terminal-lucidity-es.jpg",
        "eyebrow": "L A   T R I L O G Í A   D E L   C A M P O   ·   L E C T U R A S",
        "title": "Lucidez terminal",
        "subtitle": "La literatura empírica y lo que el marco lee",
        "tag1": "Nahm · Greyson · Happich · la colección de 2012",
        "tag2": "Chawla · Borjigin · Mashour 2019 · Batthyány",
        "accent": GOLD,
        "mark": "anomaly",
    },
]

FONT_CANDIDATES_SERIF_ITALIC = [
    "/System/Library/Fonts/Supplemental/Times New Roman Italic.ttf",
    "/System/Library/Fonts/NewYorkItalic.ttf",
    "/Library/Fonts/Times New Roman Italic.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
]
FONT_CANDIDATES_SANS = [
    "/System/Library/Fonts/Supplemental/Helvetica.ttc",
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Helvetica.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]


def pick_font(candidates, size):
    for p in candidates:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def draw_mark(draw: ImageDraw.ImageDraw, mark: str, accent):
    """A small symbolic mark in the upper-right corner of the card."""
    cx, cy = 1040, 130
    if mark == "anomaly":
        # Broken circle — symbol of a glitch
        for ang_start, ang_end in [(0, 80), (110, 200), (230, 350)]:
            draw.arc([cx - 50, cy - 50, cx + 50, cy + 50],
                     start=ang_start, end=ang_end,
                     fill=accent, width=3)
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=accent)
    elif mark == "grid":
        # Pixel grid — symbol of digital/computational
        for i in range(4):
            for j in range(4):
                x = cx - 50 + i * 26
                y = cy - 50 + j * 26
                fill = accent if (i + j) % 2 == 0 else None
                draw.rectangle([x, y, x + 18, y + 18],
                               outline=accent, width=1, fill=fill)
    elif mark == "wave":
        # Sine wave — symbol of the wave function
        pts = []
        for t in range(0, 121):
            x = cx - 60 + t
            y = cy + int(24 * math.sin(t * math.pi * 2 / 60))
            pts.append((x, y))
        for i in range(len(pts) - 1):
            draw.line([pts[i], pts[i + 1]], fill=accent, width=3)


def build_one(essay: dict) -> None:
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    accent = essay["accent"]

    # Top eyebrow
    eyebrow_font = pick_font(FONT_CANDIDATES_SANS, 18)
    draw.text((80, 80), essay["eyebrow"], fill=accent, font=eyebrow_font)
    draw.line([(80, 118), (220, 118)], fill=accent, width=2)

    # Mark on the right
    draw_mark(draw, essay["mark"], accent)

    # Title — serif italic. Size adapts to title length so long titles
    # (e.g. "What Does the Wave Wave On?") don't get clipped.
    title_text = essay["title"]
    if len(title_text) > 28:
        title_size = 58
    elif len(title_text) > 22:
        title_size = 68
    else:
        title_size = 76
    title_font = pick_font(FONT_CANDIDATES_SERIF_ITALIC, title_size)
    draw.text((80, 175), title_text, fill=CREAM, font=title_font)

    # Subtitle
    title_bbox = draw.textbbox((80, 175), essay["title"], font=title_font)
    sub_y = title_bbox[3] + 14
    sub_font = pick_font(FONT_CANDIDATES_SANS, 28)
    draw.text((80, sub_y), essay["subtitle"], fill=CREAM_DIM, font=sub_font)

    # Two-line tag content
    tag_font = pick_font(FONT_CANDIDATES_SERIF_ITALIC, 26)
    tag_y = sub_y + 75
    draw.text((80, tag_y), essay["tag1"], fill=CREAM, font=tag_font)
    draw.text((80, tag_y + 38), essay["tag2"], fill=CREAM_DIM, font=tag_font)

    # Footer — author + URL
    foot_font = pick_font(FONT_CANDIDATES_SERIF_ITALIC, 26)
    url_font  = pick_font(FONT_CANDIDATES_SANS, 20)
    draw.text((80, H - 90), "José Gude MD", fill=CREAM, font=foot_font)
    draw.text((80, H - 55), "josegudemd.com", fill=accent, font=url_font)

    out_path = OUT_DIR / essay["out"]
    img.save(out_path, "JPEG", quality=88, optimize=True, progressive=True)
    print(f"Wrote {out_path.name}  ({out_path.stat().st_size / 1024:.1f} KB)")


def build():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for essay in ESSAYS:
        build_one(essay)


if __name__ == "__main__":
    build()
