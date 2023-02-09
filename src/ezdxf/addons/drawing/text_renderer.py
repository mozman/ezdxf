#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import TypeVar, Generic, Optional
import abc
from ezdxf.tools.fonts import FontFace, FontMeasurements
from ezdxf.path import Path

T = TypeVar("T")


class TextRenderer(abc.ABC, Generic[T]):
    """Minimal requirement to be usable as a universal text renderer, for more
    information see usage in PillowBackend().

    Implementations:

        - MplTextRenderer
        - QtTextRenderer

    """
    @abc.abstractmethod
    def get_font_properties(self, font: FontFace) -> T:
        ...

    @abc.abstractmethod
    def get_font_measurements(self, font_properties: T) -> FontMeasurements:
        ...

    @abc.abstractmethod
    def get_scale(self, cap_height: float, font_properties: T) -> float:
        ...

    @abc.abstractmethod
    def get_text_line_width(
        self, text: str, cap_height: float, font: Optional[FontFace] = None
    ) -> float:
        ...

    @abc.abstractmethod
    def get_ezdxf_path(self, text: str, font_properties: T) -> Path:
        ...

