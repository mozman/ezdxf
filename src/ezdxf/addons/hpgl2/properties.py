#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import NamedTuple
import dataclasses
import enum
from .deps import NULLVEC2


class FillType(enum.IntEnum):
    NONE = 0
    SOLID = 1
    HATCHING = 2
    CROSS_HATCHING = 3
    SHADING = 4


class RGB(NamedTuple):
    r: int
    g: int
    b: int


@dataclasses.dataclass
class Pen:
    index: int
    width: float
    color: RGB


class Properties:
    DEFAULT_PEN = Pen(1, 0.35, RGB(0, 0, 0))

    def __init__(self) -> None:
        self.max_pen_count: int = 2
        self.pen_index: int = 1
        self.pen_color = RGB(0, 0, 0)
        self.pen_width: float = 0.35
        self.pen_table: dict[int, Pen] = {}
        self.fill_type = FillType.SOLID
        self.fill_hatch_line_angle: float = 0.0  # in degrees
        self.fill_hatch_line_spacing: float = 40.0  # in plotter units
        self.fill_shading_density: float = 100.0
        self.page_width: int = 0  # in plotter units
        self.page_height: int = 0  # in plotter units
        self.clipping_window = (NULLVEC2, NULLVEC2)  # in plotter units
        self.reset()

    def has_clipping_window(self) -> bool:
        return self.clipping_window[0] is not self.clipping_window[1]

    def reset(self) -> None:
        self.max_pen_count = 2
        self.pen_index = 1
        self.pen_color = RGB(0, 0, 0)
        self.pen_width = 0.35
        self.pen_table = {}
        self.fill_type = FillType.SOLID
        self.fill_hatch_line_angle = 0.0
        self.fill_hatch_line_spacing = 40.0
        self.fill_shading_density = 1.0
        self.reset_clipping_window()
        # do not reset the page size

    def reset_clipping_window(self) -> None:
        self.clipping_window = (NULLVEC2, NULLVEC2)

    def get_pen(self, index: int) -> Pen:
        return self.pen_table.get(index, self.DEFAULT_PEN)

    def set_page_size(self, width: int, height: int) -> None:
        # in plotter units
        self.page_width = int(width)
        self.page_height = int(height)

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
