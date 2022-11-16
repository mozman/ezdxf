# Copyright (c) 2020-2022, Matthew Broadway
# License: MIT License
from __future__ import annotations
from typing import Optional, Union
from collections import defaultdict
from functools import lru_cache
from .text_renderer import TextRenderer
from ezdxf.addons.xqt import QtCore as qc, QtGui as qg
from ezdxf.math import Matrix44
from ezdxf.tools.fonts import FontMeasurements, FontFace, weight_name_to_value
import ezdxf.path


class QtTextRenderer(TextRenderer[qg.QFont]):
    def __init__(self, font=qg.QFont(), use_cache: bool = True):
        self._default_font = font
        self._use_cache = use_cache

        # Each font has its own text path cache
        # key is QFont.key()
        self._text_path_cache: dict[
            str, dict[str, qg.QPainterPath]
        ] = defaultdict(dict)

        # Each font has its own font measurements cache
        # key is QFont.key()
        self._font_measurement_cache: dict[str, FontMeasurements] = {}

    @property
    def default_font(self) -> qg.QFont:
        return self._default_font

    def clear_cache(self):
        self._text_path_cache.clear()

    def get_scale(self, desired_cap_height: float, font: qg.QFont) -> float:
        measurements = self.get_font_measurements(font)
        return desired_cap_height / measurements.cap_height

    def get_font_properties(self, font: Optional[FontFace]) -> qg.QFont:
        if font is None:
            return self.default_font
        font_properties = _get_font(font)
        if font_properties is None:
            return self.default_font
        return font_properties

    def get_font_measurements(self, font: qg.QFont) -> FontMeasurements:
        # None is the default font.
        key = font.key() if font is not None else None
        measurements = self._font_measurement_cache.get(key)
        if measurements is None:
            upper_x = self.get_text_rect("X", font)
            lower_x = self.get_text_rect("x", font)
            lower_p = self.get_text_rect("p", font)
            baseline = lower_x.bottom()
            measurements = FontMeasurements(
                baseline=baseline,
                cap_height=baseline - upper_x.top(),
                x_height=baseline - lower_x.top(),
                descender_height=lower_p.bottom() - baseline,
            )
            self._font_measurement_cache[key] = measurements
        return measurements

    def get_text_path(self, text: str, font: qg.QFont) -> qg.QPainterPath:
        # None is the default font
        key = font.key() if font is not None else None
        cache = self._text_path_cache[key]  # defaultdict(dict)
        path = cache.get(text, None)
        if path is None:
            if font is None:
                font = self._default_font
            path = qg.QPainterPath()
            path.addText(0, 0, font, text)
            if self._use_cache:
                cache[text] = path
        return path

    def get_text_rect(self, text: str, font: qg.QFont) -> qc.QRectF:
        # no point caching the bounding rect calculation, it is very cheap
        return self.get_text_path(text, font).boundingRect()

    def get_text_line_width(
        self, text: str, cap_height: float, font: Optional[FontFace] = None
    ) -> float:
        qfont = self.get_font_properties(font)
        scale = self.get_scale(cap_height, qfont)
        return self.get_text_rect(text, qfont).right() * scale

    def get_ezdxf_path(self, text: str, font: qg.QFont) -> ezdxf.path.Path:
        try:
            text_path = self.get_text_path(text, font)
        except (RuntimeError, ValueError):
            return ezdxf.path.Path()
        return ezdxf.path.multi_path_from_qpainter_path(text_path).transform(
            Matrix44.scale(1, -1, 0)
        )


@lru_cache(maxsize=256)  # fonts.Font is a named tuple
def _get_font(font: FontFace) -> Optional[qg.QFont]:
    qfont = None
    if font:
        family = font.family
        italic = "italic" in font.style.lower()
        weight = _map_weight(font.weight)
        qfont = qg.QFont(family, weight=weight, italic=italic)
        # INFO: setting the stretch value makes results worse!
        # qfont.setStretch(_map_stretch(font.stretch))
    return qfont


# https://doc.qt.io/qt-5/qfont.html#Weight-enum
# QFont::Thin	0	0
# QFont::ExtraLight	12	12
# QFont::Light	25	25
# QFont::Normal	50	50
# QFont::Medium	57	57
# QFont::DemiBold	63	63
# QFont::Bold	75	75
# QFont::ExtraBold	81	81
# QFont::Black	87	87
def _map_weight(weight: Union[str, int]) -> int:
    if isinstance(weight, str):
        weight = weight_name_to_value(weight)
    value = int((weight / 10) + 10)  # normal: 400 -> 50
    return min(max(0, value), 99)


# https://doc.qt.io/qt-5/qfont.html#Stretch-enum
StretchMapping = {
    "ultracondensed": 50,
    "extracondensed": 62,
    "condensed": 75,
    "semicondensed": 87,
    "unstretched": 100,
    "semiexpanded": 112,
    "expanded": 125,
    "extraexpanded": 150,
    "ultraexpanded": 200,
}
