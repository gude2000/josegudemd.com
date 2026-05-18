#!/usr/bin/env python3
"""
build_book_og_images.py — generate per-book Open Graph / Twitter share
images (1200×630). Each card composes the actual book cover on the left
with title, tagline, author, and series mark on the right.

Outputs:
  assets/img/og-anima.jpg
  assets/img/og-numen.jpg
  assets/img/og-limen.jpg
  assets/img/og-fragile-light.jpg

Each book has its own accent color matching the site palette.
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "assets" / "img"
COVER_DIR = ROOT / "assets" / "img"

W, H = 1200, 630
BG       = (10, 14, 26)        # #0a0e1a
GOLD     = (218, 160, 85)      # #daa055
CREAM    = (232, 224, 206)     # #e8e0ce
CREAM_DIM= (185, 176, 155)     # #b9b09b

# English book OG cards
BOOKS = [
    {
        "slug":     "anima",
        "cover":    "anima-cover.jpg",
        "out":      "og-anima.jpg",
        "title":    "Anima",
        "subtitle": "A Novel",
        "eyebrow":  "B O O K   O N E   ·   T H E   F I E L D   T R I L O G Y",
        "tagline1": "The folder of edge cases.",
        "tagline2": "Patients who refused the rules.",
        "accent":   (218, 160, 85),    # gold
        "accent_soft": (196, 140, 66),
    },
    {
        "slug":     "numen",
        "cover":    "numen-cover.jpg",
        "out":      "og-numen.jpg",
        "title":    "Numen",
        "subtitle": "A Novel",
        "eyebrow":  "B O O K   T W O   ·   T H E   F I E L D   T R I L O G Y",
        "tagline1": "The journal José left for Alex.",
        "tagline2": "What a father passes on.",
        "accent":   (210, 170, 110),   # warmer cream-gold
        "accent_soft": (188, 150, 88),
    },
    {
        "slug":     "limen",
        "cover":    "limen-cover.jpg",
        "out":      "og-limen.jpg",
        "title":    "Limen",
        "subtitle": "The Field Compendium",
        "eyebrow":  "B O O K   T H R E E   ·   T H E   F I E L D   T R I L O G Y",
        "tagline1": "The convergence is the argument.",
        "tagline2": "The field made visible.",
        "accent":   (95, 175, 175),    # teal — book design accent
        "accent_soft": (75, 145, 145),
    },
    {
        "slug":     "fragile-light",
        "cover":    "fragile-light-cover.jpg",
        "out":      "og-fragile-light.jpg",
        "title":    "Fragile Light",
        "subtitle": "The Voluntarist Wager",
        "eyebrow":  "S T A N D A L O N E   ·   J O S É   G U D E   M D",
        "tagline1": "Freedom did not lose.",
        "tagline2": "Freedom was interrupted.",
        "accent":   (224, 180, 110),   # warm light
        "accent_soft": (200, 156, 88),
    },
]

FONT_CANDIDATES_SERIF_ITALIC = [
    "/System/Library/Fonts/Supplemental/Times New Roman Italic.ttf",
    "/System/Library/Fonts/NewYorkItalic.ttf",
    "/Library/Fonts/Times New Roman Italic.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
]
FONT_CANDIDATES_SERIF = [
    "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
    "/System/Library/Fonts/NewYork.ttf",
    "/Library/Fonts/Times New Roman.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
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


def fit_cover(cover_path: Path, target_h: int) -> Image.Image:
    """Open the cover and resize to target height keeping aspect ratio."""
    cover = Image.open(cover_path).convert("RGB")
    cw, ch = cover.size
    new_w = int(cw * target_h / ch)
    return cover.resize((new_w, target_h), Image.LANCZOS)


def build_one(book: dict) -> None:
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # ---- Left side: book cover ----
    cover_path = COVER_DIR / book["cover"]
    cover_h = 500
    cover = fit_cover(cover_path, cover_h)
    cover_x = 70
    cover_y = (H - cover_h) // 2  # vertical center

    # Soft shadow behind the cover
    shadow = Image.new("RGB", cover.size, (0, 0, 0))
    shadow_mask = Image.new("L", cover.size, 0)
    sd = ImageDraw.Draw(shadow_mask)
    sd.rectangle([0, 0, cover.size[0], cover.size[1]], fill=160)
    shadow_mask = shadow_mask.filter(ImageFilter.GaussianBlur(18))
    img.paste(shadow, (cover_x + 14, cover_y + 18), shadow_mask)

    img.paste(cover, (cover_x, cover_y))

    # Thin accent border along the right edge of the cover
    accent = book["accent"]
    draw.line(
        [(cover_x + cover.size[0], cover_y),
         (cover_x + cover.size[0], cover_y + cover_h)],
        fill=accent, width=2
    )

    # ---- Right side: type ----
    text_x = cover_x + cover.size[0] + 60
    text_w = W - text_x - 60

    # Eyebrow
    eyebrow_font = pick_font(FONT_CANDIDATES_SANS, 18)
    draw.text((text_x, 80), book["eyebrow"], fill=accent, font=eyebrow_font)

    # Accent rule below eyebrow
    draw.line([(text_x, 118), (text_x + 100, 118)],
              fill=book["accent_soft"], width=2)

    # Title — serif italic, large
    title_font = pick_font(FONT_CANDIDATES_SERIF_ITALIC, 96)
    draw.text((text_x, 145), book["title"], fill=CREAM, font=title_font)

    # Subtitle
    subtitle_font = pick_font(FONT_CANDIDATES_SANS, 28)
    title_bbox = draw.textbbox((text_x, 145), book["title"], font=title_font)
    sub_y = title_bbox[3] + 12
    draw.text((text_x, sub_y), book["subtitle"], fill=CREAM_DIM, font=subtitle_font)

    # Tagline (two lines, serif italic)
    tag_font = pick_font(FONT_CANDIDATES_SERIF_ITALIC, 32)
    tag_y = sub_y + 70
    draw.text((text_x, tag_y), book["tagline1"], fill=CREAM, font=tag_font)
    draw.text((text_x, tag_y + 44), book["tagline2"], fill=CREAM_DIM, font=tag_font)

    # Footer — author + URL
    foot_font = pick_font(FONT_CANDIDATES_SERIF_ITALIC, 26)
    url_font  = pick_font(FONT_CANDIDATES_SANS, 20)
    draw.text((text_x, H - 90), "José Gude MD", fill=CREAM, font=foot_font)
    draw.text((text_x, H - 55), "josegudemd.com", fill=accent, font=url_font)

    # ---- Save ----
    out_path = OUT_DIR / book["out"]
    img.save(out_path, "JPEG", quality=88, optimize=True, progressive=True)
    print(f"Wrote {out_path.name}  ({out_path.stat().st_size / 1024:.1f} KB)")


BOOKS_ES = [
    {
        "slug":     "anima-es",
        "cover":    "anima-cover-es.jpg",
        "out":      "og-anima-es.jpg",
        "title":    "Anima",
        "subtitle": "Una novela",
        "eyebrow":  "L I B R O   U N O   ·   L A   T R I L O G Í A   D E L   C A M P O",
        "tagline1": "La carpeta de casos límite.",
        "tagline2": "Pacientes que rompieron las reglas.",
        "accent":   (218, 160, 85),
        "accent_soft": (196, 140, 66),
    },
    {
        "slug":     "numen-es",
        "cover":    "numen-cover-es.jpg",
        "out":      "og-numen-es.jpg",
        "title":    "Numen",
        "subtitle": "Una novela",
        "eyebrow":  "L I B R O   D O S   ·   L A   T R I L O G Í A   D E L   C A M P O",
        "tagline1": "El diario que José dejó a Alex.",
        "tagline2": "Lo que un padre transmite.",
        "accent":   (210, 170, 110),
        "accent_soft": (188, 150, 88),
    },
    {
        "slug":     "limen-es",
        "cover":    "limen-cover.jpg",
        "out":      "og-limen-es.jpg",
        "title":    "Limen",
        "subtitle": "El compendio del campo",
        "eyebrow":  "L I B R O   T R E S   ·   L A   T R I L O G Í A   D E L   C A M P O",
        "tagline1": "La convergencia es el argumento.",
        "tagline2": "El campo hecho visible.",
        "accent":   (95, 175, 175),
        "accent_soft": (75, 145, 145),
    },
    {
        "slug":     "fragile-light-es",
        "cover":    "fragile-light-cover-es.jpg",
        "out":      "og-fragile-light-es.jpg",
        "title":    "Luz Frágil",
        "subtitle": "La apuesta voluntarista",
        "eyebrow":  "I N D E P E N D I E N T E   ·   J O S É   G U D E   M D",
        "tagline1": "La libertad no perdió.",
        "tagline2": "La libertad fue interrumpida.",
        "accent":   (224, 180, 110),
        "accent_soft": (200, 156, 88),
    },
]


def build():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for book in BOOKS + BOOKS_ES:
        build_one(book)


if __name__ == "__main__":
    build()
