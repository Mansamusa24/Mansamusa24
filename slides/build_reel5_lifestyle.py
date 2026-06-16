#!/usr/bin/env python3
"""
Build full-screen frames for Reel 5 (Trading Lifestyle Reel).
Uses the user's own photos as backgrounds with editorial-style caption
text (letter-spaced serif caps + soft shadow, no heavy meme-text stroke),
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
SERIF     = f"{FONT_DIR}/Italiana-Regular.ttf"
os.makedirs(OUT_DIR, exist_ok=True)

GOLD  = (240, 180, 41)
WHITE = (255, 255, 255)

PAD = 80

def load(size):
    try:    return ImageFont.truetype(SERIF, size)
    except: return ImageFont.load_default()

def char_w(draw, ch, font):
    b = draw.textbbox((0, 0), ch, font=font)
    return b[2] - b[0]

def spaced_width(draw, text, font, spacing):
    if not text:
        return 0
    return sum(char_w(draw, ch, font) for ch in text) + spacing * (len(text) - 1)

def fit_font(draw, text, max_w, spacing, max_size, min_size=30):
    for size in range(max_size, min_size - 1, -2):
        f = load(size)
        if spaced_width(draw, text, f, spacing) <= max_w:
            return f
    return load(min_size)

def draw_spaced(draw, x, y, text, font, fill, spacing):
    cx = x
    for ch in text:
        draw.text((cx, y), ch, font=font, fill=fill)
        cx += char_w(draw, ch, font) + spacing

def render_caption(img, text, colour, max_size, spacing, align, anchor_y):
    """Draw letter-spaced serif caption with a soft drop shadow (no hard stroke)."""
    max_w = W - PAD * 2
    probe = ImageDraw.Draw(img)
    font  = fit_font(probe, text, max_w, spacing, max_size)
    tw    = spaced_width(probe, text, font, spacing)
    th    = probe.textbbox((0, 0), "A", font=font)[3]

    if align == "left":
        x = PAD
    else:
        x = (W - tw) // 2
    y = anchor_y

    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    draw_spaced(sd, x + 4, y + 6, text, font, (0, 0, 0, 170), spacing)
    shadow = shadow.filter(ImageFilter.GaussianBlur(5))
    img.paste(Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB"), (0, 0))

    draw = ImageDraw.Draw(img)
    draw_spaced(draw, x, y, text, font, colour, spacing)

    rule_w = 70
    rule_y = y - 28
    rule_x = PAD if align == "left" else (W - rule_w) // 2
    draw.rectangle([rule_x, rule_y, rule_x + rule_w, rule_y + 3], fill=GOLD)

    return y + th

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
    font = ImageFont.truetype(SERIF, 30)
    text = "@titus.net"
    tgw  = draw.textbbox((0, 0), text, font=font)[2]
    total = iw + 10 + tgw
    xs = (W - total) // 2
    ty = H - 60
    img.paste(tg, (xs, ty - ih//2 + 6), tg)
    draw.text((xs + iw + 10, ty - 6), text, font=font, fill=GOLD)

def make_frame(out_name, src_name, text, colour, max_size, anchor_y, align="left",
               spacing=8, darken_top=False, branding=False):
    img = make_bg(src_name, darken_top=darken_top)
    render_caption(img, text, colour, max_size, spacing, align, anchor_y)

    if branding:
        add_branding(img)

    out = os.path.join(OUT_DIR, out_name)
    img.save(out, "JPEG", quality=95)
    print(f"  ✓ {out_name}")

print("Building Reel 5 lifestyle frames...\n")

make_frame("01.jpg", "01_hollywood.jpg",
           "I DIDN'T START TRADING FOR MONEY.", WHITE, 64, anchor_y=int(H*0.13), darken_top=True)

make_frame("02.jpg", "02_car.jpg",
           "I STARTED FOR FREEDOM.", GOLD, 72, anchor_y=int(H*0.13))

make_frame("03.jpg", "03_pier.jpg",
           "TIME. LOCATION. NO BOSS. NO LIMITS.", WHITE, 56, anchor_y=int(H*0.13))

make_frame("04.jpg", "04_horizon.jpg",
           "MARKET STRUCTURE IS HOW I GOT HERE.", GOLD, 56, anchor_y=int(H*0.50),
           align="center", branding=True)

print(f"\nDone → {OUT_DIR}")
