#!/usr/bin/env python3
"""
Titus Trading Network — Instagram Carousel Generator
Produces 1080x1350px PNG slides. Edit SLIDES list to change content.
Run: python3 generate_carousel.py
"""

from PIL import Image, ImageDraw, ImageFont
import os, math

# ── Output ──────────────────────────────────────────────────────────────────
OUT_DIR = os.path.join(os.path.dirname(__file__), "market-structure", "output")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Dimensions ───────────────────────────────────────────────────────────────
W, H = 1080, 1350

# ── Brand colours ────────────────────────────────────────────────────────────
BG       = (10,  10,  15)
BG2      = (18,  19,  26)
GOLD     = (240, 180,  41)
BLUE     = (59,  130, 246)
WHITE    = (255, 255, 255)
GREY     = (156, 163, 175)
BORDER   = (30,  32,  48)
RED      = (239,  68,  68)

# ── Fonts ────────────────────────────────────────────────────────────────────
FONT_DIR = "/usr/share/fonts/truetype"

def load(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

BOLD_PATH  = f"{FONT_DIR}/liberation/LiberationSans-Bold.ttf"
REG_PATH   = f"{FONT_DIR}/liberation/LiberationSans-Regular.ttf"
SERIF_PATH = f"{FONT_DIR}/dejavu/DejaVuSerif-Bold.ttf"

F_BRAND    = load(BOLD_PATH,  26)
F_SLIDENUM = load(REG_PATH,   22)
F_HERO     = load(BOLD_PATH, 110)
F_HERO_MED = load(BOLD_PATH,  80)
F_HEAD     = load(BOLD_PATH,  64)
F_BODY     = load(REG_PATH,   30)
F_BODY_SM  = load(REG_PATH,   26)
F_LABEL    = load(BOLD_PATH,  22)
F_EYEBROW  = load(BOLD_PATH,  20)

# ── Helpers ───────────────────────────────────────────────────────────────────

def new_slide():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    _draw_grid(draw)
    return img, draw

def _draw_grid(draw):
    """Faint background grid lines."""
    step = 90
    for x in range(0, W, step):
        draw.line([(x, 0), (x, H)], fill=(240, 180, 41, 10), width=1)
    for y in range(0, H, step):
        draw.line([(0, y), (W, y)], fill=(240, 180, 41, 10), width=1)

def topbar(draw, slide_num=None):
    """Brand name + optional slide number + gold divider."""
    draw.text((60, 44), "— TITUS —", font=F_BRAND, fill=GOLD)
    if slide_num:
        label = f"0{slide_num} / 06"
        bbox = draw.textbbox((0, 0), label, font=F_SLIDENUM)
        tw = bbox[2] - bbox[0]
        draw.text((W - 60 - tw, 48), label, font=F_SLIDENUM, fill=GREY)
    draw.line([(60, 100), (W - 60, 100)], fill=GOLD, width=2)

def handle(draw):
    """@handle at bottom left."""
    draw.text((60, H - 60), "@titustradingnetwork", font=F_BODY_SM, fill=GREY)

def corner_marks(draw):
    """Decorative corner brackets."""
    s, t = 60, 3
    draw.line([(s, 120), (s, 120 + 60)], fill=GOLD, width=t)
    draw.line([(s, 120), (s + 60, 120)], fill=GOLD, width=t)
    draw.line([(W - s, H - 90), (W - s, H - 90 - 60)], fill=GOLD, width=t)
    draw.line([(W - s, H - 90), (W - s - 60, H - 90)], fill=GOLD, width=t)

def wrap_text(draw, text, font, max_width):
    """Split text into lines that fit within max_width."""
    words = text.split()
    lines, line = [], []
    for word in words:
        test = " ".join(line + [word])
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            line.append(word)
        else:
            if line:
                lines.append(" ".join(line))
            line = [word]
    if line:
        lines.append(" ".join(line))
    return lines

def draw_wrapped(draw, text, font, x, y, max_width, fill=WHITE, spacing=10):
    """Draw wrapped text and return final y position."""
    lines = wrap_text(draw, text, font, max_width)
    cy = y
    for ln in lines:
        draw.text((x, cy), ln, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), ln, font=font)
        cy += (bbox[3] - bbox[1]) + spacing
    return cy

