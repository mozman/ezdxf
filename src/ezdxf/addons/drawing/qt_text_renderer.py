# Copyright (c) 2020-2022, Matthew Broadway
# License: MIT License
from typing import Dict
from collections import defaultdict
from ezdxf.addons.xqt import QtCore as qc, QtGui as qg
from ezdxf.tools.fonts import FontMeasurements


class QtTextRenderer:
    def __init__(self, font=qg.QFont(), use_cache: bool = True):
        self._default_font = font
        self._use_cache = use_cache

        # Each font has its own text path cache
        # key is QFont.key()
        self._text_path_cache: Dict[
            str, Dict[str, qg.QPainterPath]
        ] = defaultdict(dict)

        # Each font has its own font measurements cache
        # key is QFont.key()
        self._font_measurement_cache: Dict[str, FontMeasurements] = {}

    @property
    def default_font(self) -> qg.QFont:
        return self._default_font

    def clear_cache(self):
        self._text_path_cache.clear()

    def get_scale(self, desired_cap_height: float, font: qg.QFont) -> float:
        measurements = self.get_font_measurements(font)
        return desired_cap_height / measurements.cap_height

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
