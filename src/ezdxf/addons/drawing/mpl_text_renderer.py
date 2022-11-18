# Copyright (c) 2020-2022, Matthew Broadway
# License: MIT License
from __future__ import annotations
from typing import Iterator, Optional, Sequence
from collections import defaultdict
from functools import lru_cache

from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath

import ezdxf.path
from ezdxf.tools.fonts import FontMeasurements
from ezdxf.tools import fonts
from ezdxf.math import Vec2
from ezdxf.math.triangulation import mapbox_earcut_2d
from .text_renderer import TextRenderer


@lru_cache(maxsize=256)  # fonts.Font is a named tuple
def _get_font_properties(font: fonts.FontFace) -> Optional[FontProperties]:
    # Font-definitions are created by the matplotlib FontManager(),
    # but stored as json file and could be altered by an user:
    font_properties = None
    try:
        font_properties = FontProperties(
            family=font.family,
            style=font.style,
            stretch=font.stretch,
            weight=font.weight,
        )
    except ValueError:
        pass
    return font_properties


class MplTextRenderer(TextRenderer[FontProperties]):
    def __init__(self, font=FontProperties(), use_cache: bool = True):
        self._default_font = font
        self._use_cache = use_cache

        # Each font has its own text path cache
        # key is hash(FontProperties)
        self._text_path_cache: dict[int, dict[str, TextPath]] = defaultdict(
            dict
        )

        # Each font has its own font measurements cache
        # key is hash(FontProperties)
        self._font_measurement_cache: dict[int, FontMeasurements] = {}

    @property
    def default_font(self) -> FontProperties:
        return self._default_font

    def clear_cache(self):
        self._text_path_cache.clear()

    def get_scale(
        self, desired_cap_height: float, font: FontProperties
    ) -> float:
        return desired_cap_height / self.get_font_measurements(font).cap_height

    def get_font_properties(
        self, font: Optional[fonts.FontFace]
    ) -> FontProperties:
        if font is None:
            return self.default_font
        font_properties = _get_font_properties(font)
        if font_properties is None:
            return self.default_font
        return font_properties

    def get_font_measurements(self, font: FontProperties) -> FontMeasurements:
        # None is the default font.
        key = hash(font)
        measurements = self._font_measurement_cache.get(key)
        if measurements is None:
            upper_x = self.get_text_path("X", font).vertices[:, 1].tolist()
            lower_x = self.get_text_path("x", font).vertices[:, 1].tolist()
            lower_p = self.get_text_path("p", font).vertices[:, 1].tolist()
            baseline = min(lower_x)
            measurements = FontMeasurements(
                baseline=baseline,
                cap_height=max(upper_x) - baseline,
                x_height=max(lower_x) - baseline,
                descender_height=baseline - min(lower_p),
            )
            self._font_measurement_cache[key] = measurements
        return measurements

    def get_text_path(self, text: str, font: FontProperties) -> TextPath:
        # None is the default font
        cache = self._text_path_cache[hash(font)]  # defaultdict(dict)
        path = cache.get(text, None)
        if path is None:
            if font is None:
                font = self._default_font
            # must replace $ with \$ to avoid matplotlib interpreting it as math text
            path = TextPath(
                (0, 0),
                text.replace("$", "\\$"),
                size=1,
                prop=font,
                usetex=False,
            )
            if self._use_cache:
                cache[text] = path
        return path

    def get_text_line_width(
        self,
        text: str,
        cap_height: float,
        font: Optional[fonts.FontFace] = None,
    ) -> float:
        font_properties = self.get_font_properties(font)
        try:
            path = self.get_text_path(text, font_properties)
            max_x = max(x for x, y in path.vertices)
        except (RuntimeError, ValueError):
            return 0.0
        return max_x * self.get_scale(cap_height, font_properties)

    def get_ezdxf_path(
        self, text: str, font: FontProperties
    ) -> ezdxf.path.Path:
        try:
            text_path = self.get_text_path(text, font)
        except (RuntimeError, ValueError):
            return ezdxf.path.Path()
        return ezdxf.path.multi_path_from_matplotlib_path(text_path)

    def get_tessellation(
        self,
        text: str,
        font: FontProperties,
        *,
        max_flattening_distance: float = 0.01,
    ) -> Iterator[Sequence[Vec2]]:
        """Triangulate text into faces.

        !!! Does not work for any arbitrary text !!!
        """
        for polygon in ezdxf.path.nesting.group_paths(
            list(self.get_ezdxf_path(text, font).sub_paths())
        ):
            if len(polygon) == 0:
                continue
            exterior = polygon[0]
            holes = polygon[1:]
            yield from mapbox_earcut_2d(
                exterior.flattening(max_flattening_distance),
                [hole.flattening(max_flattening_distance) for hole in holes],
            )
