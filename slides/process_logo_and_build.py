#!/usr/bin/env python3
"""
Strip logo background via flood-fill, then composite onto all 6 carousel slides.
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
from collections import deque
import os

LOGO_SRC  = os.path.join(os.path.dirname(__file__), "titus_logo_original.png")
LOGO_OUT  = os.path.join(os.path.dirname(__file__), "titus_logo_transparent.png")
OUT_DIR   = os.path.join(os.path.dirname(__file__), "market-structure", "output")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Brand colours ─────────────────────────────────────────────────────────────
BG    = (10,  10,  15)
BG2   = (18,  19,  26)
GOLD  = (240, 180,  41)
BLUE  = (59,  130, 246)
WHITE = (255, 255, 255)
GREY  = (156, 163, 175)
RED   = (239,  68,  68)
W, H  = 1080, 1350

FONT_DIR  = "/usr/share/fonts/truetype"
BOLD_PATH = f"{FONT_DIR}/liberation/LiberationSans-Bold.ttf"
REG_PATH  = f"{FONT_DIR}/liberation/LiberationSans-Regular.ttf"

def load(path, size):
    try:    return ImageFont.truetype(path, size)
    except: return ImageFont.load_default()

F_BRAND   = load(BOLD_PATH, 26)
F_LABEL   = load(BOLD_PATH, 22)
F_EYEBROW = load(BOLD_PATH, 20)
F_HERO    = load(BOLD_PATH, 96)
F_HERO_MD = load(BOLD_PATH, 76)
F_HEAD    = load(BOLD_PATH, 60)
F_BODY    = load(REG_PATH,  30)
F_BODY_SM = load(REG_PATH,  26)

# ── Step 1: Remove background via flood-fill ──────────────────────────────────

def flood_fill_alpha(img, seeds, tolerance=22):
    """Remove background starting from seed pixels using BFS flood fill."""
    rgba  = img.convert("RGBA")
    data  = np.array(rgba, dtype=np.int32)
    alpha = np.ones((img.height, img.width), dtype=bool)  # True = keep
    visited = np.zeros((img.height, img.width), dtype=bool)

    queue = deque()
    for sx, sy in seeds:
        if not visited[sy, sx]:
            queue.append((sx, sy))
            visited[sy, sx] = True

    bg_color = data[seeds[0][1], seeds[0][0], :3]

    while queue:
        x, y = queue.popleft()
        pixel = data[y, x, :3]
        dist  = float(np.sqrt(np.sum((pixel - bg_color) ** 2)))
        if dist < tolerance:
            alpha[y, x] = False
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < img.width and 0 <= ny < img.height and not visited[ny, nx]:
                    visited[ny, nx] = True
                    queue.append((nx, ny))

    out = np.array(rgba)
    out[:, :, 3] = np.where(alpha, 255, 0)
    return Image.fromarray(out, "RGBA")

print("Removing logo background...")
logo_orig = Image.open(LOGO_SRC)
lw, lh    = logo_orig.size

seeds = [
    (0, 0), (lw-1, 0), (0, lh-1), (lw-1, lh-1),
    (lw//2, 0), (0, lh//2), (lw-1, lh//2), (lw//2, lh-1),
    (10, 10), (lw-10, 10), (10, lh-10), (lw-10, lh-10),
]
logo_transparent = flood_fill_alpha(logo_orig, seeds, tolerance=22)

# Slight blur on edges to soften any fringing
logo_transparent.save(LOGO_OUT)
print(f"  ✓ Saved transparent logo → {LOGO_OUT}")

# ── Helpers shared by all slides ──────────────────────────────────────────────

def new_slide():
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    _grid(draw)
    return img, draw

def _grid(draw):
    for x in range(0, W, 90):
        draw.line([(x,0),(x,H)], fill=(30,30,40), width=1)
    for y in range(0, H, 90):
        draw.line([(0,y),(W,y)], fill=(30,30,40), width=1)

def topbar(draw, slide_num=None):
    draw.text((60, 44), "— TITUS —", font=F_BRAND, fill=GOLD)
    if slide_num:
        label = f"0{slide_num} / 06"
        bbox  = draw.textbbox((0,0), label, font=F_LABEL)
        draw.text((W - 60 - (bbox[2]-bbox[0]), 48), label, font=F_LABEL, fill=GREY)
    draw.line([(60, 100), (W-60, 100)], fill=GOLD, width=2)

def handle(draw):
    draw.text((60, H-60), "@titustradingnetwork", font=F_BODY_SM, fill=GREY)

def corners(draw):
    s, t = 60, 3
    draw.line([(s, 120),(s, 180)],     fill=GOLD, width=t)
    draw.line([(s, 120),(s+60, 120)],  fill=GOLD, width=t)
    draw.line([(W-s, H-90),(W-s, H-150)],   fill=GOLD, width=t)
    draw.line([(W-s, H-90),(W-s-60, H-90)], fill=GOLD, width=t)

def glow(img, cx, cy, r, colour, alpha=40):
    layer = Image.new("RGB", (W, H), BG)
    ld    = ImageDraw.Draw(layer)
    for i in range(10, 0, -1):
        ri = int(r * i / 10)
        a  = int(alpha * (1 - i/10))
        c  = tuple(min(255, BG[ch] + int((colour[ch]-BG[ch]) * a/255)) for ch in range(3))
        ld.ellipse([cx-ri, cy-ri, cx+ri, cy+ri], fill=c)
    img.paste(layer, mask=layer.convert("L"))

def paste_logo(img, size=280, cx=None, top=None):
    """Paste transparent logo centred at cx, top edge at top."""
    cx  = cx  or W//2
    top = top or 160
    logo = logo_transparent.copy()
    logo.thumbnail((size, size), Image.LANCZOS)
    lw, lh = logo.size
    x = cx - lw//2
    img.paste(logo, (x, top), logo)

def wrap(draw, text, font, max_w, fill=WHITE, spacing=10):
    words, lines, line = text.split(), [], []
    for w in words:
        test = " ".join(line + [w])
        if draw.textbbox((0,0), test, font=font)[2] <= max_w:
            line.append(w)
        else:
            if line: lines.append(" ".join(line))
            line = [w]
    if line: lines.append(" ".join(line))
    return lines

def draw_text(draw, text, font, x, y, max_w, fill=WHITE, spacing=10):
    cy = y
    for ln in wrap(draw, text, font, max_w, fill, spacing):
        draw.text((x, cy), ln, font=font, fill=fill)
        cy += draw.textbbox((0,0), ln, font=font)[3] + spacing
    return cy

def callout(draw, rows, y, x=60, w=W-120):
    row_h, pad = 76, 24
    total = pad*2 + len(rows)*row_h
    draw.rounded_rectangle([x, y, x+w, y+total], radius=8, fill=BG2, outline=GOLD, width=1)
    cy = y + pad
    for icon, bold_word, rest, colour in rows:
        draw.text((x+16, cy+6),  icon,       font=F_BODY,  fill=WHITE)
        draw.text((x+64, cy+6),  bold_word,  font=F_LABEL, fill=colour)
        bw = draw.textbbox((0,0), bold_word+" ", font=F_LABEL)[2]
        draw.text((x+64+bw, cy+6), rest,     font=F_BODY,  fill=WHITE)
        cy += row_h
    return y + total + 20

# ── Slide builders ─────────────────────────────────────────────────────────────

def slide_1():
    img, draw = new_slide()
    glow(img, W//2, H//2, 600, GOLD, 50)
    corners(draw)
    topbar(draw)
    # Logo centred upper area
    paste_logo(img, size=320, cx=W//2, top=140)
    # Eyebrow
    draw.text((W//2, 510), "MARKET STRUCTURE", font=F_EYEBROW, fill=GOLD, anchor="mm")
    # Divider
    draw.line([(160, 545), (W-160, 545)], fill=GOLD, width=1)
    # Headline
    draw_text(draw, "Every trader needs to know this first.", F_HERO_MD, 60, 570, W-120, WHITE, 10)
    # Sub
    draw_text(draw, "Before you place another trade — understand the foundation every profitable setup is built on.",
              F_BODY, 60, 840, W-120, GREY, 8)
    # Swipe CTA
    bx1, by1, bx2, by2 = 60, 1040, 420, 1110
    draw.rounded_rectangle([bx1,by1,bx2,by2], radius=6, fill=BLUE)
    draw.text(((bx1+bx2)//2, (by1+by2)//2), "Swipe to learn  →", font=F_LABEL, fill=WHITE, anchor="mm")
    handle(draw)
    return img

def slide_2():
    img, draw = new_slide()
    glow(img, 0, 500, 400, GOLD, 40)
    topbar(draw, 2)
    y = 130
    y = draw_text(draw, "What is Market Structure?", F_HEAD, 60, y, W-120, WHITE, 6) + 16
    y = draw_text(draw, "Market structure tells you who's in control — buyers or sellers — before you enter any trade.",
                  F_BODY, 60, y, W-120, GREY, 8) + 28
    y = callout(draw, [
        ("📈", "Uptrend",   " — Higher Highs + Higher Lows. Buyers winning.", GOLD),
        ("📉", "Downtrend", " — Lower Highs + Lower Lows. Sellers winning.",  BLUE),
        ("⚠️",  "Ranging",   " — Price bouncing between the same levels.",     GREY),
    ], y)
    draw_text(draw, "Master this first. Everything else builds on it.", F_BODY_SM, 60, y+10, W-120, GREY)
    paste_logo(img, size=160, cx=W-130, top=H-230)
    handle(draw)
    return img

def slide_3():
    img, draw = new_slide()
    glow(img, W, 400, 400, BLUE, 40)
    topbar(draw, 3)
    y = 130
    y = draw_text(draw, "Break of Structure (BOS)", F_HEAD, 60, y, W-120, WHITE, 6) + 16
    y = draw_text(draw, "A BOS signals a potential shift in trend — it's your first confirmation to act.",
                  F_BODY, 60, y, W-120, GREY, 8) + 28
    y = callout(draw, [
        ("🔼", "Bullish BOS", " — Price breaks above swing high. Look for buys.", GOLD),
        ("🔽", "Bearish BOS", " — Price breaks below swing low. Look for sells.", BLUE),
        ("⚡", "CHoCH",       " — Change of Character. First sign of reversal.",   RED),
    ], y)
    draw_text(draw, "BOS = confirmation.  CHoCH = warning.  Know the difference.", F_BODY_SM, 60, y+10, W-120, GREY)
    paste_logo(img, size=160, cx=W-130, top=H-230)
    handle(draw)
    return img

def slide_4():
    img, draw = new_slide()
    glow(img, W, H, 400, GOLD, 40)
    topbar(draw, 4)
    y = 130
    y = draw_text(draw, "How to Trade It", F_HEAD, 60, y, W-120, WHITE, 6) + 16
    y = draw_text(draw, "Don't just spot structure — trade it with a clear, repeatable process.",
                  F_BODY, 60, y, W-120, GREY, 8) + 28
    y = callout(draw, [
        ("1️⃣", "Higher TF",  " — Identify trend on H4 or Daily timeframe.",       GOLD),
        ("2️⃣", "Signal",     " — Wait for BOS or CHoCH on 15m or 1H chart.",      BLUE),
        ("3️⃣", "Entry",      " — Enter on the retest of broken structure level.",  GOLD),
        ("4️⃣", "Risk Mgmt",  " — SL below swing low. Target the next key level.", BLUE),
    ], y)
    paste_logo(img, size=160, cx=W-130, top=H-230)
    handle(draw)
    return img

def slide_5():
    img, draw = new_slide()
    topbar(draw, 5)

    cx_chart, cy_chart, cw, ch = 60, 140, W-120, 860
    draw.rounded_rectangle([cx_chart, cy_chart, cx_chart+cw, cy_chart+ch], radius=8, fill=BG2, outline=(30,32,48), width=1)

    pts_norm = [
        (0.00,0.82),(0.08,0.72),(0.14,0.76),(0.22,0.58),(0.28,0.64),
        (0.36,0.42),(0.44,0.36),(0.50,0.50),(0.58,0.18),(0.66,0.12),
        (0.72,0.26),(0.80,0.32),(0.88,0.52),(0.94,0.38),(1.00,0.28),
    ]
    pad = 55
    def px(nx, ny):
        return (cx_chart+pad+int(nx*(cw-pad*2)), cy_chart+pad+int(ny*(ch-pad*2)))

    pts = [px(nx,ny) for nx,ny in pts_norm]

    for i in range(len(pts)-1):
        draw.line([pts[i],pts[i+1]], fill=(240,180,41,30), width=10)
    for i in range(len(pts)-1):
        draw.line([pts[i],pts[i+1]], fill=GOLD, width=3)
    for p in [pts[0],pts[3],pts[7],pts[8],pts[11]]:
        draw.ellipse([p[0]-6,p[1]-6,p[0]+6,p[1]+6], fill=GOLD)

    # BOS label
    bx, bt = pts[8][0], pts[8][1]-40
    draw.line([(bx,bt),(bx,pts[7][1]+10)], fill=BLUE, width=2)
    draw.rounded_rectangle([bx-2, bt-32, bx+72, bt], radius=4, fill=BLUE)
    draw.text((bx+4, bt-28), " BOS ", font=F_LABEL, fill=WHITE)

    # CHoCH label
    cx2, ct = pts[11][0], pts[11][1]-40
    draw.line([(cx2,ct),(cx2,pts[12][1])], fill=RED, width=2)
    draw.rounded_rectangle([cx2-2, ct-32, cx2+100, ct], radius=4, fill=RED)
    draw.text((cx2+4, ct-28), " CHoCH ", font=F_LABEL, fill=WHITE)

    # Structure level
    sl_y = pts[3][1]
    draw.line([(cx_chart+pad, sl_y),(pts[7][0], sl_y)], fill=GREY, width=1)
    draw.text((cx_chart+pad+4, sl_y-28), "Structure Level", font=F_BODY_SM, fill=GREY)

    draw_text(draw, "BOS confirmed on H1 → retest of structure → clean entry formed.",
              F_BODY_SM, 60, cy_chart+ch+20, W-120, GREY)

    paste_logo(img, size=160, cx=W-130, top=H-230)
    handle(draw)
    return img

def slide_6():
    img, draw = new_slide()
    glow(img, W//2, H//2, 700, GOLD, 65)
    corners(draw)
    topbar(draw)
    paste_logo(img, size=300, cx=W//2, top=150)
    y = 510
    for line, colour in [("FOLLOW FOR", WHITE), ("DAILY SETUPS", GOLD), ("& BREAKDOWNS.", WHITE)]:
        bbox = draw.textbbox((0,0), line, font=F_HERO_MD)
        lw2  = bbox[2]-bbox[0]
        draw.text(((W-lw2)//2, y), line, font=F_HERO_MD, fill=colour)
        y += bbox[3]-bbox[1]+10
    draw.text((W//2, y+20), "No gatekeeping. Just real trading education.", font=F_BODY, fill=GREY, anchor="mm")
    bx1, by1, bx2, by2 = 120, y+60, W-120, y+180
    draw.rounded_rectangle([bx1,by1,bx2,by2], radius=8, fill=BG2, outline=GOLD, width=2)
    draw.text((W//2, by1+30), "FREE COMMUNITY", font=F_LABEL, fill=GOLD, anchor="mm")
    draw.text((W//2, by1+78), "t.me/titus_net", font=F_HEAD, fill=WHITE, anchor="mm")
    draw.text((W//2, by2+40), "Drop a 📊 if this helped →", font=F_BODY_SM, fill=GREY, anchor="mm")
    handle(draw)
    return img

# ── Generate ───────────────────────────────────────────────────────────────────

slides = [
    ("titus_carousel_1_hook.png",      slide_1),
    ("titus_carousel_2_structure.png", slide_2),
    ("titus_carousel_3_bos.png",       slide_3),
    ("titus_carousel_4_entry.png",     slide_4),
    ("titus_carousel_5_chart.png",     slide_5),
    ("titus_carousel_6_cta.png",       slide_6),
]

print("\nGenerating slides...\n")
for fname, builder in slides:
    img  = builder()
    path = os.path.join(OUT_DIR, fname)
    img.save(path, "PNG")
    print(f"  ✓  {fname}")

print(f"\nAll done → {OUT_DIR}")
