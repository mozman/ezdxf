#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
""" Manage font data

The default DXF way to store fonts in the STYLE entity by using the ttf file
name is not a good choice, most render backends select fonts by their
properties, this list shows the matplotlib properties:

- family: List of font names in decreasing order of priority.
    The items may include a generic font family name, either
    'serif', 'sans-serif', 'cursive', 'fantasy', or 'monospace'.
- style: 'normal' ('regular'), 'italic' or 'oblique'
- stretch: A numeric value in the range 0-1000 or one of
    'ultra-condensed', 'extra-condensed', 'condensed',
    'semi-condensed', 'normal', 'semi-expanded', 'expanded',
    'extra-expanded' or 'ultra-expanded'
- weight: A numeric value in the range 0-1000 or one of
    'ultralight', 'light', 'normal', 'regular', 'book', 'medium',
    'roman', 'semibold', 'demibold', 'demi', 'bold', 'heavy',
    'extra bold', 'black'.

This way the backand can choose a similar font if the original font is not
available.

Select fonts in different backends:

- matplotlib: FontProperties(family, style, stretch, weight)
- pyqt: QFont(family: str, pointSize: int (ignore), weight: int, italic: bool)
- SVG: font-family; font-style; font-stretch; font-weight;

Weight Values: https://developer.mozilla.org/de/docs/Web/CSS/font-weight

Supported by matplotlib, pyqt, SVG

=========== =====
Thin        100
Hairline    100
ExtraLight  200
UltraLight  200
Light       300
Normal      400
Medium      500
DemiBold    600
SemiBold    600
Bold        700
ExtraBold   800
UltraBold   800
Black       900
Heavy       900
ExtraBlack  950
UltraBlack  950
=========== =====

Stretch Values: https://developer.mozilla.org/en-US/docs/Web/CSS/font-stretch

Supported by matplotlib, SVG

=============== ======
ultra-condensed 50%
extra-condensed 62.5%
condensed       75%
semi-condensed  87.5%
normal          100%
semi-expanded   112.5%
expanded        125%
extra-expanded  150%
ultra-expanded  200%
=============== ======


This module manages as backend agnostic font database.
The properties of many common fonts are stored in a data file "fonts.json",
therefore for basic usage no additional dependency is required.
Advanced features uses the optional matplotlib font manager tools.

The :func:`add_system_fonts` function adds all available fonts for the current
system to the font database.

"""
from typing import Dict, Optional
from collections import namedtuple
import logging
from pathlib import Path
import json

FONT_DATA_FILE = 'fonts.json'
logger = logging.getLogger('ezdxf')

Font = namedtuple('Font', "ttf family style stretch weight")

# Key is TTF font file name without path in lowercase like "arial.ttf":
fonts: Dict[str, Font] = dict()

WEIGHT_TO_VALUE = {
    "thin": 100,
    "hairline": 100,
    "extralight": 200,
    "UltraLight": 200,
    "light": 300,
    "normal": 400,
    "medium": 500,
    "demibold": 600,
    "semibold": 600,
    "bold": 700,
    "extrabold": 800,
    "ultrabold": 800,
    "black": 900,
    "heavy": 900,
    "extrablack": 950,
    "ultrablack": 950,
}


def weight_name_to_value(name: str) -> int:
    return WEIGHT_TO_VALUE.get(name.lower(), 400)


def db_key(name: str) -> str:
    return Path(name).name.lower()


def add_system_fonts() -> None:
    try:
        from matplotlib.font_manager import FontManager
    except ImportError:
        logger.debug('This function requires the optional matplotlib package.')
        return
    for entry in FontManager().ttflist:
        ttf = db_key(entry.fname)
        fonts[ttf] = Font(
            ttf,
            entry.name,
            entry.style,
            entry.stretch,
            entry.weight,
        )


def find(ttf_path: Optional[str]) -> Optional[Font]:
    if ttf_path:
        return fonts.get(db_key(ttf_path))
    else:
        return None


def get(ttf_path: str) -> Font:
    font = find(ttf_path)
    if font is None:
        # Create a pseudo entry:
        name = db_key(ttf_path)
        return Font(
            name,
            Path(ttf_path).stem,
            "normal", "normal", "normal",
        )
    else:
        return font


def load(path=None):
    path = Path(path) if path else Path(__file__).parent / FONT_DATA_FILE

    if not path.exists():
        return
    with open(path, 'rt') as fp:
        data = json.load(fp)
    if data:
        for font in data:
            key = font[0]
            fonts[key] = Font(*font)


def save(path=None):
    path = Path(path) if path else Path(__file__).parent / FONT_DATA_FILE
    with open(path, 'wt') as fp:
        json.dump(list(fonts.values()), fp, indent=2)
