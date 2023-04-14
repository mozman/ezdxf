#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import NamedTuple
import dataclasses
import enum
import copy
from .deps import NULLVEC2


class FillType(enum.IntEnum):
    NONE = 0
    SOLID = 1
    HATCHING = 2
    CROSS_HATCHING = 3
    SHADING = 4


class FillMethod(enum.IntEnum):
    EVEN_ODD = 0
    NON_ZERO_WINDING = 1


class RGB(NamedTuple):
    r: int
    g: int
    b: int

    def to_floats(self) -> tuple[float, float, float]:
        return self.r / 255, self.g / 255, self.b / 255


RGB_NONE = RGB(-1, -1, -1)


@dataclasses.dataclass
class Pen:
    index: int
    width: float  # in mm
    color: RGB


class Properties:
    DEFAULT_PEN = Pen(1, 0.35, RGB_NONE)

    def __init__(self) -> None:
        # hashed content
        self.pen_index: int = 1
        self.pen_color = RGB_NONE
        self.pen_width: float = 0.35  # in mm
        self.fill_type = FillType.SOLID
        self.fill_method = FillMethod.EVEN_ODD
        self.fill_hatch_line_angle: float = 0.0  # in degrees
        self.fill_hatch_line_spacing: float = 40.0  # in plotter units
        self.fill_shading_density: float = 100.0
        self.clipping_window = (NULLVEC2, NULLVEC2)  # in plotter units
        # not hashed content
        self.max_pen_count: int = 2
        self.pen_table: dict[int, Pen] = {}
        self.reset()

    def hash(self) -> int:
        return hash(
            (
                self.pen_index,
                self.pen_color,
                self.pen_width,
                self.fill_type,
                self.fill_method,
                self.fill_hatch_line_angle,
                self.fill_hatch_line_spacing,
                self.fill_shading_density,
                self.clipping_window,
            )
        )

    def copy(self) -> Properties:
        # the pen table is shared across all copies of Properties
        return copy.copy(self)

    def reset(self) -> None:
        self.max_pen_count = 2
        self.pen_index = self.DEFAULT_PEN.index
        self.pen_color = self.DEFAULT_PEN.color
        self.pen_width = self.DEFAULT_PEN.width
        self.pen_table = {}
        self.fill_type = FillType.SOLID
        self.fill_method = FillMethod.EVEN_ODD
        self.fill_hatch_line_angle = 0.0
        self.fill_hatch_line_spacing = 40.0
        self.fill_shading_density = 1.0
        self.reset_clipping_window()

    def has_clipping_window(self) -> bool:
        return self.clipping_window[0] is not self.clipping_window[1]

    def reset_clipping_window(self) -> None:
        self.clipping_window = (NULLVEC2, NULLVEC2)

    def get_pen(self, index: int) -> Pen:
        return self.pen_table.get(index, self.DEFAULT_PEN)

    def set_max_pen_count(self, count: int) -> None:
        self.max_pen_count = count

    def set_current_pen(self, index: int) -> None:
        self.pen_index = index
        pen = self.get_pen(index)
        self.pen_width = pen.width
        self.pen_color = pen.color

    def set_pen_width(self, index: int, width: float) -> None:
        if index == -1:
            self.pen_width = width
        else:
            pen = self.pen_table.setdefault(
                index, Pen(index, width, self.DEFAULT_PEN.color)
            )
            pen.width = width

    def set_pen_color(self, index: int, rgb: RGB) -> None:
        if index == -1:
            self.pen_color = rgb
        else:
            pen = self.pen_table.setdefault(
                index, Pen(index, self.DEFAULT_PEN.width, rgb)
            )
            pen.color = rgb

    def set_fill_type(self, fill_type: int, spacing: float, angle: float):
        if fill_type == 3:
            self.fill_type = FillType.HATCHING
            self.fill_hatch_line_spacing = spacing
            self.fill_hatch_line_angle = angle
        elif fill_type == 4:
            self.fill_type = FillType.CROSS_HATCHING
            self.fill_hatch_line_spacing = spacing
            self.fill_hatch_line_angle = angle
        elif fill_type == 10:
            self.fill_type = FillType.SHADING
            self.fill_shading_density = spacing
        else:
            self.fill_type = FillType.SOLID

    def set_fill_method(self, fill_method: int) -> None:
        self.fill_method = FillMethod(fill_method)
