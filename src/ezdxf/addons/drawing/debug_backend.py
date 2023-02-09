#  Copyright (c) 2021-2022, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Iterable, Optional
from ezdxf.math import Vec3, Matrix44
from ezdxf.tools.fonts import FontMeasurements, FontFace
from ezdxf.path import Path
from .properties import Properties
from .backend import Backend
from .config import Configuration


class BasicBackend(Backend):
    """The basic backend has no draw_path() support and approximates all curves
    by lines.
    """

    def __init__(self):
        super().__init__()
        self.collector = []
        self.configure(Configuration.defaults())

    def draw_point(self, pos: Vec3, properties: Properties) -> None:
        self.collector.append(("point", pos, properties))

    def draw_line(self, start: Vec3, end: Vec3, properties: Properties) -> None:
        self.collector.append(("line", start, end, properties))

    def draw_filled_polygon(
        self, points: Iterable[Vec3], properties: Properties
    ) -> None:
        self.collector.append(("filled_polygon", list(points), properties))

    def draw_text(
        self,
        text: str,
        transform: Matrix44,
        properties: Properties,
        cap_height: float,
    ) -> None:
        self.collector.append(("text", text, transform, properties))

    def get_font_measurements(
        self, cap_height: float, font=None
    ) -> FontMeasurements:
        return FontMeasurements(
            baseline=0.0, cap_height=1.0, x_height=0.5, descender_height=0.2
        )

    def set_background(self, color: str) -> None:
        self.collector.append(("bgcolor", color))

    def get_text_line_width(
        self, text: str, cap_height: float, font: Optional[FontFace] = None
    ) -> float:
        return len(text)

    def clear(self) -> None:
        self.collector = []


class PathBackend(BasicBackend):
    def draw_path(self, path: Path, properties: Properties) -> None:
        self.collector.append(("path", path, properties))
