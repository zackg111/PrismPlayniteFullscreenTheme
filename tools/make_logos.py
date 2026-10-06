#!/usr/bin/env python3
"""Write the platform logos for Prism Console.

Writes, under <out>/Images:
  Platforms/<specification id>.png   used by game tiles, hero and details
  Presets/<short label>.png          used by system tabs (filter preset named "SNES")
  Presets/<platform name>.png        same, for presets named "Nintendo SNES"
  Presets/<alias>.png                same, for common nicknames ("Mega Drive", "PSX")

Real console logos come from src/logos/<specification id>.png (imported from
the Batocera Carbon theme by tools/import_logos.py). Platforms with no logo
there get a generated gradient badge instead. Drop your own PNGs with the
same file names into the theme folder to replace any of them.

Usage: python3 make_logos.py <theme dir>
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 480, 200
SS = 2  # supersampling factor
FONT_BOLD = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FONT_SMALL = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"

# Palette shortcuts
RED, PINK, ORANGE, YELLOW = "#ff2d55", "#ff3d9a", "#ff8a3d", "#ffd23f"
GREEN, LIME, TEAL, CYAN = "#22c55e", "#a3e635", "#14b8a6", "#2ee6ff"
BLUE, INDIGO, PURPLE, VIOLET = "#3b82f6", "#4f46e5", "#8b5cff", "#c026d3"
NAVY, SLATE, SILVER, BLACK = "#1e3a8a", "#334155", "#94a3b8", "#111827"

# id: (wordmark, maker line, gradient stops)
PLATFORMS = {
    # Nintendo
    "nintendo_nes": ("NES", "NINTENDO", [RED, "#b91c1c", SLATE]),
    "nintendo_famicom_disk": ("FDS", "NINTENDO", ["#dc2626", YELLOW]),
    "nintendo_super_nes": ("SNES", "NINTENDO", [PURPLE, "#6d28d9", "#a78bfa"]),
    "nintendo_64": ("N64", "NINTENDO", [RED, BLUE, GREEN, YELLOW]),
    "nintendo_gamecube": ("GAMECUBE", "NINTENDO", [INDIGO, PURPLE, VIOLET]),
    "nintendo_wii": ("Wii", "NINTENDO", [CYAN, "#0ea5e9", "#e0f2fe"]),
    "nintendo_wiiu": ("Wii U", "NINTENDO", ["#0891b2", CYAN, BLUE]),
    "nintendo_switch": ("SWITCH", "NINTENDO", ["#ff3c28", PINK, "#0ab9e6"]),
    "nintendo_switch2": ("SWITCH 2", "NINTENDO", ["#0ab9e6", PURPLE, "#ff3c28"]),
    "nintendo_gameboy": ("GAME BOY", "NINTENDO", ["#4d7c0f", LIME, "#65a30d"]),
    "nintendo_gameboycolor": ("GB COLOR", "NINTENDO", [VIOLET, YELLOW, TEAL]),
    "nintendo_gameboyadvance": ("GBA", "NINTENDO", [INDIGO, PURPLE, PINK]),
    "nintendo_ds": ("DS", "NINTENDO", [SILVER, BLUE, NAVY]),
    "nintendo_dsi": ("DSi", "NINTENDO", [BLUE, CYAN, PINK]),
    "nintendo_3ds": ("3DS", "NINTENDO", [RED, PINK, "#7f1d1d"]),
    "nintendo_virtualboy": ("VIRTUAL BOY", "NINTENDO", ["#dc2626", "#450a0a"]),
    "nintendo_gameandwatch": ("GAME&WATCH", "NINTENDO", [YELLOW, ORANGE, RED]),
    "pokemon_mini": ("POKÉMON MINI", "NINTENDO", [YELLOW, RED]),
    # Sony
    "sony_playstation": ("PS1", "PLAYSTATION", [RED, YELLOW, GREEN, BLUE]),
    "sony_playstation2": ("PS2", "PLAYSTATION", [NAVY, BLUE, INDIGO]),
    "sony_playstation3": ("PS3", "PLAYSTATION", [BLACK, SLATE, SILVER]),
    "sony_playstation4": ("PS4", "PLAYSTATION", ["#0037a5", BLUE, CYAN]),
    "sony_playstation5": ("PS5", "PLAYSTATION", [BLUE, "#e2e8f0", PURPLE]),
    "sony_psp": ("PSP", "PLAYSTATION", [BLACK, INDIGO, VIOLET]),
    "sony_vita": ("PS VITA", "PLAYSTATION", [BLUE, TEAL, CYAN]),
    # Microsoft
    "xbox": ("XBOX", "MICROSOFT", ["#14532d", GREEN, LIME]),
    "xbox360": ("XBOX 360", "MICROSOFT", [GREEN, LIME, "#e2e8f0"]),
    "xbox_one": ("XBOX ONE", "MICROSOFT", ["#107c10", GREEN, BLACK]),
    "xbox_series": ("SERIES X|S", "MICROSOFT", [BLACK, "#107c10", LIME]),
    "microsoft_msx": ("MSX", "MICROSOFT", [ORANGE, RED]),
    "microsoft_msx2": ("MSX2", "MICROSOFT", [RED, PURPLE]),
    # Sega
    "sega_sg1000": ("SG-1000", "SEGA", [RED, SLATE]),
    "sega_mastersystem": ("MASTER SYSTEM", "SEGA", [RED, BLACK]),
    "sega_genesis": ("GENESIS", "SEGA", [BLACK, RED, ORANGE]),
    "sega_cd": ("SEGA CD", "SEGA", [BLUE, RED, BLACK]),
    "sega_32x": ("32X", "SEGA", [YELLOW, RED, BLACK]),
    "sega_saturn": ("SATURN", "SEGA", [NAVY, BLUE, SILVER]),
    "sega_dreamcast": ("DREAMCAST", "SEGA", [ORANGE, "#f97316", "#fde68a"]),
    "sega_gamegear": ("GAME GEAR", "SEGA", [BLACK, BLUE, CYAN]),
    # NEC / SNK / Bandai / others
    "nec_turbografx_16": ("TURBOGRAFX", "NEC", [ORANGE, RED, BLACK]),
    "nec_turbografx_cd": ("TG-CD", "NEC", [RED, ORANGE, YELLOW]),
    "nec_supergrafx": ("SUPERGRAFX", "NEC", [SLATE, ORANGE]),
    "nec_pcfx": ("PC-FX", "NEC", [PURPLE, PINK]),
    "nec_pc88": ("PC-88", "NEC", [TEAL, BLUE]),
    "nec_pc98": ("PC-98", "NEC", [BLUE, INDIGO]),
    "snk_neogeo_aes": ("NEO GEO", "SNK", [BLACK, YELLOW, RED]),
    "snk_neogeo_cd": ("NEO GEO CD", "SNK", [YELLOW, ORANGE, BLACK]),
    "snk_neogeopocket": ("NGP", "SNK", [SLATE, BLUE]),
    "snk_neogeopocket_color": ("NGP COLOR", "SNK", [BLUE, YELLOW, RED]),
    "bandai_wonderswan": ("WONDERSWAN", "BANDAI", [SLATE, CYAN]),
    "bandai_wonderswan_color": ("WS COLOR", "BANDAI", [CYAN, PURPLE, PINK]),
    "arcade": ("ARCADE", "COIN-OP", [PINK, PURPLE, CYAN]),
    "3do": ("3DO", "PANASONIC", [YELLOW, RED, BLUE]),
    "philips_cdi": ("CD-i", "PHILIPS", [BLUE, CYAN]),
    "vectrex": ("VECTREX", "GCE", [BLACK, CYAN, "#e0f2fe"]),
    "coleco_vision": ("COLECOVISION", "COLECO", [BLACK, SILVER, BLUE]),
    "mattel_intellivision": ("INTELLIVISION", "MATTEL", ["#78350f", YELLOW]),
    "magnavox_odyssey_2": ("ODYSSEY²", "MAGNAVOX", [BLACK, ORANGE]),
    "fairchild_channelf": ("CHANNEL F", "FAIRCHILD", ["#78350f", ORANGE]),
    "watara_supervision": ("SUPERVISION", "WATARA", [SLATE, TEAL]),
    "megaduck": ("MEGA DUCK", "WELBACK", [YELLOW, GREEN]),
    "arduboy": ("ARDUBOY", "OPEN HW", [TEAL, BLACK]),
    "uzebox": ("UZEBOX", "OPEN HW", [GREEN, BLACK]),
    "tic_80": ("TIC-80", "FANTASY", [PINK, YELLOW, CYAN]),
    "wasm4": ("WASM-4", "FANTASY", [PURPLE, CYAN]),
    # Atari
    "atari_2600": ("2600", "ATARI", ["#7c2d12", ORANGE, YELLOW]),
    "atari_5200": ("5200", "ATARI", [BLACK, SILVER]),
    "atari_7800": ("7800", "ATARI", [BLACK, RED, ORANGE]),
    "atari_8bit": ("ATARI 8-BIT", "ATARI", [SLATE, ORANGE]),
    "atari_jaguar": ("JAGUAR", "ATARI", [BLACK, RED]),
    "atari_lynx": ("LYNX", "ATARI", [ORANGE, BLACK]),
    "atari_st": ("ATARI ST", "ATARI", [SILVER, SLATE]),
    "atari_falcon030": ("FALCON", "ATARI", [SLATE, BLUE]),
    # Computers
    "pc_windows": ("PC", "WINDOWS", ["#0078d4", CYAN, PURPLE]),
    "pc_dos": ("DOS", "MS-DOS", [BLACK, SLATE, GREEN]),
    "pc_linux": ("LINUX", "PC", [YELLOW, BLACK]),
    "macintosh": ("MAC", "APPLE", [SILVER, SLATE]),
    "apple_2": ("APPLE II", "APPLE", [GREEN, YELLOW, ORANGE, RED, PURPLE, BLUE]),
    "commodore_64": ("C64", "COMMODORE", ["#3730a3", "#818cf8"]),
    "commodore_amiga": ("AMIGA", "COMMODORE", [BLUE, ORANGE, "#e2e8f0"]),
    "commodore_amiga_cd32": ("CD32", "COMMODORE", [BLACK, BLUE, ORANGE]),
    "commodore_vci20": ("VIC-20", "COMMODORE", [RED, BLUE]),
    "commodore_plus4": ("PLUS/4", "COMMODORE", [SLATE, RED]),
    "commodore_pet": ("PET", "COMMODORE", [BLACK, GREEN]),
    "commodore_cbm2": ("CBM-II", "COMMODORE", [SLATE, BLUE]),
    "commodore_cbm5x0": ("CBM-5x0", "COMMODORE", [SLATE, TEAL]),
    "amstrad_cpc": ("CPC", "AMSTRAD", [RED, GREEN, BLUE]),
    "sinclair_zxspectrum": ("ZX SPECTRUM", "SINCLAIR", [RED, YELLOW, GREEN, CYAN]),
    "sinclair_zxspectrum3": ("SPECTRUM +3", "SINCLAIR", [BLACK, RED, YELLOW, GREEN, CYAN]),
    "sinclair_zx81": ("ZX81", "SINCLAIR", [BLACK, RED]),
    "sharp_x1": ("X1", "SHARP", [RED, SLATE]),
    "sharp_x68000": ("X68000", "SHARP", [SLATE, BLUE]),
    "thomson_mo5": ("MO5", "THOMSON", [ORANGE, SLATE]),
    "thomson_to7": ("TO7", "THOMSON", [BLUE, SLATE]),
    "ti_83": ("TI-83", "TEXAS INSTR.", [BLUE, SLATE]),
    "adobe_flash": ("FLASH", "ADOBE", [RED, BLACK]),
}

# Official Playnite platform names, for the name-keyed preset images
NAMES = {
    "3do": "3DO Interactive Multiplayer", "adobe_flash": "Adobe Flash", "amstrad_cpc": "Amstrad CPC",
    "apple_2": "Apple II", "arcade": "Arcade", "arduboy": "Arduboy", "atari_2600": "Atari 2600",
    "atari_5200": "Atari 5200", "atari_7800": "Atari 7800", "atari_8bit": "Atari 8-bit",
    "atari_falcon030": "Atari Falcon030", "atari_jaguar": "Atari Jaguar", "atari_lynx": "Atari Lynx",
    "bandai_wonderswan_color": "Bandai WonderSwan Color", "bandai_wonderswan": "Bandai WonderSwan",
    "coleco_vision": "Coleco ColecoVision", "commodore_64": "Commodore 64",
    "commodore_amiga_cd32": "Commodore Amiga CD32", "commodore_amiga": "Commodore Amiga",
    "commodore_cbm5x0": "Commodore CBM-5x0", "commodore_cbm2": "Commodore CBM-II",
    "commodore_pet": "Commodore PET", "commodore_vci20": "Commodore VIC20",
    "fairchild_channelf": "Fairchild Channel F", "vectrex": "GCE Vectrex", "macintosh": "Macintosh",
    "magnavox_odyssey_2": "Magnavox Odyssey 2", "mattel_intellivision": "Mattel Intellivision",
    "megaduck": "Mega Duck", "microsoft_msx": "Microsoft MSX", "microsoft_msx2": "Microsoft MSX2",
    "xbox360": "Microsoft Xbox 360", "xbox_one": "Microsoft Xbox One", "xbox_series": "Microsoft Xbox Series",
    "xbox": "Microsoft Xbox", "nec_pc88": "NEC PC-88", "nec_pc98": "NEC PC-98", "nec_pcfx": "NEC PC-FX",
    "nec_supergrafx": "NEC SuperGrafx", "nec_turbografx_16": "NEC TurboGrafx 16",
    "nec_turbografx_cd": "NEC TurboGrafx-CD", "nintendo_3ds": "Nintendo 3DS", "nintendo_64": "Nintendo 64",
    "nintendo_ds": "Nintendo DS", "nintendo_dsi": "Nintendo DSi", "nintendo_nes": "Nintendo Entertainment System",
    "nintendo_famicom_disk": "Nintendo Family Computer Disk System",
    "nintendo_gameandwatch": "Nintendo Game & Watch", "nintendo_gameboyadvance": "Nintendo Game Boy Advance",
    "nintendo_gameboycolor": "Nintendo Game Boy Color", "nintendo_gameboy": "Nintendo Game Boy",
    "nintendo_gamecube": "Nintendo GameCube", "nintendo_super_nes": "Nintendo SNES",
    "nintendo_switch": "Nintendo Switch", "nintendo_switch2": "Nintendo Switch 2",
    "nintendo_virtualboy": "Nintendo Virtual Boy", "nintendo_wiiu": "Nintendo Wii U", "nintendo_wii": "Nintendo Wii",
    "pc_dos": "PC (DOS)", "pc_linux": "PC (Linux)", "pc_windows": "PC (Windows)", "sega_32x": "Sega 32X",
    "sega_cd": "Sega CD", "sega_dreamcast": "Sega Dreamcast", "sega_gamegear": "Sega Game Gear",
    "sega_genesis": "Sega Genesis", "sega_mastersystem": "Sega Master System", "sega_saturn": "Sega Saturn",
    "sega_sg1000": "Sega SG-1000", "sharp_x1": "Sharp X1", "sharp_x68000": "Sharp X68000",
    "sinclair_zxspectrum3": "Sinclair ZX Spectrum +3", "sinclair_zxspectrum": "Sinclair ZX Spectrum",
    "sinclair_zx81": "Sinclair ZX81", "snk_neogeo_aes": "SNK Neo Geo AES", "snk_neogeo_cd": "SNK Neo Geo CD",
    "snk_neogeopocket_color": "SNK Neo Geo Pocket Color", "snk_neogeopocket": "SNK Neo Geo Pocket",
    "sony_playstation2": "Sony PlayStation 2", "sony_playstation3": "Sony PlayStation 3",
    "sony_playstation4": "Sony PlayStation 4", "sony_playstation5": "Sony PlayStation 5",
    "sony_psp": "Sony PlayStation Portable", "sony_vita": "Sony PlayStation Vita",
    "sony_playstation": "Sony PlayStation", "ti_83": "Texas Instruments TI-83", "thomson_mo5": "Thomson MO5",
    "thomson_to7": "Thomson TO7", "tic_80": "TIC-80", "uzebox": "Uzebox", "wasm4": "WASM-4",
    "watara_supervision": "Watara Supervision", "philips_cdi": "Philips CD-i", "pokemon_mini": "Pokémon mini",
}

# Extra friendly preset names people commonly use
ALIASES = {
    "nintendo_super_nes": ["Super Nintendo", "Super NES", "SFC", "Super Famicom"],
    "nintendo_nes": ["Famicom"], "nintendo_64": ["Nintendo 64"], "nintendo_gamecube": ["GameCube", "GC"],
    "nintendo_switch": ["Switch"], "nintendo_gameboy": ["Game Boy", "GB"], "nintendo_gameboycolor": ["GBC", "Game Boy Color"],
    "nintendo_gameboyadvance": ["Game Boy Advance"], "nintendo_wiiu": ["WiiU"],
    "sony_playstation": ["PlayStation", "PSX", "PS One"], "sony_playstation2": ["PlayStation 2"],
    "sony_playstation3": ["PlayStation 3"], "sony_playstation4": ["PlayStation 4"], "sony_playstation5": ["PlayStation 5"],
    "sony_vita": ["Vita", "PSVita"], "sega_genesis": ["Mega Drive", "Megadrive", "Genesis"],
    "sega_mastersystem": ["Master System", "SMS"], "sega_dreamcast": ["Dreamcast"], "sega_saturn": ["Saturn"],
    "sega_gamegear": ["Game Gear"], "nec_turbografx_16": ["PC Engine", "TurboGrafx-16", "TG16"],
    "pc_windows": ["Windows", "PC Games", "Steam"], "pc_dos": ["MS-DOS"], "snk_neogeo_aes": ["Neo Geo", "NeoGeo"],
    "arcade": ["MAME"], "xbox_series": ["Xbox Series X", "Xbox Series"], "commodore_amiga": ["Amiga"],
}


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def gradient(w, h, stops):
    """Diagonal multi-stop gradient."""
    cols = [hex_rgb(c) for c in stops]
    if len(cols) == 1:
        cols = cols * 2
    grad = Image.new("RGB", (w, h))
    px = grad.load()
    n = len(cols) - 1
    for y in range(h):
        for x in range(w):
            t = (x / w) * 0.75 + (y / h) * 0.25
            seg = min(int(t * n), n - 1)
            lt = t * n - seg
            a, b = cols[seg], cols[seg + 1]
            px[x, y] = tuple(int(a[i] + (b[i] - a[i]) * lt) for i in range(3))
    return grad


def fit_font(draw, text, path, max_w, max_h):
    size = max_h
    while size > 10:
        f = ImageFont.truetype(path, size)
        l, t, r, b = draw.textbbox((0, 0), text, font=f)
        if r - l <= max_w and b - t <= max_h:
            return f
        size -= 2
    return ImageFont.truetype(path, size)


def badge(label, maker, stops):
    w, h, r = W * SS, H * SS, 44 * SS
    base = gradient(w // 4, h // 4, stops).resize((w, h), Image.BICUBIC)

    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), radius=r, fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.paste(base, (0, 0), mask)

    # glossy top sheen + subtle diagonal stripes
    over = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    d.ellipse((-w * 0.2, -h * 1.1, w * 1.2, h * 0.55), fill=(255, 255, 255, 46))
    for i in range(-h, w, 46 * SS):
        d.polygon([(i, h), (i + 14 * SS, h), (i + 14 * SS + h, 0), (i + h, 0)], fill=(255, 255, 255, 10))
    over.putalpha(Image.composite(over.getchannel("A"), Image.new("L", (w, h), 0), mask))
    img = Image.alpha_composite(img, over)

    d = ImageDraw.Draw(img)
    d.rounded_rectangle((3 * SS, 3 * SS, w - 3 * SS, h - 3 * SS), radius=r - 3 * SS,
                        outline=(255, 255, 255, 120), width=3 * SS)

    pad = 30 * SS
    small = ImageFont.truetype(FONT_SMALL, 22 * SS)
    mk = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(mk).text((pad, 22 * SS), " ".join(maker), font=small, fill=(0, 0, 0, 170))
    img = Image.alpha_composite(img, mk.filter(ImageFilter.GaussianBlur(3 * SS)))
    ImageDraw.Draw(img).text((pad, 20 * SS), " ".join(maker), font=small, fill=(255, 255, 255, 225))

    big = fit_font(d, label, FONT_BOLD, w - pad * 2, int(h * 0.48))
    l, t, rr, b = d.textbbox((0, 0), label, font=big)
    tx = (w - (rr - l)) / 2 - l
    ty = h * 0.60 - (b - t) / 2 - t
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).text((tx, ty + 4 * SS), label, font=big, fill=(0, 0, 0, 150), features=["-calt"])
    shadow = shadow.filter(ImageFilter.GaussianBlur(6 * SS))
    img = Image.alpha_composite(img, shadow)
    ImageDraw.Draw(img).text((tx, ty), label, font=big, fill=(255, 255, 255, 255), features=["-calt"])

    return img.resize((W, H), Image.LANCZOS)


def safe(name):
    return "".join(c for c in name if c not in '<>:"/\\|?*').strip()


def main(theme_dir):
    pdir = os.path.join(theme_dir, "Images", "Platforms")
    sdir = os.path.join(theme_dir, "Images", "Presets")
    logo_src = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "logos")
    os.makedirs(pdir, exist_ok=True)
    os.makedirs(sdir, exist_ok=True)
    real, badges = 0, []
    for pid, (label, maker, stops) in PLATFORMS.items():
        src = os.path.join(logo_src, pid + ".png")
        if os.path.exists(src):
            img = Image.open(src).convert("RGBA")
            real += 1
        else:
            img = badge(label, maker, stops)
            badges.append(pid)
        img.save(os.path.join(pdir, pid + ".png"), optimize=True)
        small = img.resize((max(1, img.width * 100 // img.height), 100), Image.LANCZOS)
        names = {label, NAMES.get(pid, "")} | set(ALIASES.get(pid, []))
        for n in names:
            n = safe(n)
            if n:
                small.save(os.path.join(sdir, n + ".png"), optimize=True)
    print(f"wrote {real} console logos and {len(badges)} generated badges to {pdir}")
    if badges:
        print("  badges:", ", ".join(badges))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
