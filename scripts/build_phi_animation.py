#!/usr/bin/env python3
"""
build_phi_animation.py — render the φ-rectangles + spiral construction
as a short MP4 video for share-friendly contexts (Twitter, etc).

Output: assets/video/phi-rectangles.mp4  (~720p, ~10 s, ~1–2 MB)

Run from repo root:
    python3 scripts/build_phi_animation.py
"""
from __future__ import annotations
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Arc

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "video" / "phi-rectangles.mp4"
OUT.parent.mkdir(parents=True, exist_ok=True)

PHI = (1 + math.sqrt(5)) / 2

# Brand palette (matches the site)
BG       = "#0a0e1a"
GOLD     = "#daa055"
GOLD_SOFT= "#c48c42"
CREAM    = "#e8e0ce"
CREAM_DIM= "#b9b09b"

# ---------- Fibonacci layout ----------
# We build a 5-step Fibonacci spiral construction. Each step adds a square
# of side length F(n), placed adjacent to the existing rectangle following
# the classic golden-rectangle spiral pattern.
FIB = [1, 1, 2, 3, 5, 8, 13]  # 7 squares — covers the visual nicely

def build_squares():
    """Return list of (x, y, side, quadrant) for each square in build order.
    quadrant ∈ {'r','d','l','u'} = direction the new square attaches (right/down/left/up).
    """
    squares = []
    x, y = 0.0, 0.0
    # Place the first square
    side = FIB[0]
    squares.append((x, y, side, 'seed'))
    # The first add goes RIGHT, then we rotate counter-clockwise:
    # right → up → left → down → right → up → ...
    rotation = ['r', 'u', 'l', 'd']
    bbox = [x, y, x + side, y + side]  # x_min, y_min, x_max, y_max
    for i in range(1, len(FIB)):
        s = FIB[i]
        direction = rotation[(i - 1) % 4]
        if direction == 'r':
            nx = bbox[2]; ny = bbox[1]
            bbox[2] = nx + s
        elif direction == 'u':
            nx = bbox[2] - s; ny = bbox[3]
            bbox[3] = ny + s
        elif direction == 'l':
            nx = bbox[0] - s; ny = bbox[3] - s
            bbox[0] = nx
        elif direction == 'd':
            nx = bbox[0]; ny = bbox[1] - s
            bbox[1] = ny
        squares.append((nx, ny, s, direction))
    return squares, bbox

# ---------- per-square spiral arc ----------
def spiral_arc_for_square(x, y, s, direction, prev_direction):
    """Return (cx, cy, radius, theta_start, theta_end) for the quarter-arc
    drawn inside this square. Each square hosts one 90° arc whose corner
    sits at the inner vertex of the spiral. Angles in degrees, math-convention."""
    # The arc center sits at the corner of the square opposite to where the
    # spiral enters. Direction of growth determines which corner.
    # Arc center is the corner of the square that, together with the entry
    # and exit corners, makes a continuous CCW spiral that bulges AWAY from
    # the spiral's overall center (i.e., convex outward, never concave).
    if direction == 'seed':
        # Enters TL (0,s), exits BR (s,0); center at TR (s,s).
        return (x + s, y + s, s, 180, 270)
    if direction == 'r':
        # Enters BL (x,y), exits TR (x+s, y+s); center at TL (x, y+s).
        return (x,     y + s, s, 270, 360)
    if direction == 'u':
        # Enters BR (x+s, y), exits TL (x, y+s); center at BL (x, y).
        return (x,     y,     s, 0, 90)
    if direction == 'l':
        # Enters TR (x+s, y+s), exits BL (x, y); center at BR (x+s, y).
        return (x + s, y,     s, 90, 180)
    if direction == 'd':
        # Enters TL (x, y+s), exits BR (x+s, y); center at TR (x+s, y+s).
        return (x + s, y + s, s, 180, 270)