def callout_box(draw, rows, y, x=60, w=W - 120):
    """Draw a dark bordered box with icon + text rows."""
    row_h   = 80
    pad_v   = 28
    total_h = pad_v * 2 + len(rows) * row_h
    draw.rounded_rectangle([x, y, x + w, y + total_h], radius=8, fill=BG2, outline=GOLD, width=1)
    cy = y + pad_v
    for icon, text, colour in rows:
        draw.text((x + 20, cy + 6), icon, font=F_BODY, fill=WHITE)
        tx = x + 70
        lines = wrap_text(draw, text, F_BODY, w - 100)
        line_h = draw.textbbox((0,0), "A", font=F_BODY)[3] + 4
        for i, ln in enumerate(lines[:2]):
            # Bold the coloured keyword (first word)
            parts = ln.split(" ", 1)
            draw.text((tx, cy + i * line_h), parts[0], font=F_LABEL, fill=colour)
            if len(parts) > 1:
                kw_w = draw.textbbox((0, 0), parts[0] + " ", font=F_LABEL)[2]
                draw.text((tx + kw_w, cy + i * line_h), parts[1], font=F_BODY, fill=WHITE)
        cy += row_h
    return y + total_h + 24

def glow(img, cx, cy, radius, colour, alpha=30):
    """Add a soft radial glow using a blended layer."""
    layer = Image.new("RGB", (W, H), BG)
    ld = ImageDraw.Draw(layer)
    steps = 8
    for i in range(steps, 0, -1):
        r = int(radius * i / steps)
        a = int(alpha * (1 - i / steps))
        c = tuple(min(255, int(colour[ch] * a / 255) + BG[ch]) for ch in range(3))
        ld.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
    img.paste(layer, mask=layer.convert("L"))

# ── Slide builders ────────────────────────────────────────────────────────────

