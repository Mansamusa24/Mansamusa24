#!/usr/bin/env python3
"""
Build an Instagram Story for a live BTCUSD setup watch: chart screenshot
with a branded header (covering the TradingView chrome) and a caption
calling out the confluence + confirmation being watched for.
"""

from PIL import Image, ImageDraw, ImageFont
import os

W, H      = 1080, 1920
BASE_DIR  = os.path.dirname(__file__)
SRC       = os.path.join(BASE_DIR, "stories", "source", "btc_fib_watch.jpeg")
OUT_DIR   = os.path.join(BASE_DIR, "stories", "output")
LOGO_PATH = os.path.join(BASE_DIR, "titus_logo_transparent.png")
TG_PATH   = os.path.join(BASE_DIR, "telegram_logo.png")
FONT_DIR  = os.path.join(BASE_DIR, "fonts")
BOLD      = f"{FONT_DIR}/Anton-Regular.ttf"
os.makedirs(OUT_DIR, exist_ok=True)

GOLD  = (240, 180, 41)
WHITE = (255, 255, 255)

PAD   = 70
MAX_W = W - PAD * 2

def load(size):
    try:    return ImageFont.truetype(BOLD, size)
    except: return ImageFont.load_default()

def tw(draw, text, font):
    return draw.textbbox((0, 0), text, font=font)[2]

def fit_font(draw, text, max_size, min_size=36):
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

def make_bg():
    img = Image.open(SRC).convert("RGB")
    scale = max(W / img.width, H / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - W) // 2, (nh - H) // 2
    return img.crop((left, top, left + W, top + H))

def add_branding(img):
    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo.thumbnail((110, 110), Image.LANCZOS)
    lw, lh_ = logo.size
    ly = H - lh_ - 95
    img.paste(logo, ((W - lw) // 2, ly), logo)

    tg = Image.open(TG_PATH).convert("RGBA")
    tg.thumbnail((32, 32), Image.LANCZOS)
    iw, ih = tg.size
    draw = ImageDraw.Draw(img)
    font = load(26)
    text = "@titus.net"
    tgw  = tw(draw, text, font)
    total = iw + 8 + tgw
    xs = (W - total) // 2
    ty = H - 50
    img.paste(tg, (xs, ty - ih // 2 + 5), tg)
    draw.text((xs + iw + 8, ty - 2), text, font=font, fill=GOLD)

def build():
    img = make_bg().convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Header bar covers the TradingView chrome and carries our own caption.
    header_h = 300
    draw.rectangle([0, 0, W, header_h], fill=(8, 9, 12, 255))

    tag_font = load(34)
    draw.text((PAD, 54), "BTCUSD  ·  LIVE WATCH", font=tag_font, fill=GOLD)

    headline = "FIB SUPPORT REACTION"
    h_font   = fit_font(draw, headline, 80)
    lines    = wrap_text(draw, headline, h_font, MAX_W)
    line_h   = draw.textbbox((0, 0), "A", font=h_font)[3] + 12
    y = 110
    for line in lines:
        x = (W - tw(draw, line, h_font)) // 2
        draw.text((x, y), line, font=h_font, fill=WHITE)
        y += line_h

    rule_w = 70
    draw.rectangle([(W - rule_w) // 2, header_h - 26, (W + rule_w) // 2, header_h - 23], fill=GOLD)

    # Bottom gradient + caption + branding.
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    grad_top = int(H * 0.62)
    for y in range(grad_top, H):
        p = (y - grad_top) / (H - grad_top)
        alpha = int(40 + 195 * p)
        od.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    caption = "LIQUIDITY SWEEP + MSS = TRIGGER"
    c_font  = fit_font(draw, caption, 58)
    c_lines = wrap_text(draw, caption, c_font, MAX_W)
    c_lh    = draw.textbbox((0, 0), "A", font=c_font)[3] + 14
    c_total = c_lh * len(c_lines)
    cy = H - 270 - c_total
    for line in c_lines:
        x = (W - tw(draw, line, c_font)) // 2
        draw.text((x, cy), line, font=c_font, fill=GOLD)
        cy += c_lh

    img = img.convert("RGB")
    add_branding(img)

    out = os.path.join(OUT_DIR, "btc_fib_watch.jpg")
    img.save(out, "JPEG", quality=95)
    print(f"  ✓ {out}")

print("Building BTC fib-watch story...\n")
build()
