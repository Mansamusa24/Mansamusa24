#!/usr/bin/env python3
"""
Build slides 2-6 using TradingView chart as background.
Same @asianriches style: dark gradient overlay, bold caps, gold highlights, logo.
"""

from PIL import Image, ImageDraw, ImageFont
import os

W, H      = 1080, 1350
OUT_DIR   = os.path.join(os.path.dirname(__file__), "market-structure", "output")
BG_PATH   = os.path.join(os.path.dirname(__file__), "bg_chart.jpg")
LOGO_PATH = os.path.join(os.path.dirname(__file__), "titus_logo_transparent.png")
FONT_DIR  = "/usr/share/fonts/truetype"
BOLD      = f"{FONT_DIR}/liberation/LiberationSans-Bold.ttf"

GOLD  = (240, 180,  41)
WHITE = (255, 255, 255)
GREY  = (200, 200, 200)

def load(path, size):
    try:    return ImageFont.truetype(path, size)
    except: return ImageFont.load_default()

F_XL   = load(BOLD, 90)
F_LG   = load(BOLD, 76)
F_MD   = load(BOLD, 62)
F_SM   = load(BOLD, 48)
F_XS   = load(BOLD, 36)
F_TINY = load(BOLD, 26)

# ── Shared helpers ─────────────────────────────────────────────────────────────

def make_bg(extra_dark=False):
    """Return cropped, resized chart background."""
    bg    = Image.open(BG_PATH).convert("RGB")
    scale = W / bg.width
    new_h = int(bg.height * scale)
    bg    = bg.resize((W, new_h), Image.LANCZOS)
    if new_h >= H:
        bg = bg.crop((0, 0, W, H))
    else:
        canvas = Image.new("RGB", (W, H), (5, 8, 20))
        canvas.paste(bg, (0, 0))
        bg = canvas

    overlay  = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od       = ImageDraw.Draw(overlay)
    darkness = 240 if extra_dark else 210
    grad_top = int(H * 0.22)
    for y in range(grad_top, H):
        p     = (y - grad_top) / (H - grad_top)
        alpha = int(darkness * min(p * 1.5, 1.0))
        od.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))

    # Also darken the top a little so text area is readable
    for y in range(0, grad_top):
        p     = 1 - (y / grad_top)
        alpha = int(80 * p)
        od.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))

    return Image.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")

def tw(draw, text, font):
    return draw.textbbox((0,0), text, font=font)[2]

def lh(draw, font, gap=6):
    return draw.textbbox((0,0), "A", font=font)[3] + gap

def centred(draw, text, font, y, fill=WHITE):
    x = (W - tw(draw, text, font)) // 2
    draw.text((x, y), text, font=font, fill=fill)
    return y + lh(draw, font)

def mixed(draw, segments, font, y, gap=6):
    total = sum(tw(draw, t, font) for t, _ in segments)
    x     = (W - total) // 2
    for text, colour in segments:
        draw.text((x, y), text, font=font, fill=colour)
        x += tw(draw, text, font)
    return y + lh(draw, font, gap)