def slide_1():
    img, draw = new_slide()
    glow(img, W // 2, H // 2, 600, GOLD, alpha=60)
    corner_marks(draw)
    topbar(draw)
    draw.text((W // 2, 200), "MARKET STRUCTURE", font=F_EYEBROW, fill=GOLD,
              anchor="mm")
    draw_wrapped(draw, "Every trader needs to know this first.", F_HERO,
                 60, 340, W - 120, fill=WHITE, spacing=8)
    draw.line([(60, 700), (W - 60, 700)], fill=GOLD, width=2)
    draw_wrapped(draw,
        "Before you place another trade — understand the foundation every profitable setup is built on.",
        F_BODY, 60, 730, W - 120, fill=GREY, spacing=8)
    # Swipe button
    bx1, by1, bx2, by2 = 60, 1050, 440, 1120
    draw.rounded_rectangle([bx1, by1, bx2, by2], radius=6, fill=BLUE)
    draw.text(((bx1 + bx2) // 2, (by1 + by2) // 2), "Swipe to learn  →",
              font=F_LABEL, fill=WHITE, anchor="mm")
    handle(draw)
    return img

def slide_2():
    img, draw = new_slide()
    glow(img, 0, 500, 400, GOLD, alpha=40)
    topbar(draw, 2)
    y = 140
    y = draw_wrapped(draw, "What is Market Structure?", F_HEAD, 60, y, W - 120,
                     fill=WHITE, spacing=6) + 20
    y = draw_wrapped(draw,
        "Market structure is how price moves — it tells you whether buyers or sellers are in control.",
        F_BODY, 60, y, W - 120, fill=GREY, spacing=8) + 30
    y = callout_box(draw, [
        ("📈", "Uptrend  Higher Highs + Higher Lows. Buyers winning.", GOLD),
        ("📉", "Downtrend  Lower Highs + Lower Lows. Sellers winning.", BLUE),
        ("⚠️",  "Ranging  Price bouncing between the same levels.", GREY),
    ], y)
    draw_wrapped(draw, "Master this — and you'll always know who is winning before you enter.",
                 F_BODY_SM, 60, y + 10, W - 120, fill=GREY)
    handle(draw)
    return img

def slide_3():
    img, draw = new_slide()
    glow(img, W, 400, 400, BLUE, alpha=40)
    topbar(draw, 3)
    y = 140
    y = draw_wrapped(draw, "Break of Structure (BOS)", F_HEAD, 60, y, W - 120,
                     fill=WHITE, spacing=6) + 20
    y = draw_wrapped(draw,
        "A BOS is when price breaks a key swing high or low — signalling a potential shift in trend.",
        F_BODY, 60, y, W - 120, fill=GREY, spacing=8) + 30
    y = callout_box(draw, [
        ("🔼", "Bullish BOS  Price breaks above swing high. Look for buys.", GOLD),
        ("🔽", "Bearish BOS  Price breaks below swing low. Look for sells.", BLUE),
        ("⚡", "CHoCH  Change of Character. First sign of reversal.", RED),
    ], y)
    draw_wrapped(draw, "BOS = confirmation.  CHoCH = warning.  Know the difference.",
                 F_BODY_SM, 60, y + 10, W - 120, fill=GREY)
    handle(draw)
    return img

def slide_4():
    img, draw = new_slide()
    glow(img, W, H, 400, GOLD, alpha=40)
    topbar(draw, 4)
    y = 140
    y = draw_wrapped(draw, "How to Trade It", F_HEAD, 60, y, W - 120,
                     fill=WHITE, spacing=6) + 20
    y = draw_wrapped(draw, "Don't just spot the structure — trade it with a clear process.",
                     F_BODY, 60, y, W - 120, fill=GREY, spacing=8) + 30
    y = callout_box(draw, [
        ("1️⃣", "Higher TF  Identify trend on H4 or Daily timeframe.", GOLD),
        ("2️⃣", "Signal  Wait for BOS or CHoCH on 15m or 1H chart.", BLUE),
        ("3️⃣", "Entry  Enter on retest of the broken structure level.", GOLD),
        ("4️⃣", "Risk  SL below swing low. Target next key level.", BLUE),
    ], y)
    handle(draw)
    return img

def slide_5_chart():
    """Chart slide — draws a synthetic price action chart with annotations."""
    img, draw = new_slide()
    topbar(draw, 5)

    # Chart area
    cx, cy, cw, ch = 60, 140, W - 120, 920
    draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=8, fill=BG2, outline=BORDER, width=1)

    # Price path points (normalised 0-1)
    pts_norm = [
        (0.00, 0.80), (0.08, 0.72), (0.14, 0.76), (0.22, 0.58),
        (0.28, 0.64), (0.36, 0.42), (0.44, 0.36), (0.50, 0.48),  # Wave 2 pullback
        (0.58, 0.20), (0.66, 0.14), (0.72, 0.28), (0.78, 0.34),  # Wave 3 up
        (0.86, 0.55), (0.92, 0.38), (1.00, 0.30),
    ]
    pad = 60
    def to_px(nx, ny):
        return (cx + pad + int(nx * (cw - pad * 2)),
                cy + pad + int(ny * (ch - pad * 2)))

    pts = [to_px(nx, ny) for nx, ny in pts_norm]

    # Glow under line
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i + 1]], fill=(240, 180, 41, 40), width=12)

    # Main price line
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i + 1]], fill=GOLD, width=3)

    # Dots at key points
    key_pts = [pts[0], pts[3], pts[7], pts[8], pts[11]]
    for p in key_pts:
        draw.ellipse([p[0]-6, p[1]-6, p[0]+6, p[1]+6], fill=GOLD)

    # BOS annotation
    bos_x = pts[8][0]
    bos_y_top = pts[8][1] - 30
    bos_y_bot = pts[7][1] + 10
    draw.line([(bos_x, bos_y_top), (bos_x, bos_y_bot)], fill=BLUE, width=2)
    draw.rectangle([bos_x - 2, bos_y_top - 34, bos_x + 80, bos_y_top], fill=BLUE)
    draw.text((bos_x + 4, bos_y_top - 30), " BOS ", font=F_LABEL, fill=WHITE)

    # CHoCH annotation
    choch_x = pts[11][0]
    choch_y = pts[11][1] - 30
    draw.line([(choch_x, choch_y), (choch_x, pts[12][1])], fill=RED, width=2)
    draw.rectangle([choch_x - 2, choch_y - 34, choch_x + 110, choch_y], fill=RED)
    draw.text((choch_x + 4, choch_y - 30), " CHoCH ", font=F_LABEL, fill=WHITE)

    # Horizontal structure level
    sl_y = pts[3][1]
    draw.line([(cx + pad, sl_y), (pts[7][0], sl_y)], fill=GREY, width=1)
    draw.text((cx + pad + 5, sl_y - 28), "Structure Level", font=F_BODY_SM, fill=GREY)

    # Entry zone box
    ez_x1, ez_y1 = pts[7][0], pts[7][1]
    ez_x2, ez_y2 = pts[8][0], pts[3][1]
    draw.rectangle([ez_x1, ez_y1, ez_x2, ez_y2],
                   outline=(59, 130, 246, 80), width=2)
    draw.text((ez_x1 + 8, (ez_y1 + ez_y2) // 2 - 14), "Entry\nZone", font=F_BODY_SM, fill=BLUE)

    draw_wrapped(draw, "BOS confirmed → retest of structure → clean entry zone formed.",
                 F_BODY_SM, 60, cy + ch + 20, W - 120, fill=GREY)
    handle(draw)
    return img

def slide_6():
    img, draw = new_slide()
    glow(img, W // 2, H // 2, 700, GOLD, alpha=70)
    corner_marks(draw)
    topbar(draw)
    draw.text((W // 2, 230), "— TITUS —", font=F_BRAND, fill=GOLD, anchor="mm")

    y = 320
    for line in ["FOLLOW FOR", "DAILY SETUPS", "& BREAKDOWNS."]:
        color = GOLD if line == "& BREAKDOWNS." else WHITE
        bbox = draw.textbbox((0, 0), line, font=F_HERO_MED)
        lw = bbox[2] - bbox[0]
        draw.text(((W - lw) // 2, y), line, font=F_HERO_MED, fill=color)
        y += (bbox[3] - bbox[1]) + 12

    draw.text((W // 2, y + 30), "No gatekeeping. Just real trading education.",
              font=F_BODY, fill=GREY, anchor="mm")

    # Community box
    bx1, by1, bx2, by2 = 120, y + 90, W - 120, y + 220
    draw.rounded_rectangle([bx1, by1, bx2, by2], radius=8, fill=BG2, outline=GOLD, width=2)
    draw.text((W // 2, by1 + 30), "FREE COMMUNITY", font=F_LABEL, fill=GOLD, anchor="mm")
    draw.text((W // 2, by1 + 80), "t.me/titus_net", font=F_HEAD, fill=WHITE, anchor="mm")

    draw.text((W // 2, by2 + 50), "Drop a 📊 if this helped you →",
              font=F_BODY_SM, fill=GREY, anchor="mm")
    handle(draw)
    return img

# ── Generate all slides ───────────────────────────────────────────────────────

slides = [
    ("titus_carousel_1_hook.png",        slide_1),
    ("titus_carousel_2_structure.png",   slide_2),
    ("titus_carousel_3_bos.png",         slide_3),
    ("titus_carousel_4_entry.png",       slide_4),
    ("titus_carousel_5_chart.png",       slide_5_chart),
    ("titus_carousel_6_cta.png",         slide_6),
]

print("Generating Titus Trading Network carousel slides...\n")
for filename, builder in slides:
    img = builder()
    path = os.path.join(OUT_DIR, filename)
    img.save(path, "PNG", quality=95)
    print(f"  ✓  {filename}")

print(f"\nAll slides saved to: {OUT_DIR}")
