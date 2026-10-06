# Prism Console

A clean, colorful console-style **Playnite Fullscreen** theme. Big rounded covers on a single game rail, a neon focus ring, color-coded system tabs, and a bright logo badge for every platform.

Targets Playnite 10 (Fullscreen theme API 2.10.0, Playnite 10.62 and newer).

## Pick your rail

The rail position is chosen by picking one of three themes in Playnite. They share everything else.

| Theme in Playnite | Layout |
|---|---|
| Prism Console (Top Rail) | Game rail across the top, selected game details below over the artwork. |
| Prism Console (Bottom Rail) | Classic console layout: artwork and details up top, rail along the bottom. |
| Prism Console (Center Rail) | Big covers: one large rail through the middle, compact details underneath. |

Install all three and switch any time from Fullscreen **Settings > Visuals > Theme** (restart Fullscreen mode to apply).

## Install

1. Drag a `.pext` from `dist/` onto the Playnite window (or double-click it) and confirm. Or copy a `dist/PrismConsole_<Variant>` folder into `%AppData%\Playnite\Themes\Fullscreen\` (portable installs: `<Playnite folder>\Themes\Fullscreen\`).
2. In Fullscreen mode open **Settings > Visuals** and pick the theme.
3. **Required for the rail:** in **Settings > Layout** turn **Horizontal Scrolling** on and set **Columns** to about 6 to 8. With horizontal scrolling the tiles grow to fill the rail's height, so you get one clean row. More columns means smaller covers.
4. Recommended: in **Settings > Visuals** turn on **Show Background Image on Main Screen** so the selected game's artwork fills the screen behind the details.

## Organizing by system

The tabs in the top bar are your Fullscreen **filter presets**. Make one per system:

1. In Desktop mode, filter the library to a platform (e.g. Nintendo SNES).
2. Save it as a filter preset, name it something like `SNES`, and tick **Show as quick filter in Fullscreen mode**.
3. Order presets in the filter preset manager. Tabs cycle through seven accent colors.

If a preset's name matches a logo in `Images/Presets/`, the tab shows the logo instead of text. Short labels (`SNES`, `N64`, `PS2`, `GENESIS`), full Playnite platform names (`Nintendo SNES`, `Sony PlayStation 2`) and common nicknames (`Mega Drive`, `PC Engine`, `PSX`, `Switch`, `Steam`) all work.

## Platform logos

Every tile, the hero area and the details screen show the game's real console logo (SNES, PlayStation 2, Genesis, and so on), and system tabs show the logo instead of the preset name. 87 of Playnite's 96 built-in platforms have a real logo. The other 9 (PS5, Switch 2, Xbox One, Xbox Series, Arduboy, Atari Falcon, Commodore CBM-II and CBM-5x0, TI-83) get a generated gradient badge until you add your own.

Lookup order:

1. `Images/Platforms/<platform specification id>.png`
2. `Images/Platforms/<platform name>.png` (for custom platforms, add your own file)
3. A gradient chip with the platform name

To use your own art, drop a transparent PNG with the same file name into the installed theme folder (and into `Images/Presets/<preset name>.png` for a tab). Wide logos about 200 px tall look best.

To hide the small logo on each cover, set `PC_TilePlatformBadgeVisibility` to `Collapsed` in `Constants.xaml`.

### Logo credits

Console logos are from the Batocera [Carbon theme](https://github.com/fabricecaruso/es-theme-carbon) for EmulationStation (Carbon by Rookervik, based on "simple" by Nils Bonenberger), converted by `tools/import_logos.py`. They are trademarks of their respective owners and are included only to identify each system.

## Customizing

* Colors: everything is in `src/theme/Constants.xaml` (accent colors, tab colors, background, focus ring).
* Rail sizes and positions: `src/variants.json` (rail height, margins, hero placement per variant).

## Building

```
python3 tools/build.py              # regenerates logos and rebuilds dist/
python3 tools/build.py --no-logos   # reuse logos from build/logos
```

Needs Python 3 with Pillow and the Inter font (used only for the fallback badges). The real logos are already converted into `src/logos/`; to refresh them, clone the Carbon theme and run `python3 tools/import_logos.py <carbon folder>` (needs `pip install cairosvg`).

## Project layout

```
src/theme/            theme files (only files that differ from Playnite's default theme)
  Constants.xaml      palette + layout knobs (rail block rewritten per variant)
  Media.xaml          platform logo control, info chips
  Views/Main.xaml     main screen: top bar, hero, game rail, bottom bar
  Views/GameDetails.xaml
  DerivedStyles/      rail tile + focus ring, top/bottom bar buttons
  CustomControls/FilterPresetSelector.xaml   colorful system tabs
src/variants.json     top / bottom / center rail settings
src/logos/            real console logos, one PNG per platform specification id
tools/import_logos.py converts Carbon theme logos into src/logos/
tools/logo_map.py     Playnite platform id -> Carbon logo name
tools/make_logos.py   writes platform + tab logos (badges for missing ones)
tools/build.py        assembles dist/ folders and .pext packages
dist/                 ready-to-install themes
```

Playnite loads its default theme first and then each file from this theme on top, so files not listed here (menus, settings, filters) keep the default layout with this theme's colors.
