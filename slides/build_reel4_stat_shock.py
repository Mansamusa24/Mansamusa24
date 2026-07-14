#!/usr/bin/env python3
"""
Build full-screen stat cards for Reel 4 (Stat Shock Reel).
Each card is a complete 1080x1920 frame (dark vignette backdrop + clean
shadowed text, no hard outline) ready to drop straight into CapCut as a
slideshow, no recording required.
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

W, H     = 1080, 1920
OUT_DIR  = os.path.join(os.path.dirname(__file__), "reel4_stat_shock")
LOGO_PATH = os.path.join(os.path.dirname(__file__), "titus_logo_transparent.png")
TG_PATH   = os.path.join(os.path.dirname(__file__), "telegram_logo.png")
os.makedirs(OUT_DIR, exist_ok=True)

FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
BOLD     = f"{FONT_DIR}/Anton-Regular.ttf"

GOLD  = (240, 180, 41)
WHITE = (255, 255, 255)

PAD   = 80
MAX_W = W - PAD * 2

def load(size):
    try:    return ImageFont.truetype(BOLD, size)
    except: return ImageFont.load_default()

def tw(draw, text, font):
    return draw.textbbox((0, 0), text, font=font)[2]

def fit_font(draw, text, max_size, min_size=48):
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

def shadow_text(img, x, y, text, font, fill):
    """Soft drop shadow instead of a hard meme-style outline."""
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.text((x + 3, y + 6), text, font=font, fill=(0, 0, 0, 150))
    shadow = shadow.filter(ImageFilter.GaussianBlur(7))
    img.paste(Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB"), (0, 0))
    ImageDraw.Draw(img).text((x, y), text, font=font, fill=fill)

def make_bg():
    """Clean dark vignette background, no screenshot chrome, pure statement-card feel."""
    img  = Image.new("RGB", (W, H), (8, 9, 12))
    draw = ImageDraw.Draw(img)
    cx, cy = W // 2, H // 2
    max_r  = int((W**2 + H**2) ** 0.5 / 2)
    for r in range(max_r, 0, -4):
        p     = r / max_r
        shade = int(8 + 14 * (1 - p))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(shade, shade + 1, shade + 3))
    return img

def add_branding(img):
    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo.thumbnail((130, 130), Image.LANCZOS)
    lw, lh_ = logo.size
    ly = H - lh_ - 110
    img.paste(logo, ((W - lw)//2, ly), logo)

    tg = Image.open(TG_PATH).convert("RGBA")
    tg.thumbnail((36, 36), Image.LANCZOS)
    iw, ih = tg.size
    draw = ImageDraw.Draw(img)
    font = load(28)
    text = "@titus.net"
    tgw  = tw(draw, text, font)
    total = iw + 8 + tgw
    xs = (W - total) // 2
    ty = H - 60
    img.paste(tg, (xs, ty - ih//2 + 6), tg)
    draw.text((xs + iw + 8, ty - 2), text, font=font, fill=GOLD)

def make_card(filename, text, colour, max_size=140, branding=False):
    img  = make_bg()
    draw = ImageDraw.Draw(img)

    font  = fit_font(draw, text, max_size)
    lines = wrap_text(draw, text, font, MAX_W)
    line_h = draw.textbbox((0, 0), "A", font=font)[3] + 24
    total_h = line_h * len(lines)
    y = int(H * 0.44) - total_h // 2

    rule_x = (W - 70) // 2
    draw.rectangle([rule_x, y - 50, rule_x + 70, y - 47], fill=GOLD)

    for line in lines:
        x = (W - tw(draw, line, font)) // 2
        shadow_text(img, x, y, line, font, colour)
        y += line_h

    if branding:
        add_branding(img)

    out = os.path.join(OUT_DIR, filename)
    img.save(out, "JPEG", quality=95)
    print(f"  ✓ {filename}")

print("Building Reel 4 stat cards...\n")

make_card("01.jpg", "90% OF TRADERS LOSE MONEY.", WHITE, 130)
make_card("02.jpg", "THE REASON IS NOT STRATEGY.", WHITE, 110)
make_card("03.jpg", "IT IS PATIENCE.", GOLD, 160)
make_card("04.jpg", "MOST PEOPLE EXIT TOO EARLY.", WHITE, 110)
make_card("05.jpg", "OR ENTER TOO LATE.", WHITE, 130)
make_card("06.jpg", "MARKET STRUCTURE FIXES BOTH.", GOLD, 100)
make_card("07.jpg", "FOLLOW FOR DAILY PROOF.", WHITE, 110, branding=True)

print(f"\nDone → {OUT_DIR}")
