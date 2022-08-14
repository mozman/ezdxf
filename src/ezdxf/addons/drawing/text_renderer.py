#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import TypeVar
from typing_extensions import Protocol
from ezdxf.tools.fonts import FontFace, FontMeasurements
from ezdxf.path import Path

T = TypeVar("T")


class TextRenderer(Protocol):
    """Minimal requirement to be usable as a universal text renderer, for more
    information see usage in PillowBackend().

    Implementations:

        - MplTextRenderer
        - QtTextRenderer

    """
    def get_font_properties(self, font: FontFace) -> T:
        ...

    def get_font_measurements(self, font_properties: T) -> FontMeasurements:
        ...

    def get_scale(self, cap_height: float, font_properties: T) -> float:
        ...

    def get_text_line_width(
        self, text: str, cap_height: float, font: FontFace = None
    ) -> float:
        ...

    def get_ezdxf_path(self, text: str, font_properties: T) -> Path:
        ...

