#!/usr/bin/env python3
"""
Build a Facebook page cover banner from the master infographic: extract the
KuCoin + Bitget "Copy My Trades" band and set it on a Facebook-cover-sized
black canvas (1640x624) with the Titus logo and a heading above it.
"""

from PIL import Image, ImageDraw, ImageFont
import os

BASE_DIR  = os.path.dirname(__file__)
SRC       = os.path.join(BASE_DIR, "stories", "source", "titus_master_infographic.png")
OUT_DIR   = os.path.join(BASE_DIR, "stories", "output")
LOGO_PATH = os.path.join(BASE_DIR, "titus_logo_transparent.png")
FONT      = os.path.join(BASE_DIR, "fonts", "Anton-Regular.ttf")
os.makedirs(OUT_DIR, exist_ok=True)

GOLD  = (240, 180, 41)
WHITE = (240, 240, 240)

# The copy-trade band inside the infographic (both panels, gold borders).
BAND_BOX = (55, 843, 1198, 1053)

# Facebook page cover, recommended high-res upload size.
CANVAS_W, CANVAS_H = 1640, 624

def f(size):
    try:    return ImageFont.truetype(FONT, size)
    except: return ImageFont.load_default()

def build():
    src  = Image.open(SRC).convert("RGB")
    band = src.crop(BAND_BOX)

    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (0, 0, 0))
    draw   = ImageDraw.Draw(canvas)

    # --- Heading at the top ---
    head_font = f(58)
    head = "COPY MY TRADES WITH TITUS"
    hw = draw.textlength(head, font=head_font)
    draw.text(((CANVAS_W - hw) / 2, 60), head, font=head_font, fill=GOLD)

    sub_font = f(30)
    sub = "LEAD TRADER ON KUCOIN  ·  ELITE TRADER ON BITGET"
    sw = draw.textlength(sub, font=sub_font)
    draw.text(((CANVAS_W - sw) / 2, 132), sub, font=sub_font, fill=WHITE)

    # --- Copy-trade band, scaled to fit width, placed lower half ---
    margin = 70
    target_w = CANVAS_W - margin * 2
    scale = target_w / band.width
    band_r = band.resize((target_w, int(band.height * scale)), Image.LANCZOS)
    bx = margin
    by = 210
    canvas.paste(band_r, (bx, by))

    canvas.save(os.path.join(OUT_DIR, "fb_banner_copytrade.jpg"), "JPEG", quality=95)
    print(f"  ✓ fb_banner_copytrade.jpg  ({CANVAS_W}x{CANVAS_H})")

    # --- Also save the clean band on its own, in case you want just that ---
    band.save(os.path.join(OUT_DIR, "copytrade_band.png"))
    print(f"  ✓ copytrade_band.png  ({band.width}x{band.height})")

print("Building Facebook copy-trade banner...\n")
build()
