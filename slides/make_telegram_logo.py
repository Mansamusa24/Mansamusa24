#!/usr/bin/env python3
"""Draw a clean Telegram logo icon and save it."""
from PIL import Image, ImageDraw
import math, os

SIZE = 120
TG_BLUE = (42, 171, 238)   # Telegram brand blue

img  = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Circle background
draw.ellipse([0, 0, SIZE-1, SIZE-1], fill=TG_BLUE)

# Paper plane (simplified: send arrow pointing top-right)
# Points scaled to 120x120
s = SIZE
pts_plane = [
    (int(s*0.14), int(s*0.50)),   # left tail
    (int(s*0.86), int(s*0.22)),   # top right tip
    (int(s*0.54), int(s*0.78)),   # bottom point
    (int(s*0.54), int(s*0.56)),   # inner fold
    (int(s*0.34), int(s*0.50)),   # inner left
]
# Main arrow body
draw.polygon([
    (int(s*0.14), int(s*0.50)),
    (int(s*0.86), int(s*0.22)),
    (int(s*0.54), int(s*0.78)),
    (int(s*0.54), int(s*0.56)),
    (int(s*0.34), int(s*0.50)),
], fill=(255,255,255))

# Bottom tail flap
draw.polygon([
    (int(s*0.54), int(s*0.56)),
    (int(s*0.54), int(s*0.78)),
    (int(s*0.40), int(s*0.63)),
], fill=(210,210,210))

out = os.path.join(os.path.dirname(__file__), "telegram_logo.png")
img.save(out, "PNG")
print(f"Saved Telegram logo → {out}")
