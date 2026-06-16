#!/usr/bin/env python3
"""
Build transparent text overlay PNGs for Reel 1 (Chart Breakdown).
Each overlay is 1080x1920 (Reel size) with transparent background so it can
be dropped straight into CapCut as a layer on top of the screen recording.
"""

from PIL import Image, ImageDraw, ImageFont
import os

W, H     = 1080, 1920
OUT_DIR  = os.path.join(os.path.dirname(__file__), "reel1_overlays")
os.makedirs(OUT_DIR, exist_ok=True)

FONT_DIR = "/usr/share/fonts/truetype"
BOLD     = f"{FONT_DIR}/liberation/LiberationSans-Bold.ttf"

GOLD  = (240, 180, 41)
WHITE = (255, 255, 255)

PAD   = 70
MAX_W = W - PAD * 2

def load(size):
    try:    return ImageFont.truetype(BOLD, size)
    except: return ImageFont.load_default()

def tw(draw, text, font):
    return draw.textbbox((0, 0), text, font=font)[2]

def fit_font(draw, text, max_size, min_size=40):
    for size in range(max_size, min_size - 1, -2):
        f = load(size)
        if tw(draw, text, f) <= MAX_W:
            return f
    return load(min_size)

def wrap_text(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if tw(draw, trial, font) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def bold_text(draw, x, y, text, font, fill, stroke=3):
    for dx in range(-stroke, stroke + 1):
        for dy in range(-stroke, stroke + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=(0, 0, 0, 255))
    draw.text((x, y), text, font=font, fill=fill)

def make_overlay(filename, text, colour, max_size, y_frac):
    img  = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font  = fit_font(draw, text, max_size)
    lines = wrap_text(draw, text, font, MAX_W)

    lh_single = draw.textbbox((0, 0), "A", font=font)[3] + 14
    total_h   = lh_single * len(lines)
    y         = int(H * y_frac) - total_h // 2

    for line in lines:
        x = (W - tw(draw, line, font)) // 2
        bold_text(draw, x, y, line, font, colour)
        y += lh_single

    out = os.path.join(OUT_DIR, filename)
    img.save(out, "PNG")
    print(f"  ✓ {filename}")

print("Building Reel 1 text overlays...\n")

make_overlay("01_watch_this.png",
             "WATCH THIS BEFORE YOU TAKE YOUR NEXT TRADE",
             WHITE, 84, 0.12)

make_overlay("02_breaks_structure.png",
             "PRICE BREAKS STRUCTURE HERE",
             GOLD, 96, 0.12)

make_overlay("03_retests_level.png",
             "NOW IT RETESTS THE LEVEL",
             WHITE, 96, 0.12)

make_overlay("04_this_is_entry.png",
             "THIS IS THE ENTRY",
             GOLD, 110, 0.12)

make_overlay("05_stop_target.png",
             "STOP LOSS BELOW STRUCTURE. TARGET AT THE NEXT KEY LEVEL",
             WHITE, 72, 0.12)

make_overlay("06_target_hit.png",
             "TARGET HIT",
             GOLD, 130, 0.12)

make_overlay("07_final_line.png",
             "THIS IS MARKET STRUCTURE. LEARN IT BEFORE YOU TRADE ANOTHER PENNY.",
             WHITE, 78, 0.5)

print(f"\nDone → {OUT_DIR}")
