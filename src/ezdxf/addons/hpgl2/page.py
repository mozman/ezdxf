#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
# 1 plot unit (plu) = 0.025mm
# 40 plu = 1mm
# 1016 plu = 1 inch
# 3.39 plu = 1 dot @300 dpi

from __future__ import annotations
from typing import Sequence
import math
import enum
from .deps import Vec2, PAGE_SIZES, NULLVEC2

INCH_TO_PLU = 1016
MM_TO_PLU = 40


class PageRotation(enum.IntEnum):
    RO_0 = 0
    RO_90 = 90
    RO_180 = 180
    RO_270 = 270


class Page:
    def __init__(self, size_x: int, size_y: int):
        self.size_x = int(size_x)  # in plotter units (plu)
        self.size_y = int(size_y)  # plu

        self.p1 = NULLVEC2  # plu
        self.p2 = Vec2(size_x, size_y)
        self.user_scaling = False
        self.user_scale_x: float = 1.0
        self.user_scale_y: float = 1.0
        self.user_origin = NULLVEC2  # plu
        self.page_rotation = PageRotation.RO_0

    def set_scaling_points(self, p1: Vec2, p2: Vec2) -> None:
        self.p1 = p1
        self.p2 = p2

    def set_scale(
        self, x1: float, x2: float, y1: float, y2: float, isotropic=True
    ) -> None:
        pass

    def set_ucs(self, origin: Vec2, sx: float = 1.0, sy: float = 1.0):
        self.user_origin = Vec2(origin)
        self.user_scale_x = float(sx)
        self.user_scale_y = float(sy)
        if math.isclose(self.user_scale_x, 1.0) and math.isclose(
            self.user_scale_y, 1.0
        ):
            self.user_scaling = False
        else:
            self.user_scaling = True

    def set_rotation(self, angle: int) -> None:
        pass

    def page_point(self, x: float, y: float) -> Vec2:
        """Returns the page location as page point in plotter units."""
        return self.page_vector(x, y) + self.user_origin

    def page_vector(self, x: float, y: float) -> Vec2:
        """Returns the user vector in page vector in plotter units."""
        if self.user_scaling:
            x = self.user_scale_x * x
            y = self.user_scale_y * y
        return Vec2(x, y)

    def page_points(self, points: Sequence[Vec2]) -> list[Vec2]:
        """Returns all user points as page points in plotter units."""
        return [self.page_point(p.x, p.y) for p in points]

    def page_vectors(self, vectors: Sequence[Vec2]) -> list[Vec2]:
        """Returns all user vectors as page vectors in plotter units."""
        return [self.page_vector(p.x, p.y) for p in vectors]

    def scale_length(self, length: float) -> tuple[float, float]:
        """Scale a length in user units to plotter units, scaling can be non-uniform."""
        return length * self.user_scale_x, length * self.user_scale_y


def get_page_size(name: str, landscape=True) -> tuple[int, int]:
    """Returns the page size in plot units (plu)."""
    units, size_x, size_y = PAGE_SIZES.get(name, PAGE_SIZES["ISO A0"])
    if units == "mm":
        size_x *= MM_TO_PLU
        size_y *= MM_TO_PLU
    elif units == "inch":
        size_x *= INCH_TO_PLU
        size_y *= INCH_TO_PLU
    if landscape:
        return int(size_x), int(size_y)
    else:
        return int(size_y), int(size_x)
