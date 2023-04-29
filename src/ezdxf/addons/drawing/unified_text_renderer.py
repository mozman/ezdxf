# Copyright (c) 2023, Manfred Moitzi
# License: MIT License
from __future__ import annotations
import pathlib

import ezdxf.path
from ezdxf.fonts import fonts
from ezdxf.fonts.font_measurements import FontMeasurements
from ezdxf.fonts.ttfonts import TTFontRenderer

from .text_renderer import TextRenderer


class UnifiedTextRenderer(TextRenderer):
    """In the future this text renderer should render TTF and SHX fonts.

    - TTF rendering is based on the fontTools package
    - SHX rendering is done by the ezdxf.shapefile module
    """

    def __init__(self, font=fonts.FontFace()) -> None:
        self.font_manager = fonts.font_manager
        self._default_font = font
        self._text_renderer_cache: dict[int, TTFontRenderer] = dict()

    def get_text_renderer(self, font_face: fonts.FontFace) -> TTFontRenderer:
        font_name = pathlib.Path(font_face.filename).name
        key = hash(font_name)
        try:
            return self._text_renderer_cache[key]
        except KeyError:
            pass
        ttfont = self.font_manager.get_ttf_font(font_name)
        engine = TTFontRenderer(ttfont)
        self._text_renderer_cache[key] = engine
        return engine

    @property
    def default_font_face(self) -> fonts.FontFace:
        fallback_name = self.font_manager.fallback_font_name()
        return self.font_manager.get_font_face(fallback_name)

    def clear_cache(self):
        self._text_renderer_cache.clear()

    def get_font_measurements(
        self, font_face: fonts.FontFace, cap_height: float = 1.0
    ) -> FontMeasurements:
        ttf_font = self.font_manager.ttf_font_from_font_face(font_face)
        font_engine = TTFontRenderer(ttf_font)
        basic_measurements = font_engine.font_measurements
        return basic_measurements.scale(font_engine.get_scaling_factor(cap_height))

    def get_text_path(
        self, text: str, font_face: fonts.FontFace, cap_height: float = 1.0
    ) -> ezdxf.path.Path2d:
        engine = self.get_text_renderer(font_face)
        return engine.get_text_path(text, cap_height)

    def get_text_line_width(
        self,
        text: str,
        font_face: fonts.FontFace,
        cap_height: float = 1.0,
    ) -> float:
        engine = self.get_text_renderer(font_face)
        return engine.get_text_length(text, cap_height)
