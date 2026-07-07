#!/usr/bin/env python3
"""
Build a Facebook page cover banner from the master infographic: pull just the
KuCoin and Bitget logo + role blocks (no "Copy My Trades" text) and set them in
two fresh gold-bordered panels on a Facebook-cover-sized black canvas.
"""

from PIL import Image, ImageDraw, ImageFont
import os

BASE_DIR  = os.path.dirname(__file__)
SRC       = os.path.join(BASE_DIR, "stories", "source", "titus_master_infographic.png")
OUT_DIR   = os.path.join(BASE_DIR, "stories", "output")
FONT      = os.path.join(BASE_DIR, "fonts", "Anton-Regular.ttf")
os.makedirs(OUT_DIR, exist_ok=True)

GOLD  = (240, 180, 41)
WHITE = (240, 240, 240)

# Logo + role blocks (logo + KUCOIN/Bitget + LEAD/ELITE TRADER) inside the
# infographic, cropped before the internal divider so the copy-trade text is
# dropped.
KU_BLOCK = (70, 878, 372, 1016)
BG_BLOCK = (648, 878, 920, 1016)

CANVAS_W, CANVAS_H = 1640, 624

def f(size):
    try:    return ImageFont.truetype(FONT, size)
    except: return ImageFont.load_default()

def fit(block, box_w, box_h):
    s = min(box_w / block.width, box_h / block.height)
    return block.resize((int(block.width * s), int(block.height * s)), Image.LANCZOS)

def build():
    src = Image.open(SRC).convert("RGB")
    ku  = src.crop(KU_BLOCK)
    bg  = src.crop(BG_BLOCK)

    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (0, 0, 0))
    draw   = ImageDraw.Draw(canvas)

    # Everything is kept inside a centred safe zone so Facebook's mobile edge
    # crop and the profile-picture overlay never cut the content.
    # --- Heading ---
    head_font = f(48)
    head = "TRADE WITH TITUS"
    hw = draw.textlength(head, font=head_font)
    draw.text(((CANVAS_W - hw) / 2, 108), head, font=head_font, fill=GOLD)

    sub_font = f(24)
    sub = "LEAD TRADER ON KUCOIN  ·  ELITE TRADER ON BITGET"
    sw = draw.textlength(sub, font=sub_font)
    draw.text(((CANVAS_W - sw) / 2, 170), sub, font=sub_font, fill=WHITE)

    # --- Two fresh panels (compact, centred) ---
    panel_w, panel_h = 500, 190
    gap = 56
    total = panel_w * 2 + gap
    x0 = (CANVAS_W - total) // 2
    y0 = 250
    pad = 34
    for i, (block, x) in enumerate([(ku, x0), (bg, x0 + panel_w + gap)]):
        draw.rounded_rectangle(
            [x, y0, x + panel_w, y0 + panel_h],
            radius=26, outline=GOLD, width=3,
        )
        b = fit(block, panel_w - pad * 2, panel_h - pad * 2)
        bx = x + (panel_w - b.width) // 2
        by = y0 + (panel_h - b.height) // 2
        canvas.paste(b, (bx, by))

    canvas.save(os.path.join(OUT_DIR, "fb_banner_copytrade.jpg"), "JPEG", quality=95)
    print(f"  ✓ fb_banner_copytrade.jpg  ({CANVAS_W}x{CANVAS_H})")

print("Building Facebook copy-trade banner (logos + roles only)...\n")
build()
