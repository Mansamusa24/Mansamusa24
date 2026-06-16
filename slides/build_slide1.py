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

F_HUGE  = load(BOLD, 112)
F_LARGE = load(BOLD, 96)
F_MED   = load(BOLD, 72)
F_SMALL = load(BOLD, 48)
F_TINY  = load(BOLD, 30)

# ── 1. Background: correct EXIF rotation, scale to FILL 1080x1350, centre-crop
from PIL import ImageOps
bg = Image.open(BG_PATH)
bg = ImageOps.exif_transpose(bg).convert("RGB")

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

PAD     = 60          # left/right padding
MAX_W   = W - PAD*2  # 960px usable width

def text_w(draw, text, font):
    return draw.textbbox((0, 0), text, font=font)[2]

def fit_font(draw, text, max_size, min_size=36):
    """Return largest font that fits within MAX_W."""
    for size in range(max_size, min_size - 1, -2):
        f = load(BOLD, size)
        if text_w(draw, text, f) <= MAX_W:
            return f
    return load(BOLD, min_size)

def draw_centred(draw, text, font, y, fill=WHITE):
    x = (W - text_w(draw, text, font)) // 2
    draw.text((x, y), text, font=font, fill=fill)
    lh = draw.textbbox((0,0), "A", font=font)[3]
    return y + lh + 8

def draw_mixed(draw, segments, font, y):
    total = sum(text_w(draw, t, font) for t, _ in segments)
    x     = (W - total) // 2
    for text, colour in segments:
        draw.text((x, y), text, font=font, fill=colour)
        x += text_w(draw, text, font)
    lh = draw.textbbox((0,0), "A", font=font)[3]
    return y + lh + 8

# ── 4. Logo + Telegram bottom ─────────────────────────────────────────────────
logo = Image.open(LOGO_PATH).convert("RGBA")
logo.thumbnail((160, 160), Image.LANCZOS)
lw, lh = logo.size
ly     = H - lh - 70
slide.paste(logo, ((W - lw)//2, ly), logo)

draw = ImageDraw.Draw(slide)

# ── 5. Text block: auto-fit fonts, stack from 38% down to just above logo ────
text_top = int(H * 0.36)
text_bot = ly - 16

# Define lines with their preferred max font size
line_defs = [
    ("EVERY TRADER NEEDS",   F_LARGE, WHITE),
    ("TO KNOW THIS FIRST.",  F_LARGE, WHITE),
    ("THE TRUTH ABOUT",      F_MED,   WHITE),
    ("MARKET STRUCTURE",     F_LARGE, GOLD),
    ("THE PROS NEVER TEACH", F_MED,   WHITE),
    ("SWIPE TO LEARN →",     F_SMALL, GOLD),
]

# Auto-fit each line
fitted = []
for text, preferred, colour in line_defs:
    font = fit_font(draw, text, preferred.size if hasattr(preferred, 'size') else 96)
    fitted.append((text, font, colour))

# Measure total height
gap       = 10
total_h   = sum(draw.textbbox((0,0),"A",font=f)[3] + gap for _, f, _ in fitted)
avail     = text_bot - text_top
y         = text_top + max(0, (avail - total_h) // 2)

for text, font, colour in fitted:
    y = draw_centred(draw, text, font, y, fill=colour)

# Telegram logo + @titus.net
from PIL import Image as _Img
tg_logo = _Img.open(os.path.join(os.path.dirname(__file__), "telegram_logo.png")).convert("RGBA")
tg_logo.thumbnail((44, 44), _Img.LANCZOS)
iw, ih  = tg_logo.size
tg_text = "@titus.net"
tg_font = load(BOLD, 32)
tgw     = text_w(draw, tg_text, tg_font)
total   = iw + 10 + tgw
xs      = (W - total) // 2
ty      = H - 44
slide.paste(tg_logo, (xs, ty - ih//2 + 10), tg_logo)
draw = ImageDraw.Draw(slide)
draw.text((xs + iw + 10, ty), tg_text, font=tg_font, fill=GOLD)

# ── 5. Save ───────────────────────────────────────────────────────────────────
out = os.path.join(OUT_DIR, "titus_carousel_1_hook.png")
slide.save(out, "PNG")
print(f"✓ Saved → {out}")
