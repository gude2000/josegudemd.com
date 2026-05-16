#!/usr/bin/env python3
"""
build_og_image.py — generate the default Open Graph / Twitter share image
for josegudemd.com. 1200x630 px (Facebook/X recommended), brand palette,
title + tagline + a small Webb-triangle vector.

Output: assets/img/og-default.jpg
"""
from __future__ import annotations
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "img" / "og-default.jpg"

W, H = 1200, 630
BG       = (10, 14, 26)        # #0a0e1a
GOLD     = (218, 160, 85)      # #daa055
GOLD_SOFT= (196, 140, 66)      # #c48c42
CREAM    = (232, 224, 206)     # #e8e0ce
CREAM_DIM= (185, 176, 155)     # #b9b09b

# Try macOS-friendly font paths, falling back to Linux paths and finally
# PIL's default if nothing works.
FONT_CANDIDATES_SERIF = [
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


def build():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Subtle radial vignette (cheap)
    cx, cy = W // 2, H // 2
    for r in range(0, 480, 24):
        alpha = int(8 * (1 - r / 480))
        # approximate by darkening corners — skipped, BG already dark enough

    # --- Webb-triangle vector on the right side ---
    # 34.38° · 55.62° · 90° right triangle, sides 1 : φ, fitted around (900, 315)
    PHI = (1 + math.sqrt(5)) / 2
    base_x = 950
    base_y = 380
    leg_long  = 220                       # horizontal leg (the φ leg)
    leg_short = leg_long / PHI            # vertical leg
    # Vertices (90° at lower-left of triangle area)
    A = (base_x - leg_long / 2, base_y + leg_short / 2)            # 90° corner — lower-left
    B = (base_x + leg_long / 2, base_y + leg_short / 2)            # 34.38° — lower-right
    C = (base_x - leg_long / 2, base_y - leg_short / 2)            # 55.62° — upper-left

    # Recursive nested similar triangles (3 levels deep)
    def draw_triangle(p_right, p_top, p_bot, depth, alpha_scale):
        col = (
            int(GOLD[0] * alpha_scale + BG[0] * (1 - alpha_scale)),
            int(GOLD[1] * alpha_scale + BG[1] * (1 - alpha_scale)),
            int(GOLD[2] * alpha_scale + BG[2] * (1 - alpha_scale)),
        )
        draw.line([p_right, p_top, p_bot, p_right], fill=col, width=2)
        if depth <= 0:
            return
        # Inner self-similar triangle: scale by 1/φ around p_right (the 90° corner)
        scale = 1 / PHI
        def lerp(a, b, t):
            return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        # Foot of altitude from the right-angle vertex to the hypotenuse divides
        # the original triangle into two smaller similar ones; we draw the
        # smaller of the two as the nested.
        new_right = lerp(p_right, p_top, scale)
        new_top   = p_top
        new_bot   = lerp(p_right, p_bot, scale * 0)  # collapses; use a cleaner self-similar
        # Simpler nesting: just scale the whole triangle by 1/phi around centroid
        cx2 = (p_right[0] + p_top[0] + p_bot[0]) / 3
        cy2 = (p_right[1] + p_top[1] + p_bot[1]) / 3
        def scale_pt(p):
            return (cx2 + (p[0] - cx2) / PHI, cy2 + (p[1] - cy2) / PHI)
        draw_triangle(scale_pt(p_right), scale_pt(p_top), scale_pt(p_bot),
                      depth - 1, alpha_scale * 0.72)

    draw_triangle(A, C, B, depth=3, alpha_scale=0.95)

    # Angle markers — tiny gold arcs (just dots, simplest)
    def angle_dot(p, radius=4):
        draw.ellipse([p[0]-radius, p[1]-radius, p[0]+radius, p[1]+radius],
                     fill=CREAM)
    angle_dot(A)
    angle_dot(B)
    angle_dot(C)

    # --- Title / type on the left ---
    title_font = pick_font(FONT_CANDIDATES_SERIF, 88)
    name_font  = pick_font(FONT_CANDIDATES_SERIF, 54)
    sub_font   = pick_font(FONT_CANDIDATES_SANS, 28)
    small_font = pick_font(FONT_CANDIDATES_SANS, 22)

    # Eyebrow (small letter-spaced tag)
    draw.text((90, 110), "T H E   F I E L D   T R I L O G Y", fill=GOLD, font=small_font)

    # Author name
    draw.text((90, 170), "José Gude MD", fill=CREAM, font=name_font)

    # Series titles
    draw.text((90, 270), "Anima · Numen · Limen", fill=CREAM_DIM, font=sub_font)
    draw.text((90, 308), "Fragile Light", fill=CREAM_DIM, font=sub_font)

    # Tagline
    tagline = "Receiver-model consciousness ·"
    tagline2 = "the chord that refuses to resolve"
    draw.text((90, 420), tagline, fill=CREAM, font=sub_font)
    draw.text((90, 454), tagline2, fill=CREAM, font=sub_font)

    # Footer URL
    draw.text((90, 540), "josegudemd.com", fill=GOLD, font=small_font)

    # Save as JPEG at high quality
    img.save(OUT, "JPEG", quality=88, optimize=True, progressive=True)
    print(f"Wrote {OUT}  ({OUT.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    build()
