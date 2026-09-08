#!/usr/bin/env python3
"""Render the social-card image used for link previews.

Regenerate after changing the title/tagline:
    cd api && uv run python3 ../docs-site/scripts/make-og-image.py

Output is committed, so this only needs to run when the wording changes.
Brand values mirror web/public/favicon.svg and web/vite.config.ts.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
BG = "#0c1322"
AMBER = "#f5a623"
WHITE = "#f8fafc"
MUTED = "#94a3b8"

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
BOLD = FONT_DIR / "DejaVuSans-Bold.ttf"
REGULAR = FONT_DIR / "DejaVuSans.ttf"

OUT = Path(__file__).resolve().parent.parent / "public" / "og.png"


def die(draw, x, y, size, pips):
    """One die: rounded square outline plus pip circles at 3x3 grid slots.

    Filled with the background so a die drawn later cleanly occludes the one
    behind it, the way the two dice overlap in the app's favicon.
    """
    draw.rounded_rectangle(
        [x, y, x + size, y + size], radius=size // 6, fill=BG, outline=AMBER, width=7
    )
    step = size / 4
    for col, row in pips:
        cx, cy = x + step * col, y + step * row
        r = size / 14
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=AMBER)


def main() -> None:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # Accent rule along the top edge.
    d.rectangle([0, 0, W, 10], fill=AMBER)

    # Dice sit right of the text block, overlapping like the app's favicon.
    die(d, 855, 140, 200, [(1, 1), (2, 2), (3, 3)])
    die(d, 1005, 295, 155, [(1, 1), (3, 1), (1, 3), (3, 3)])

    title = ImageFont.truetype(str(BOLD), 88)
    tag = ImageFont.truetype(str(REGULAR), 36)
    small = ImageFont.truetype(str(BOLD), 28)

    d.text((90, 268), "MC GamerTime", font=title, fill=WHITE)
    d.text((90, 386), "Board game inventory and session tracker", font=tag, fill=MUTED)

    # Short amber rule anchors the text block and echoes the top edge.
    d.rectangle([90, 462, 90 + 96, 468], fill=AMBER)
    d.text((90, 500), "Self-host with Docker  ·  or deploy on AWS", font=small, fill=AMBER)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, optimize=True)
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024}KB)")


if __name__ == "__main__":
    main()
