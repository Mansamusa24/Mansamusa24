#!/usr/bin/env python3
"""
Build an Instagram Story for a live BTCUSD setup watch: the chart screenshot
left almost untouched, with a hand-marked-up annotation (box + arrow + short
note) pointing at the level being watched, instead of a banner/header on top.
"""

from PIL import Image, ImageDraw, ImageFont
import os

W, H      = 1080, 1920
BASE_DIR  = os.path.dirname(__file__)
SRC       = os.path.join(BASE_DIR, "stories", "source", "btc_fib_watch.jpeg")
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

def tw(draw, text, font):
    return draw.textbbox((0, 0), text, font=font)[2]

def make_bg():
    img = Image.open(SRC).convert("RGB")
    scale = max(W / img.width, H / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - W) // 2, (nh - H) // 2
    return img.crop((left, top, left + W, top + H))

def draw_arrow(draw, x, y_top, y_bottom, colour, width=5):
    draw.line([(x, y_bottom), (x, y_top)], fill=colour, width=width)
    ah = 14
    draw.polygon([
        (x - ah * 0.7, y_top + ah),
        (x + ah * 0.7, y_top + ah),
        (x, y_top - 2),
    ], fill=colour)

def build():
    img  = make_bg().convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Mark up the fib confluence zone (38.2% -> 61.8%) with a hand-drawn-style box.
    box = [12, 945, 866, 1180]
    draw.rounded_rectangle(box, radius=18, outline=GOLD, width=6)

    # Arrow pointing up into the box from a note below it, clear of the
    # second fib zone box that sits directly underneath.
    arrow_x = 260
    note_top = 1530
    draw_arrow(draw, arrow_x, box[3] + 8, note_top - 20, GOLD)

    note_font = load_note(50)
    note_lines = ["watching for a", "liquidity sweep + MSS", "right here"]
    ny = note_top
    for line in note_lines:
        draw.text((140, ny), line, font=note_font, fill=WHITE)
        ny += 58

    # Small logo watermark, bottom-right corner, kept minimal.
    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo.thumbnail((90, 90), Image.LANCZOS)
    lw, lh_ = logo.size
    logo.putalpha(logo.getchannel("A").point(lambda a: int(a * 0.85)))
    img.paste(logo, (W - lw - 36, H - lh_ - 36), logo)

    img = img.convert("RGB")
    out = os.path.join(OUT_DIR, "btc_fib_watch.jpg")
    img.save(out, "JPEG", quality=95)
    print(f"  ✓ {out}")

print("Building BTC fib-watch story...\n")
build()
