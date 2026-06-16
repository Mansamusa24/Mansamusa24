#!/usr/bin/env python3
"""
Build full-screen frames for Reel 5 (Trading Lifestyle Reel).
Uses the user's own photos as backgrounds with bold Anton caption text,
ready to drop straight into CapCut as a slideshow.
"""

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import os

W, H      = 1080, 1920
SRC_DIR   = os.path.join(os.path.dirname(__file__), "reel5_lifestyle", "source")
OUT_DIR   = os.path.join(os.path.dirname(__file__), "reel5_lifestyle", "output")
LOGO_PATH = os.path.join(os.path.dirname(__file__), "titus_logo_transparent.png")
TG_PATH   = os.path.join(os.path.dirname(__file__), "telegram_logo.png")
FONT_DIR  = os.path.join(os.path.dirname(__file__), "fonts")
BOLD      = f"{FONT_DIR}/Anton-Regular.ttf"
os.makedirs(OUT_DIR, exist_ok=True)

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
    sd.text((x + 3, y + 6), text, font=font, fill=(0, 0, 0, 160))
    shadow = shadow.filter(ImageFilter.GaussianBlur(7))
    img.paste(Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB"), (0, 0))
    ImageDraw.Draw(img).text((x, y), text, font=font, fill=fill)

def make_bg(filename, darken_top=False):
    """Fill-crop the source photo to 1080x1920, then darken for legibility."""
    img = Image.open(os.path.join(SRC_DIR, filename)).convert("RGB")
    img = ImageOps.exif_transpose(img)
    scale_w = W / img.width
    scale_h = H / img.height
    scale   = max(scale_w, scale_h)
    new_w   = int(img.width * scale)
    new_h   = int(img.height * scale)
    img     = img.resize((new_w, new_h), Image.LANCZOS)
    left    = (new_w - W) // 2
    top     = (new_h - H) // 2
    img     = img.crop((left, top, left + W, top + H))

    overlay   = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od        = ImageDraw.Draw(overlay)
    top_alpha = 110 if darken_top else 55
    bot_alpha = 195
    for y in range(H):
        alpha = int(top_alpha + (bot_alpha - top_alpha) * (y / (H - 1)))
        od.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))

    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

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

def make_frame(out_name, src_name, text, colour, max_size, y_frac, darken_top=False, branding=False):
    img  = make_bg(src_name, darken_top=darken_top)
    draw = ImageDraw.Draw(img)

    font  = fit_font(draw, text, max_size)
    lines = wrap_text(draw, text, font, MAX_W)
    line_h = draw.textbbox((0, 0), "A", font=font)[3] + 20
    total_h = line_h * len(lines)
    y = int(H * y_frac) - total_h // 2

    rule_x = (W - 70) // 2
    draw.rectangle([rule_x, y - 36, rule_x + 70, y - 33], fill=GOLD)

    for line in lines:
        x = (W - tw(draw, line, font)) // 2
        shadow_text(img, x, y, line, font, colour)
        y += line_h

    if branding:
        add_branding(img)

    out = os.path.join(OUT_DIR, out_name)
    img.save(out, "JPEG", quality=95)
    print(f"  ✓ {out_name}")

print("Building Reel 5 lifestyle frames...\n")

make_frame("01.jpg", "01_hollywood.jpg",
           "I DIDN'T START TRADING FOR MONEY.", WHITE, 90, y_frac=0.58, darken_top=True)

make_frame("02.jpg", "02_car.jpg",
           "I STARTED FOR FREEDOM.", GOLD, 110, y_frac=0.68)

make_frame("03.jpg", "03_pier.jpg",
           "TIME. LOCATION. NO BOSS. NO LIMITS.", WHITE, 80, y_frac=0.46)

make_frame("04.jpg", "04_horizon.jpg",
           "MARKET STRUCTURE IS HOW I GOT HERE.", GOLD, 80, y_frac=0.48, branding=True)

print(f"\nDone → {OUT_DIR}")
