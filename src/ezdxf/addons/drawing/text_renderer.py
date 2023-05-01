#  Copyright (c) 2022-2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import TypeVar
import abc
from ezdxf.fonts import fonts
from ezdxf.path import Path2d

T = TypeVar("T")


class TextRenderer(abc.ABC):
    """Minimal requirement to be usable as a universal text renderer"""

    @abc.abstractmethod
    def get_font_measurements(
        self, font_face: fonts.FontFace, cap_height: float = 1.0
    ) -> fonts.FontMeasurements:
        ...

    @abc.abstractmethod
    def get_text_line_width(
        self,
        text: str,
        font_face: fonts.FontFace,
        cap_height: float = 1.0,
    ) -> float:
        ...

    @abc.abstractmethod
    def get_text_path(
        self, text: str, font_face: fonts.FontFace, cap_height: float = 1.0
    ) -> Path2d:
        ...

    @abc.abstractmethod
    def is_stroke_font(self, font_face: fonts.FontFace) -> bool:
        ...
