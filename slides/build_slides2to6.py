#!/usr/bin/env python3
"""
Build slides 2-6 using TradingView chart as background.
@asianriches style: dark gradient overlay, bold caps, gold highlights, logo.
Auto-fit fonts so all text stays within Instagram 1080x1350 frame.
"""

from PIL import Image, ImageDraw, ImageFont, ImageOps
import os

W, H      = 1080, 1080
PAD       = 60
MAX_W     = W - PAD * 2    # 960px usable width
OUT_DIR   = os.path.join(os.path.dirname(__file__), "market-structure", "output")
BG_PATH   = os.path.join(os.path.dirname(__file__), "bg_chart.jpg")
LOGO_PATH = os.path.join(os.path.dirname(__file__), "titus_logo_transparent.png")
TG_PATH   = os.path.join(os.path.dirname(__file__), "telegram_logo.png")
FONT_DIR  = os.path.join(os.path.dirname(__file__), "fonts")
BOLD      = f"{FONT_DIR}/BigShoulders-Bold.ttf"

GOLD  = (240, 180,  41)
WHITE = (255, 255, 255)
GREY  = (200, 200, 200)

def load(size):
    try:    return ImageFont.truetype(BOLD, size)
    except: return ImageFont.load_default()

def fit_font(draw, text, max_size=90, min_size=32):
    """Return largest font where text fits within MAX_W."""
    for size in range(max_size, min_size - 1, -2):
        f = load(size)
        if draw.textbbox((0,0), text, font=f)[2] <= MAX_W:
            return f
    return load(min_size)

def tw(draw, text, font):
    return draw.textbbox((0,0), text, font=font)[2]

def lh(draw, font, gap=10):
    return draw.textbbox((0,0), "A", font=font)[3] + gap

def bold_text(draw, x, y, text, font, fill):
    """Draw text with stroke to simulate extra-bold weight."""
    stroke = 2
    for dx in range(-stroke, stroke + 1):
        for dy in range(-stroke, stroke + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=(0, 0, 0))
    draw.text((x, y), text, font=font, fill=fill)

def centred(draw, text, font, y, fill=WHITE):
    x = (W - tw(draw, text, font)) // 2
    bold_text(draw, x, y, text, font, fill)
    return y + lh(draw, font)

def mixed(draw, segments, font, y):
    total = sum(tw(draw, t, font) for t, _ in segments)
    x     = (W - total) // 2
    for text, colour in segments:
        draw.text((x, y), text, font=font, fill=colour)
        x += tw(draw, text, font)
    return y + lh(draw, font)

def make_bg(extra_dark=False):
    bg      = Image.open(BG_PATH).convert("RGB")
    scale_w = W / bg.width
    scale_h = H / bg.height
    scale   = max(scale_w, scale_h)
    new_w   = int(bg.width  * scale)
    new_h   = int(bg.height * scale)
    bg      = bg.resize((new_w, new_h), Image.LANCZOS)
    left    = (new_w - W) // 2
    top     = (new_h - H) // 2
    bg      = bg.crop((left, top, left + W, top + H))

    overlay  = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od       = ImageDraw.Draw(overlay)
    base     = 195 if extra_dark else 170   # flat darken across whole frame, hides chart price axis
    extra    = 55                             # additional darkening toward the bottom
    grad_top = int(H * 0.18)
    for y in range(H):
        if y < grad_top:
            alpha = base
        else:
            p     = (y - grad_top) / (H - grad_top)
            alpha = min(base + int(extra * min(p * 1.4, 1.0)), 250)
        od.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))

    return Image.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")