def add_logo(slide, y_bottom, size=150):
    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo.thumbnail((size, size), Image.LANCZOS)
    lw2, lh2 = logo.size
    slide.paste(logo, ((W - lw2)//2, y_bottom - lh2 - 20), logo)
    draw = ImageDraw.Draw(slide)
    handle = "@titustradingnetwork"
    draw.text(((W - tw(draw, handle, F_TINY))//2, y_bottom - 22),
              handle, font=F_TINY, fill=GREY)

def slide_number(draw, n):
    label = f"{n} / 6"
    draw.text((W - tw(draw, label, F_TINY) - 40, 40), label, font=F_TINY, fill=GREY)

# ── Slide 2: What is Market Structure ─────────────────────────────────────────

def build_slide2():
    bg   = make_bg()
    draw = ImageDraw.Draw(bg)
    slide_number(draw, 2)

    y = int(H * 0.33)
    y = mixed(draw, [("WHAT IS ", WHITE), ("MARKET", GOLD)], F_XL, y) + 4
    y = centred(draw, "STRUCTURE?", F_XL, y, GOLD)
    y += 20
    y = centred(draw, "THE FOUNDATION EVERY", F_MD, y)
    y = centred(draw, "PROFITABLE TRADE IS", F_MD, y)
    y = centred(draw, "BUILT ON.", F_MD, y)
    y += 24
    y = centred(draw, "UPTREND", F_SM, y, GOLD)
    y = centred(draw, "Higher Highs and Higher Lows", F_XS, y, GREY)
    y += 10
    y = centred(draw, "DOWNTREND", F_SM, y, GOLD)
    y = centred(draw, "Lower Highs and Lower Lows", F_XS, y, GREY)
    y += 10
    y = centred(draw, "RANGING", F_SM, y, GOLD)
    y = centred(draw, "Price stuck between the same levels", F_XS, y, GREY)

    add_logo(bg, H - 10)
    return bg

# ── Slide 3: Break of Structure ───────────────────────────────────────────────

def build_slide3():
    bg   = make_bg()
    draw = ImageDraw.Draw(bg)
    slide_number(draw, 3)

    y = int(H * 0.33)
    y = centred(draw, "BREAK OF", F_XL, y)
    y = mixed(draw, [("STRUCTURE ", WHITE), ("(BOS)", GOLD)], F_XL, y) + 4
    y += 18
    y = centred(draw, "WHEN PRICE BREAKS A KEY", F_MD, y)
    y = centred(draw, "LEVEL IT IS TELLING YOU", F_MD, y)
    y = mixed(draw, [("SOMETHING IS ", WHITE), ("CHANGING.", GOLD)], F_MD, y)
    y += 20
    y = centred(draw, "BULLISH BOS", F_SM, y, GOLD)
    y = centred(draw, "Price breaks above swing high", F_XS, y, GREY)
    y += 8
    y = centred(draw, "BEARISH BOS", F_SM, y, GOLD)
    y = centred(draw, "Price breaks below swing low", F_XS, y, GREY)
    y += 8
    y = centred(draw, "CHANGE OF CHARACTER", F_SM, y, GOLD)
    y = centred(draw, "First sign the trend is flipping", F_XS, y, GREY)

    add_logo(bg, H - 10)
    return bg

# ── Slide 4: How To Trade It ──────────────────────────────────────────────────

def build_slide4():
    bg   = make_bg()
    draw = ImageDraw.Draw(bg)
    slide_number(draw, 4)

    y = int(H * 0.33)
    y = centred(draw, "HOW TO", F_XL, y)
    y = mixed(draw, [("TRADE IT ", WHITE), ("RIGHT", GOLD)], F_XL, y) + 4
    y += 18
    y = centred(draw, "A SIMPLE 4 STEP PROCESS", F_MD, y, GREY)
    y += 24
    y = mixed(draw, [("STEP 1  ", GOLD), ("IDENTIFY THE TREND", WHITE)], F_SM, y)
    y = centred(draw, "Use H4 or Daily timeframe first", F_XS, y, GREY)
    y += 14
    y = mixed(draw, [("STEP 2  ", GOLD), ("WAIT FOR THE SIGNAL", WHITE)], F_SM, y)
    y = centred(draw, "BOS or Change of Character on 15m or 1H", F_XS, y, GREY)
    y += 14
    y = mixed(draw, [("STEP 3  ", GOLD), ("ENTER ON THE RETEST", WHITE)], F_SM, y)
    y = centred(draw, "Wait for price to retest broken level", F_XS, y, GREY)
    y += 14
    y = mixed(draw, [("STEP 4  ", GOLD), ("MANAGE YOUR RISK", WHITE)], F_SM, y)
    y = centred(draw, "SL below swing low. Target next key level", F_XS, y, GREY)

    add_logo(bg, H - 10)
    return bg

# ── Slide 5: Chart Breakdown ──────────────────────────────────────────────────

def build_slide5():
    bg   = make_bg(extra_dark=True)
    draw = ImageDraw.Draw(bg)
    slide_number(draw, 5)

    y = int(H * 0.35)
    y = centred(draw, "THIS IS WHAT A", F_LG, y)
    y = mixed(draw, [("PERFECT ", WHITE), ("ENTRY", GOLD)], F_XL, y) + 4
    y = centred(draw, "LOOKS LIKE ON A CHART.", F_LG, y)
    y += 24
    y = centred(draw, "BOS CONFIRMED ON H1", F_SM, y, GOLD)
    y = centred(draw, "Price retested broken structure", F_XS, y, GREY)
    y += 14
    y = centred(draw, "ENTRY ZONE FORMED", F_SM, y, GOLD)
    y = centred(draw, "Clean low risk entry with tight SL", F_XS, y, GREY)
    y += 14
    y = centred(draw, "TARGET HIT", F_SM, y, GOLD)
    y = centred(draw, "Next key level taken out", F_XS, y, GREY)

    add_logo(bg, H - 10)
    return bg

# ── Slide 6: CTA ──────────────────────────────────────────────────────────────

def build_slide6():
    bg   = make_bg(extra_dark=True)
    draw = ImageDraw.Draw(bg)

    y = int(H * 0.30)
    y = centred(draw, "IF THIS HELPED YOU", F_LG, y)
    y = mixed(draw, [("FOLLOW ", WHITE), ("@TITUSTRADINGNETWORK", GOLD)], F_MD, y) + 4
    y += 16
    y = centred(draw, "DAILY SETUPS.", F_XL, y, WHITE)
    y = centred(draw, "REAL EDUCATION.", F_XL, y, WHITE)
    y = centred(draw, "NO GATEKEEPING.", F_XL, y, GOLD)
    y += 28
    y = centred(draw, "FREE COMMUNITY", F_SM, y, GOLD)
    y = centred(draw, "t.me/titus_net", F_MD, y, WHITE)
    y += 20
    y = centred(draw, "DROP A 📊 IN THE COMMENTS", F_XS, y, GREY)

    add_logo(bg, H - 10)
    return bg

# ── Generate all ───────────────────────────────────────────────────────────────

slides = [
    ("titus_carousel_2_structure.png", build_slide2),
    ("titus_carousel_3_bos.png",       build_slide3),
    ("titus_carousel_4_entry.png",     build_slide4),
    ("titus_carousel_5_chart.png",     build_slide5),
    ("titus_carousel_6_cta.png",       build_slide6),
]

print("Building slides 2-6...\n")
for fname, builder in slides:
    img  = builder()
    path = os.path.join(OUT_DIR, fname)
    img.save(path, "PNG")
    print(f"  ✓  {fname}")

print(f"\nDone. Saved to {OUT_DIR}")
