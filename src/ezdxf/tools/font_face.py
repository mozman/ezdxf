#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import NamedTuple


class FontFace(NamedTuple):
    ttf: str = ""
    family: str = "sans-serif"
    style: str = "normal"
    stretch: str = "normal"
    weight: str = "normal"

    @property
    def is_italic(self) -> bool:
        return self.style.find("italic") > -1

    @property
    def is_oblique(self) -> bool:
        return self.style.find("oblique") > -1

    @property
    def is_bold(self) -> bool:
        weight = self.weight
        if isinstance(weight, int):
            return weight > 400
        else:
            return weight_name_to_value(weight) > 400


def weight_name_to_value(name: str) -> int:
    """Map weight names to values. e.g. 'normal' -> 400"""
    return WEIGHT_TO_VALUE.get(name.lower(), 400)


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
