#!/usr/bin/env python3
"""
Build a Facebook page cover banner from the master infographic: pull just the
KuCoin and Bitget logo + role blocks (no "Copy My Trades" text) and set them in
two gold-bordered panels pushed to the left and right edges, leaving the centre
clear for the profile picture that Facebook overlays at the bottom-centre.
"""

from PIL import Image, ImageDraw, ImageFont
import os

BASE_DIR  = os.path.dirname(__file__)
SRC       = os.path.join(BASE_DIR, "stories", "source", "titus_master_infographic.png")
OUT_DIR   = os.path.join(BASE_DIR, "stories", "output")
FONT      = os.path.join(BASE_DIR, "fonts", "Anton-Regular.ttf")
os.makedirs(OUT_DIR, exist_ok=True)

DEBUG = os.environ.get("DEBUG") == "1"   # overlay the FB profile circle to check clearance

GOLD  = (240, 180, 41)
WHITE = (240, 240, 240)

KU_BLOCK = (70, 878, 372, 1016)
BG_BLOCK = (648, 878, 920, 1016)

CANVAS_W, CANVAS_H = 1640, 624

# Where Facebook overlays the round profile picture on the mobile cover:
# horizontally centred, sitting low, roughly this centre + radius.
PROFILE_C = (CANVAS_W // 2, 546)
PROFILE_R = 225

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

    # --- Heading, top-centre (clear of the bottom-centre profile pic) ---
    head_font = f(50)
    head = "TRADE WITH TITUS"
    hw = draw.textlength(head, font=head_font)
    draw.text(((CANVAS_W - hw) / 2, 48), head, font=head_font, fill=GOLD)

    sub_font = f(25)
    sub = "LEAD TRADER ON KUCOIN  ·  ELITE TRADER ON BITGET"
    sw = draw.textlength(sub, font=sub_font)
    draw.text(((CANVAS_W - sw) / 2, 112), sub, font=sub_font, fill=WHITE)

    # --- Two panels flanking the centre, near the outer edges ---
    panel_w, panel_h = 430, 210
    margin = 70
    pad = 30
    y0 = 260
    positions = [margin, CANVAS_W - margin - panel_w]
    for block, x in [(ku, positions[0]), (bg, positions[1])]:
        draw.rounded_rectangle(
            [x, y0, x + panel_w, y0 + panel_h],
            radius=24, outline=GOLD, width=3,
        )
        b = fit(block, panel_w - pad * 2, panel_h - pad * 2)
        bx = x + (panel_w - b.width) // 2
        by = y0 + (panel_h - b.height) // 2
        canvas.paste(b, (bx, by))

    if DEBUG:
        cx, cy = PROFILE_C
        draw.ellipse([cx - PROFILE_R, cy - PROFILE_R, cx + PROFILE_R, cy + PROFILE_R],
                     outline=(255, 0, 0), width=4)

    canvas.save(os.path.join(OUT_DIR, "fb_banner_copytrade.jpg"), "JPEG", quality=95)
    print(f"  ✓ fb_banner_copytrade.jpg  ({CANVAS_W}x{CANVAS_H})  DEBUG={DEBUG}")

print("Building Facebook copy-trade banner (panels flanking centre)...\n")
build()
