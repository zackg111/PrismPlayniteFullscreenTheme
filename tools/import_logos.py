#!/usr/bin/env python3
"""Import real console logos from the Batocera Carbon EmulationStation theme.

  git clone --depth 1 https://github.com/fabricecaruso/es-theme-carbon /tmp/carbon
  python3 tools/import_logos.py /tmp/carbon

Writes src/logos/<platform specification id>.png (trimmed, 200 px tall).
Logos that are mostly black would vanish on the dark theme, so the importer
uses Carbon's white "-w" variant when one exists, otherwise it lightens the
near-black parts. Needs: pip install cairosvg
"""
import io
import os
import re
import sys

import cairosvg
from PIL import Image

from logo_map import CARBON

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "src", "logos")
HEIGHT, MAX_W = 200, 720

# Logos that sit on their own plate or box and read fine on dark as they are
KEEP_AS_IS = {"3do", "atari_lynx", "coleco_vision", "pokemon_mini", "sega_cd", "sega_genesis"}


def load(logos_dir, name):
    for ext in ("svg", "png"):
        p = os.path.join(logos_dir, f"{name}.{ext}")
        if not os.path.exists(p):
            continue
        if ext == "png":
            return Image.open(p).convert("RGBA")
        s = open(p, encoding="utf-8", errors="ignore").read()
        # Illustrator files declare XML entities; inline them so no DTD processing is needed
        ents = dict(re.findall(r'<!ENTITY\s+(\S+)\s+"([^"]*)"', s))
        s = re.sub(r"<!DOCTYPE[^\[>]*(\[.*?\])?\s*>", "", s, flags=re.S)
        for k, v in ents.items():
            s = s.replace(f"&{k};", v)
        png = cairosvg.svg2png(bytestring=s.encode("utf-8"), output_height=HEIGHT * 2)
        return Image.open(io.BytesIO(png)).convert("RGBA")
    return None


def darkness(img):
    """Share of visible pixels that are near-black and colorless."""
    px = [p for p in img.get_flattened_data() if p[3] > 64]
    if not px:
        return 0
    dark = sum(1 for r, g, b, a in px if max(r, g, b) < 80 and max(r, g, b) - min(r, g, b) < 40)
    return dark / len(px)


def lighten(img):
    """Turn near-black, colorless pixels light gray; leave colored parts alone."""
    out = []
    for r, g, b, a in img.get_flattened_data():
        if max(r, g, b) < 110 and max(r, g, b) - min(r, g, b) < 40:
            v = 235 - (r + g + b) // 3 // 3
            out.append((v, v, v, a))
        else:
            out.append((r, g, b, a))
    img = img.copy()
    img.putdata(out)
    return img


def fit(img):
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    scale = min(HEIGHT / img.height, MAX_W / img.width)
    return img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))), Image.LANCZOS)


def main(carbon_dir):
    logos_dir = os.path.join(carbon_dir, "art", "logos")
    os.makedirs(OUT, exist_ok=True)
    done, missing = 0, []
    for pid, name in sorted(CARBON.items()):
        img = load(logos_dir, name) if name else None
        if img is None:
            missing.append(pid)
            continue
        how = "color"
        if pid not in KEEP_AS_IS and darkness(img) > 0.2:
            white = load(logos_dir, name + "-w")
            if white is not None:
                img, how = white, "white variant"
            else:
                img, how = lighten(img), "lightened"
        fit(img).save(os.path.join(OUT, pid + ".png"), optimize=True)
        done += 1
        if how != "color":
            print(f"  {pid}: {how}")
    print(f"imported {done} logos into {OUT}")
    print("no logo (badge fallback):", ", ".join(missing))


if __name__ == "__main__":
    main(sys.argv[1])
