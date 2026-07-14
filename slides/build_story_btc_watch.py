#!/usr/bin/env python3
"""
Build an Instagram Story for a live BTCUSD setup watch: the chart screenshot
left almost untouched, with a hand-marked-up annotation (box + arrow + short
note) pointing at the level being watched, instead of a banner/header on top.
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
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

def remove_mco_watermark(img):
    """Blur out the 'More Crypto Online' watermark text and replace it with
    our own logo in the same spot, redrawing the fib line that runs through it."""
    line_y, line_colour = 142, (204, 112, 127)

    band = img.crop((0, 20, 858, line_y - 1))
    band = band.filter(ImageFilter.GaussianBlur(30))
    img.paste(band, (0, 20))

    draw = ImageDraw.Draw(img)
    draw.line([(0, line_y), (858, line_y)], fill=line_colour, width=2)

    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo.thumbnail((170, 170), Image.LANCZOS)
    lw, lh_ = logo.size
    logo.putalpha(logo.getchannel("A").point(lambda a: int(a * 0.9)))
    img.paste(logo, (430 - lw // 2, 95 - lh_ // 2), logo)

def remove_mco_subtext(img, original):
    """Blur out the 'MCO Global | www.mcoglobalonline.com' line, preserving
    the (3) and (5) wave-count labels that sit partly on top of it. The
    labels are restored by glyph brightness mask rather than a hard
    rectangle, so no seam shows around them."""
    keep_boxes = [(514, 225, 590, 277), (626, 213, 705, 261)]

    band_box = (0, 200, 858, 252)
    band = img.crop(band_box).filter(ImageFilter.GaussianBlur(18))
    img.paste(band, band_box[:2])

    for kb in keep_boxes:
        patch = original.crop(kb)
        gray  = patch.convert("L")
        mask  = gray.point(lambda v: 255 if v > 175 else 0).filter(ImageFilter.GaussianBlur(1.0))
        img.paste(patch, kb[:2], mask)

def build():
    img      = make_bg().convert("RGBA")
    original = img.copy()
    remove_mco_watermark(img)
    remove_mco_subtext(img, original)
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
