#!/usr/bin/env python3
"""
Overlay the 3 pre-trade conditions as gold bullet points on the lion / bull
market image. Text sits in the clear black band across the top so it never
covers the lion or the chart.
"""

from PIL import Image, ImageDraw, ImageFont
import os

BASE_DIR  = os.path.dirname(__file__)
SRC       = os.path.join(BASE_DIR, "stories", "source", "lion_conditions.jpeg")
OUT_DIR   = os.path.join(BASE_DIR, "stories", "output")
LOGO_PATH = os.path.join(BASE_DIR, "titus_logo_transparent.png")
FONT      = os.path.join(BASE_DIR, "fonts", "Anton-Regular.ttf")
os.makedirs(OUT_DIR, exist_ok=True)

GOLD  = (240, 180, 41)
WHITE = (245, 245, 245)

def f(size):
    try:    return ImageFont.truetype(FONT, size)
    except: return ImageFont.load_default()

def build():
    img = Image.open(SRC).convert("RGBA")
    w, h = img.size
    draw = ImageDraw.Draw(img)

    # --- Headline, centred in the top black band ---
    head_font = f(52)
    head = "BEFORE I ENTER A TRADE"
    hw = draw.textlength(head, font=head_font)
    draw.text(((w - hw) / 2, 48), head, font=head_font, fill=GOLD)

    sub_font = f(26)
    sub = "ALL THREE MUST LINE UP. NO CONFLUENCE, NO TRADE."
    sw = draw.textlength(sub, font=sub_font)
    draw.text(((w - sw) / 2, 118), sub, font=sub_font, fill=WHITE)

    # --- Three bullet conditions ---
    bullet_font = f(46)
    bullets = ["LIQUIDITY SWEEP", "MARKET STRUCTURE SHIFT", "RVOL CONFIRMATION"]
    bx = 90          # left start of dot
    tx = 150         # text start
    by = 195         # first bullet baseline
    step = 78
    for i, b in enumerate(bullets):
        y = by + i * step
        # gold square bullet marker
        draw.rectangle([bx, y + 14, bx + 24, y + 38], fill=GOLD)
        draw.text((tx, y), b, font=bullet_font, fill=WHITE)

    # --- Logo watermark, bottom right in the dark corner ---
    if os.path.exists(LOGO_PATH):
        logo = Image.open(LOGO_PATH).convert("RGBA")
        logo.thumbnail((130, 130), Image.LANCZOS)
        lw, lh = logo.size
        logo.putalpha(logo.getchannel("A").point(lambda a: int(a * 0.9)))
        img.paste(logo, (w - lw - 36, h - lh - 36), logo)

    img = img.convert("RGB")
    out = os.path.join(OUT_DIR, "lion_conditions.jpg")
    img.save(out, "JPEG", quality=95)
    print(f"  ✓ {out}  ({img.size[0]}x{img.size[1]})")

print("Building lion pre-trade conditions graphic...\n")
build()
