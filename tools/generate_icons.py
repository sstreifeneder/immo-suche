#!/usr/bin/env python3
"""Erzeugt die PWA-Icons (Berg + Sonne) nach ./icons/. Nutzt Pillow."""
import os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "icons")
os.makedirs(OUT, exist_ok=True)

BG = (15, 20, 23)
SUN = (224, 179, 65)
M1 = (76, 194, 164)   # accent
M2 = (106, 169, 255)  # accent2


def draw_icon(size, pad_ratio=0.0):
    img = Image.new("RGB", (size, size), BG)
    d = ImageDraw.Draw(img)
    pad = int(size * pad_ratio)
    inner = size - 2 * pad

    def x(fx): return pad + int(fx * inner)
    def y(fy): return pad + int(fy * inner)

    # Sonne
    r = int(inner * 0.12)
    cx, cy = x(0.70), y(0.30)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SUN)

    # hinterer Berg
    d.polygon([(x(0.05), y(0.82)), (x(0.45), y(0.34)), (x(0.85), y(0.82))], fill=M2)
    # vorderer Berg
    d.polygon([(x(0.30), y(0.86)), (x(0.62), y(0.46)), (x(0.95), y(0.86))], fill=M1)
    # Schneekappe vorderer Berg
    d.polygon([(x(0.62), y(0.46)), (x(0.555), y(0.55)), (x(0.60), y(0.555)),
               (x(0.635), y(0.52)), (x(0.665), y(0.555)), (x(0.69), y(0.535))], fill=(232, 238, 241))
    # Boden
    d.rectangle([x(0.0), y(0.82), x(1.0), y(1.0)], fill=(24, 32, 37))
    return img


for sz in (192, 512):
    draw_icon(sz, 0.0).save(os.path.join(OUT, f"icon-{sz}.png"))
# maskable: Inhalt im sicheren Zentrum (Rand ~16%)
draw_icon(512, 0.16).save(os.path.join(OUT, "icon-maskable-512.png"))
print("Icons geschrieben nach", OUT, ":", sorted(os.listdir(OUT)))
