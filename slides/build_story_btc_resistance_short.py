#!/usr/bin/env python3
"""
Build a Telegram post for a possible BTC short as price approaches the
fib resistance cluster: crop out the mobile app's view-only banner/nav
chrome and annotate directly on the chart with the same hand-marked-up
style (arrow + note) used for the fib-watch story.
"""

from PIL import Image, ImageDraw, ImageFont
import os

BASE_DIR  = os.path.dirname(__file__)
SRC       = os.path.join(BASE_DIR, "stories", "source", "btc_resistance_short.jpeg")
OUT_DIR   = os.path.join(BASE_DIR, "stories", "output")
LOGO_PATH = os.path.join(BASE_DIR, "titus_logo_transparent.png")
FONT_DIR  = os.path.join(BASE_DIR, "fonts")
NOTE_FONT = f"{FONT_DIR}/Italiana-Regular.ttf"
os.makedirs(OUT_DIR, exist_ok=True)

GOLD  = (240, 180, 41)
WHITE = (255, 255, 255)

def load_note(size):
    try:    return ImageFont.truetype(NOTE_FONT, size)
    except: return ImageFont.load_default()

def draw_arrow(draw, x, y_top, y_bottom, colour, width=6):
    draw.line([(x, y_bottom), (x, y_top)], fill=colour, width=width)
    ah = 16
    draw.polygon([
        (x - ah * 0.7, y_top + ah),
        (x + ah * 0.7, y_top + ah),
        (x, y_top - 2),
    ], fill=colour)

def build():
    img = Image.open(SRC).convert("RGB")
    w, h = img.size
    img = img.crop((0, 0, w, 1727))  # drop the view-only banner + bottom nav

    img = img.convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Arrow pointing up into the 38.2%-78.6% fib resistance cluster from a
    # note below it, clear of the candles and price-scale column.
    arrow_x  = 560
    zone_y   = 680   # just under the 38.2% line, bottom of the fib cluster
    note_top = 1090
    draw_arrow(draw, arrow_x, zone_y, note_top - 20, GOLD)

    note_font = load_note(54)
    note_lines = ["approaching the", "fib resistance cluster —", "watching for a rejection"]
    ny = note_top
    for line in note_lines:
        draw.text((420, ny), line, font=note_font, fill=WHITE)
        ny += 64

    # Small logo watermark, in the clear space inside the (4) resistance
    # zone at top, away from any price data.
    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo.thumbnail((130, 130), Image.LANCZOS)
    lw, lh = logo.size
    logo.putalpha(logo.getchannel("A").point(lambda a: int(a * 0.85)))
    img.paste(logo, (40, 30), logo)

    img = img.convert("RGB")
    out = os.path.join(OUT_DIR, "btc_resistance_short.jpg")
    img.save(out, "JPEG", quality=95)
    print(f"  ✓ {out}")

print("Building BTC resistance-short Telegram post...\n")
build()
