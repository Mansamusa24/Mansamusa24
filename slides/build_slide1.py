#!/usr/bin/env python3
"""
Build Slide 1 in @asianriches style:
- Cinematic full-bleed background
- Dark gradient overlay on bottom half
- Massive bold white + gold headline
- Titus logo bottom centre
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import os

W, H      = 1080, 1350
OUT_DIR   = os.path.join(os.path.dirname(__file__), "market-structure", "output")
BG_PATH   = os.path.join(os.path.dirname(__file__), "bg_slide1.jpg")
LOGO_PATH = os.path.join(os.path.dirname(__file__), "titus_logo_transparent.png")
FONT_DIR  = "/usr/share/fonts/truetype"

GOLD  = (240, 180,  41)
WHITE = (255, 255, 255)

def load(path, size):
    try:    return ImageFont.truetype(path, size)
    except: return ImageFont.load_default()

BOLD = f"{FONT_DIR}/liberation/LiberationSans-Bold.ttf"

F_HUGE  = load(BOLD, 80)
F_LARGE = load(BOLD, 66)
F_MED   = load(BOLD, 52)
F_SMALL = load(BOLD, 32)
F_TINY  = load(BOLD, 24)

# ── 1. Background: correct EXIF rotation, scale to FILL 1080x1350, centre-crop
from PIL.ExifTags import TAGS
bg = Image.open(BG_PATH).convert("RGB")

# Auto-rotate based on EXIF orientation
try:
    exif = bg._getexif()
    if exif:
        for tag, val in exif.items():
            if TAGS.get(tag) == 'Orientation':
                if val == 3:   bg = bg.rotate(180, expand=True)
                elif val == 6: bg = bg.rotate(270, expand=True)
                elif val == 8: bg = bg.rotate(90,  expand=True)
except Exception:
    pass

scale_w = W / bg.width
scale_h = H / bg.height
scale   = max(scale_w, scale_h)
new_w   = int(bg.width  * scale)
new_h   = int(bg.height * scale)
bg      = bg.resize((new_w, new_h), Image.LANCZOS)
left    = (new_w - W) // 2
top     = (new_h - H) // 2
bg      = bg.crop((left, top, left + W, top + H))

slide = bg.copy()
draw  = ImageDraw.Draw(slide)

# ── 2. Dark gradient overlay — bottom 60% ────────────────────────────────────
overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
od      = ImageDraw.Draw(overlay)
grad_top = int(H * 0.28)   # gradient starts here
for y in range(grad_top, H):
    # alpha ramps from 0 → 230 over the gradient zone
    progress = (y - grad_top) / (H - grad_top)
    alpha    = int(210 * min(progress * 1.4, 1.0))
    od.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))

slide = Image.alpha_composite(slide.convert("RGBA"), overlay).convert("RGB")
draw  = ImageDraw.Draw(slide)

# ── 3. Text layout ────────────────────────────────────────────────────────────
#
# Style: @asianriches — HUGE caps, white + gold keywords, tight leading
# Headline broken into lines manually for max impact
#

def text_w(draw, text, font):
    return draw.textbbox((0, 0), text, font=font)[2]

def draw_line_mixed(draw, segments, y, font, line_w=W, pad=60):
    """Draw a line with mixed colours. segments = [(text, colour), ...]"""
    total = sum(draw.textbbox((0,0), t, font=font)[2] for t, _ in segments)
    x     = (line_w - total) // 2  # centre
    for text, colour in segments:
        draw.text((x, y), text, font=font, fill=colour)
        x += draw.textbbox((0,0), text, font=font)[2]
    return y + draw.textbbox((0,0), "A", font=font)[3] + 4

def draw_centred(draw, text, font, y, fill=WHITE):
    tw = text_w(draw, text, font)
    draw.text(((W - tw) // 2, y), text, font=font, fill=fill)
    return y + draw.textbbox((0,0), text, font=font)[3] + 6

# ── 4. Logo bottom centre ─────────────────────────────────────────────────────
logo = Image.open(LOGO_PATH).convert("RGBA")
logo.thumbnail((160, 160), Image.LANCZOS)
lw, lh = logo.size
lx     = (W - lw) // 2
ly     = H - lh - 40
slide.paste(logo, (lx, ly), logo)

# Calculate available text height: from 42% down to just above logo
text_top  = int(H * 0.40)
text_bot  = ly - 20   # stop just above logo
draw = ImageDraw.Draw(slide)

# Measure total text block height so we can centre it
line_gap = 8
lines = [
    ("BEFORE YOU PLACE", F_LARGE, WHITE),
    ("ANOTHER TRADE —",  F_LARGE, WHITE),
    ("MASTER MARKET",    F_LARGE, WHITE),   # gold handled separately
    ("STRUCTURE.",       F_LARGE, GOLD),
    ("HERE'S WHAT THE",  F_MED,   WHITE),
    ("PROS DON'T TEACH:", F_MED,  WHITE),
]

def line_h(font):
    return draw.textbbox((0,0), "A", font=font)[3] + line_gap

total_h = (line_h(F_LARGE)*4 + line_h(F_MED)*2 +
           line_h(F_SMALL))   # swipe cue
avail   = text_bot - text_top
y_start = text_top + max(0, (avail - total_h) // 2)

y = y_start
y = draw_centred(draw, "EVERY TRADER NEEDS",  F_LARGE, y)
y = draw_centred(draw, "TO KNOW THIS FIRST.",   F_LARGE, y)
y = draw_line_mixed(draw, [("THE TRUTH ABOUT ", WHITE), ("MARKET", GOLD)], y, F_MED) + line_gap
y = draw_centred(draw, "STRUCTURE",  F_LARGE, y, fill=GOLD)
y = draw_centred(draw, "THE PROS NEVER", F_MED, y + 4)
y = draw_centred(draw, "TALK ABOUT:", F_MED, y)
y += 18
y = draw_line_mixed(draw, [("SWIPE TO LEARN  ", WHITE), ("→", GOLD)], y, F_SMALL)

# Telegram logo + @titus.net under brand logo
from PIL import Image as _Img
tg_logo = _Img.open(os.path.join(os.path.dirname(__file__), "telegram_logo.png")).convert("RGBA")
tg_logo.thumbnail((44, 44), _Img.LANCZOS)
iw, ih  = tg_logo.size

draw    = ImageDraw.Draw(slide)
tg_text = "@titus.net"
txt_w   = text_w(draw, tg_text, F_SMALL)
gap     = 10
total   = iw + gap + txt_w
x_start = (W - total) // 2
ty      = H - 40

slide.paste(tg_logo, (x_start, ty - ih//2 + 8), tg_logo)
draw = ImageDraw.Draw(slide)
draw.text((x_start + iw + gap, ty - 4), tg_text, font=F_SMALL, fill=(240, 180, 41))

# ── 5. Save ───────────────────────────────────────────────────────────────────
out = os.path.join(OUT_DIR, "titus_carousel_1_hook.png")
slide.save(out, "PNG")
print(f"✓ Saved → {out}")
