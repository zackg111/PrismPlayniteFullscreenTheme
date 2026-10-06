#!/usr/bin/env python3
"""Build the Prism Console fullscreen theme variants.

  python3 tools/build.py            build all variants into dist/
  python3 tools/build.py --no-logos reuse previously generated logos

Output per variant:
  dist/PrismConsole_<Variant>/              unpacked theme folder
  dist/PrismConsole_<Variant>_<ver>.pext    installable package (drag onto Playnite)
"""
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src", "theme")
DIST = os.path.join(ROOT, "dist")
LOGO_CACHE = os.path.join(ROOT, "build", "logos")

INT_KEYS = {"PC_RailRow": "sys:Int32", "PC_HeroRow": "sys:Int32"}
DOUBLE_KEYS = {"PC_RailHeight", "PC_HeroTitleSize"}
THICKNESS_KEYS = {"PC_RailMargin", "PC_HeroMargin"}
VALIGN_KEYS = {"PC_RailVerticalAlignment", "PC_HeroVerticalAlignment"}
VIS_KEYS = {"PC_HeroDetailsVisibility"}


def layout_block(name, v):
    lines = [
        "    <!-- ===== RAIL LAYOUT (generated per variant) ===== -->",
        "    <!-- Content grid has three rows: 0 = top slot, 1 = middle (fills), 2 = bottom slot -->",
        f'    <sys:String x:Key="PC_RailPosition">{name}</sys:String>',
    ]
    for key, val in v.items():
        if key in INT_KEYS:
            lines.append(f'    <sys:Int32 x:Key="{key}">{int(val)}</sys:Int32>')
        elif key in DOUBLE_KEYS:
            lines.append(f'    <sys:Double x:Key="{key}">{val}</sys:Double>')
        elif key in THICKNESS_KEYS:
            lines.append(f'    <Thickness x:Key="{key}">{val}</Thickness>')
        elif key in VALIGN_KEYS:
            lines.append(f'    <VerticalAlignment x:Key="{key}">{val}</VerticalAlignment>')
        elif key in VIS_KEYS:
            lines.append(f'    <Visibility x:Key="{key}">{val}</Visibility>')
    lines.append("    <!-- ===== END RAIL LAYOUT ===== -->")
    return "\n".join(lines)


def main():
    cfg = json.load(open(os.path.join(ROOT, "src", "variants.json"), encoding="utf-8"))
    ver = cfg["version"]

    if "--no-logos" not in sys.argv or not os.path.isdir(LOGO_CACHE):
        shutil.rmtree(LOGO_CACHE, ignore_errors=True)
        subprocess.check_call([sys.executable, os.path.join(ROOT, "tools", "make_logos.py"), LOGO_CACHE])

    os.makedirs(DIST, exist_ok=True)
    constants = open(os.path.join(SRC, "Constants.xaml"), encoding="utf-8").read()
    pattern = re.compile(r"    <!-- ===== RAIL LAYOUT.*?END RAIL LAYOUT ===== -->", re.S)
    assert pattern.search(constants), "layout markers missing in Constants.xaml"

    for name, v in cfg["variants"].items():
        v = dict(v)
        desc = v.pop("description")
        folder = f"PrismConsole_{name}"
        out = os.path.join(DIST, folder)
        shutil.rmtree(out, ignore_errors=True)
        shutil.copytree(SRC, out)
        shutil.copytree(os.path.join(LOGO_CACHE, "Images"), os.path.join(out, "Images"), dirs_exist_ok=True)

        with open(os.path.join(out, "Constants.xaml"), "w", encoding="utf-8") as f:
            f.write(pattern.sub(lambda _: layout_block(name, v), constants))

        manifest = (
            f"Id: PrismConsole_{name}_Rail\n"
            f"Name: Prism Console ({name} Rail)\n"
            f"Author: {cfg['author']}\n"
            f"Version: {ver}\n"
            f"Mode: Fullscreen\n"
            f"ThemeApiVersion: {cfg['themeApiVersion']}\n"
        )
        with open(os.path.join(out, "theme.yaml"), "w", encoding="utf-8") as f:
            f.write(manifest)

        pext = os.path.join(DIST, f"{folder}_{ver.replace('.', '_')}.pext")
        with zipfile.ZipFile(pext, "w", zipfile.ZIP_DEFLATED) as z:
            z.write(os.path.join(out, "theme.yaml"), "theme.yaml")
            for dirpath, _, files in os.walk(out):
                for fn in sorted(files):
                    full = os.path.join(dirpath, fn)
                    rel = os.path.relpath(full, out).replace(os.sep, "/")
                    if rel != "theme.yaml":
                        z.write(full, rel)
        print(f"{name:7} {desc}\n        -> {os.path.relpath(pext, ROOT)} ({os.path.getsize(pext) // 1024} KB)")


if __name__ == "__main__":
    main()