def render_animation():
    squares, bbox = build_squares()
    pad = 1.0
    xmin, ymin, xmax, ymax = bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad
    width  = xmax - xmin
    height = ymax - ymin

    # 16:9 frame at 720p. We letterbox the rectangle inside, centered.
    fig_w, fig_h = 12.8, 7.2  # inches at 100 dpi → 1280×720
    dpi = 100

    # Timing: each square gets ~1 s to appear, then a final 1.5 s to draw the spiral
    fps = 30
    per_square_frames = 22       # ≈ 0.73 s per square fade-in
    settle_frames     = 12       # short pause after all squares are placed
    spiral_frames     = 80       # ≈ 2.6 s to draw the spiral
    hold_frames       = 30       # ≈ 1 s hold at the end
    total_frames = per_square_frames * len(squares) + settle_frames + spiral_frames + hold_frames

    tmpdir = Path(tempfile.mkdtemp(prefix="phi_anim_"))
    try:
        # Precompute spiral arc points (for the final reveal animation)
        spiral_points = []
        for i, sq in enumerate(squares):
            x, y, s, d = sq
            prev_d = squares[i-1][3] if i > 0 else None
            cx, cy, r, t0, t1 = spiral_arc_for_square(x, y, s, d, prev_d)
            # 60 samples per arc
            ts = np.linspace(math.radians(t0), math.radians(t1), 60)
            for tt in ts:
                spiral_points.append((cx + r * math.cos(tt), cy + r * math.sin(tt)))
        spiral_xs = np.array([p[0] for p in spiral_points])
        spiral_ys = np.array([p[1] for p in spiral_points])

        for frame in range(total_frames):
            fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi)
            ax.set_facecolor(BG)
            fig.patch.set_facecolor(BG)
            ax.set_aspect('equal')
            ax.axis('off')
            # Frame the same view across all frames
            ax.set_xlim(xmin, xmax)
            ax.set_ylim(ymin, ymax)

            # 1) Draw squares progressively
            for i, (x, y, s, d) in enumerate(squares):
                # When is this square introduced?
                start_frame = i * per_square_frames
                age = frame - start_frame
                if age < 0:
                    break
                if age < per_square_frames:
                    alpha = age / per_square_frames
                else:
                    alpha = 1.0
                rect = Rectangle((x, y), s, s,
                                 linewidth=2.0,
                                 edgecolor=GOLD,
                                 facecolor=GOLD,
                                 alpha=alpha * 0.10)
                ax.add_patch(rect)
                # Outline a touch brighter
                rect2 = Rectangle((x, y), s, s,
                                  linewidth=2.0,
                                  edgecolor=GOLD,
                                  facecolor='none',
                                  alpha=alpha)
                ax.add_patch(rect2)
                # Label the side length
                if alpha > 0.5:
                    ax.text(x + s/2, y + s/2, f"{s}",
                            color=CREAM, fontsize=10 + min(s, 8),
                            ha='center', va='center',
                            alpha=alpha * 0.85,
                            family='serif')

            # 2) Spiral reveal phase
            squares_done_frame = per_square_frames * len(squares) + settle_frames
            if frame >= squares_done_frame:
                spiral_age = frame - squares_done_frame
                if spiral_age <= spiral_frames:
                    n = int(len(spiral_points) * (spiral_age / spiral_frames))
                    if n > 1:
                        ax.plot(spiral_xs[:n], spiral_ys[:n],
                                color=CREAM, linewidth=2.4, alpha=0.95)
                else:
                    ax.plot(spiral_xs, spiral_ys,
                            color=CREAM, linewidth=2.4, alpha=0.95)

            # Title / caption — fade in early, hold throughout
            title_age = frame
            title_alpha = min(1.0, title_age / 18)
            ax.text(0.5, 0.95,
                    r"$\varphi$-rectangles  ·  the Fibonacci construction",
                    transform=ax.transAxes,
                    color=CREAM, fontsize=14,
                    ha='center', va='top',
                    alpha=title_alpha,
                    family='serif')
            ax.text(0.5, 0.05,
                    r"each square has side $F_n$ ; the spiral threads every corner",
                    transform=ax.transAxes,
                    color=CREAM_DIM, fontsize=11,
                    ha='center', va='bottom',
                    alpha=title_alpha,
                    family='serif', style='italic')

            outpath = tmpdir / f"frame_{frame:05d}.png"
            fig.savefig(outpath, dpi=dpi, facecolor=BG, edgecolor='none',
                        bbox_inches=None, pad_inches=0)
            plt.close(fig)
            if frame % 30 == 0:
                print(f"  rendered frame {frame}/{total_frames}")

        # Assemble with ffmpeg
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-framerate", str(fps),
            "-i", str(tmpdir / "frame_%05d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "slow",
            "-crf", "23",
            "-movflags", "+faststart",
            str(OUT),
        ]
        subprocess.run(ffmpeg_cmd, check=True)
        size_kb = OUT.stat().st_size / 1024
        duration = total_frames / fps
        print(f"\nWrote {OUT}  ({size_kb:.0f} KB, {duration:.1f} s, {total_frames} frames)")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    if shutil.which("ffmpeg") is None:
        print("ffmpeg not on PATH — install it first.", file=sys.stderr)
        sys.exit(1)
    render_animation()
