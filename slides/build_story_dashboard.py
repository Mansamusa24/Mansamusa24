#!/usr/bin/env python3
"""
Build an Instagram Story from a desk photo of the Titus dashboard: blur out
the browser address bar (which reveals the dashboard's private server
address) and place the Titus Trading Network logo over it instead.
"""

from PIL import Image, ImageFilter
import os

BASE_DIR  = os.path.dirname(__file__)
SRC       = os.path.join(BASE_DIR, "stories", "source", "dashboard_screen.jpeg")
OUT_DIR   = os.path.join(BASE_DIR, "stories", "output")
LOGO_PATH = os.path.join(BASE_DIR, "titus_logo_transparent.png")
os.makedirs(OUT_DIR, exist_ok=True)

# Address-bar row only (tab row above and dashboard ticker below are left
# untouched), found by pixel-sampling the toolbar's grey band.
ADDR_BAR_BOX = (1800, 100, 2440, 205)
# Red "not secure" caution badge sitting in the tab row, left of the tabs.
CAUTION_BOX  = (1075, 65, 1200, 150)

def build():
    img = Image.open(SRC).convert("RGB")

    for box in (ADDR_BAR_BOX, CAUTION_BOX):
        band = img.crop(box).filter(ImageFilter.GaussianBlur(25))
        img.paste(band, box[:2])

    img = img.convert("RGBA")
    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo.thumbnail((95, 95), Image.LANCZOS)
    lw, lh = logo.size
    cx = (ADDR_BAR_BOX[0] + ADDR_BAR_BOX[2]) // 2
    cy = (ADDR_BAR_BOX[1] + ADDR_BAR_BOX[3]) // 2
    img.paste(logo, (cx - lw // 2, cy - lh // 2), logo)

    img = img.convert("RGB")
    out = os.path.join(OUT_DIR, "dashboard_story.jpg")
    img.save(out, "JPEG", quality=95)
    print(f"  ✓ {out}")

print("Building dashboard story (address bar hidden)...\n")
build()