def add_bottom(slide, slide_num=None):
    """Add logo, Telegram handle and optional slide number."""
    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo.thumbnail((150, 150), Image.LANCZOS)
    lw2, lh2 = logo.size
    ly        = H - lh2 - 70
    slide.paste(logo, ((W - lw2)//2, ly), logo)

    tg_icon = Image.open(TG_PATH).convert("RGBA")
    tg_icon.thumbnail((40, 40), Image.LANCZOS)
    iw, ih  = tg_icon.size
    draw    = ImageDraw.Draw(slide)
    tg_font = load(30)
    tg_text = "@titus.net"
    tgw     = tw(draw, tg_text, tg_font)
    total   = iw + 10 + tgw
    xs      = (W - total) // 2
    ty      = H - 40
    slide.paste(tg_icon, (xs, ty - ih//2 + 8), tg_icon)
    draw = ImageDraw.Draw(slide)
    draw.text((xs + iw + 10, ty - 2), tg_text, font=tg_font, fill=GOLD)

    if slide_num:
        label = f"{slide_num} / 6"
        sf    = load(28)
        draw.text((W - PAD - tw(draw, label, sf), 44), label, font=sf, fill=GREY)

    return ly   # return top of logo so text stays above it

def draw_block(draw, lines, text_top, text_bot):
    """
    lines = [(text, max_font_size, colour), ...]
    Auto-fits each line by width, then shrinks the whole block proportionally
    if needed so it always fits vertically in [text_top, text_bot] without
    overlapping the logo, then stacks them centred.
    """
    avail = text_bot - text_top
    scale = 1.0
    fitted, total_h = [], 0
    while True:
        fitted = [(text, fit_font(draw, text, max(int(max_size * scale), 22)), colour)
                  for text, max_size, colour in lines]
        total_h = sum(lh(draw, f) for _, f, _ in fitted)
        if total_h <= avail or scale <= 0.4:
            break
        scale -= 0.05

    y = text_top + max(0, (avail - total_h) // 2)
    for text, font, colour in fitted:
        y = centred(draw, text, font, y, fill=colour)

# ── Slide builders ─────────────────────────────────────────────────────────────

def build_slide2():
    bg  = make_bg()
    ly  = add_bottom(bg, slide_num=2)
    d   = ImageDraw.Draw(bg)
    draw_block(d, [
        ("WHAT IS",             88, WHITE),
        ("MARKET STRUCTURE?",   88, GOLD),
        ("THE FOUNDATION EVERY", 72, WHITE),
        ("PROFITABLE TRADE",    72, WHITE),
        ("IS BUILT ON.",        72, WHITE),
        ("UPTREND",             60, GOLD),
        ("Higher Highs and Higher Lows", 44, GREY),
        ("DOWNTREND",           60, GOLD),
        ("Lower Highs and Lower Lows",   44, GREY),
        ("RANGING",             60, GOLD),
        ("Price stuck between the same levels", 40, GREY),
    ], int(H * 0.28), ly - 20)
    return bg

def build_slide3():
    bg  = make_bg()
    ly  = add_bottom(bg, slide_num=3)
    d   = ImageDraw.Draw(bg)
    draw_block(d, [
        ("BREAK OF STRUCTURE",        88, WHITE),
        ("WHEN PRICE BREAKS A KEY",   72, WHITE),
        ("LEVEL IT IS TELLING YOU",   72, WHITE),
        ("SOMETHING IS CHANGING.",    72, GOLD),
        ("BULLISH BOS",               60, GOLD),
        ("Price breaks above swing high", 44, GREY),
        ("BEARISH BOS",               60, GOLD),
        ("Price breaks below swing low",  44, GREY),
        ("CHANGE OF CHARACTER",       60, GOLD),
        ("First sign the trend is flipping", 40, GREY),
    ], int(H * 0.28), ly - 20)
    return bg

def build_slide4():
    bg  = make_bg()
    ly  = add_bottom(bg, slide_num=4)
    d   = ImageDraw.Draw(bg)
    draw_block(d, [
        ("HOW TO TRADE IT RIGHT",     88, WHITE),
        ("A SIMPLE 4 STEP PROCESS",   60, GREY),
        ("STEP 1  IDENTIFY THE TREND", 60, GOLD),
        ("Use 4 Hour or Daily first",  44, GREY),
        ("STEP 2  WAIT FOR SIGNAL",    60, GOLD),
        ("BOS or Change of Character on 15m", 40, GREY),
        ("STEP 3  ENTER ON RETEST",    60, GOLD),
        ("Wait for price to retest broken level", 40, GREY),
        ("STEP 4  MANAGE YOUR RISK",   60, GOLD),
        ("SL below swing low. Target next key level", 38, GREY),
    ], int(H * 0.28), ly - 20)
    return bg

def build_slide5():
    bg  = make_bg(extra_dark=True)
    ly  = add_bottom(bg, slide_num=5)
    d   = ImageDraw.Draw(bg)
    draw_block(d, [
        ("THIS IS WHAT A",            88, WHITE),
        ("PERFECT ENTRY",             96, GOLD),
        ("LOOKS LIKE ON A CHART.",    80, WHITE),
        ("BOS CONFIRMED ON H1",       60, GOLD),
        ("Price retested broken structure", 44, GREY),
        ("ENTRY ZONE FORMED",         60, GOLD),
        ("Clean low risk entry with tight SL", 40, GREY),
        ("TARGET HIT",                60, GOLD),
        ("Next key level taken out",  44, GREY),
    ], int(H * 0.28), ly - 20)
    return bg

def build_slide6():
    bg  = make_bg(extra_dark=True)
    ly  = add_bottom(bg)
    d   = ImageDraw.Draw(bg)
    draw_block(d, [
        ("IF THIS HELPED YOU",        80, WHITE),
        ("FOLLOW FOR MORE",           90, WHITE),
        ("DAILY SETUPS.",             88, WHITE),
        ("REAL EDUCATION.",           88, WHITE),
        ("NO GATEKEEPING.",           88, GOLD),
        ("JOIN THE FREE TELEGRAM",    60, WHITE),
        ("DROP A COMMENT BELOW",      44, GREY),
    ], int(H * 0.25), ly - 20)
    return bg

# ── Generate ───────────────────────────────────────────────────────────────────

slides = [
    ("titus_carousel_2_structure.jpg", build_slide2),
    ("titus_carousel_3_bos.jpg",       build_slide3),
    ("titus_carousel_4_entry.jpg",     build_slide4),
    ("titus_carousel_5_chart.jpg",     build_slide5),
    ("titus_carousel_6_cta.jpg",       build_slide6),
]

print("Building slides 2-6...\n")
for fname, builder in slides:
    img  = builder()
    path = os.path.join(OUT_DIR, fname)
    img.save(path, "JPEG", quality=95)
    print(f"  ✓  {fname}")

print(f"\nDone → {OUT_DIR}")
