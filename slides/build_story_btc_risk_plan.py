#!/usr/bin/env python3
"""
Build a Telegram post from a closed-trade TradingView screenshot: crop out
the mobile app's drawing toolbar/nav chrome and leave the chart + trade
markup (target, stop, R:R) untouched, with a small logo watermark.
"""

from PIL import Image
import os

BASE_DIR  = os.path.dirname(__file__)
SRC       = os.path.join(BASE_DIR, "stories", "source", "btc_risk_plan.jpeg")
OUT_DIR   = os.path.join(BASE_DIR, "stories", "output")
LOGO_PATH = os.path.join(BASE_DIR, "titus_logo_transparent.png")
os.makedirs(OUT_DIR, exist_ok=True)

def build():
    img = Image.open(SRC).convert("RGB")
    w, h = img.size
    img = img.crop((0, 0, w, 1800))  # drop the toolbar/nav bar below the RSI panel

    img = img.convert("RGBA")
    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo.thumbnail((220, 220), Image.LANCZOS)
    lw, lh_ = logo.size
    logo.putalpha(logo.getchannel("A").point(lambda a: int(a * 0.85)))
    img.paste(logo, (30, img.height - lh_ - 30), logo)

    img = img.convert("RGB")
    out = os.path.join(OUT_DIR, "btc_risk_plan.jpg")
    img.save(out, "JPEG", quality=95)
    print(f"  ✓ {out}")

print("Building BTC risk-plan Telegram post...\n")
build()
