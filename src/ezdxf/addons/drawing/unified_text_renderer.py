# Copyright (c) 2023, Matthew Broadway
# License: MIT License
from __future__ import annotations
from typing import Iterator, Optional, Sequence
import time
import logging
import pathlib

import ezdxf.path
from ezdxf.tools.fonts import FontMeasurements
from ezdxf.tools import fonts
from ezdxf.math import Vec2
from ezdxf.math.triangulation import mapbox_earcut_2d
from .text_renderer import TextRenderer
from ezdxf.tools.ttfonts import TTFontRenderer, FontManager
from ezdxf import options

logger = logging.getLogger("ezdxf")
FONT_MANAGER_CACHE_FILE = "font_manager_cache.json"
CACHE_DIRECTORY = ".cache"


class UnifiedTextRenderer(TextRenderer[fonts.FontFace]):
    """This text renderer should render TTF and SHX fonts.

    - TTF rendering is bases on the fontTools package
    - SHX rendering is done by the ezdxf.shapefile module
    """

    def __init__(self, font=fonts.FontFace()):
        self.font_manager: FontManager = FontManager()
        self._default_font = font
        # Each font has its own text path cache
        # key is hash(FontProperties)
        self._text_renderer_cache: dict[int, TTFontRenderer] = dict()

    def load_font_manager(self) -> None:
        cache_path = options.xdg_path(CACHE_DIRECTORY, CACHE_DIRECTORY)
        fm_path = fonts.get_cache_file_path(cache_path, FONT_MANAGER_CACHE_FILE)
        if fm_path.exists():
            t0 = time.perf_counter()
            self.font_manager.loads(fm_path.read_text())
            logger.info(
                f"loaded FileManager cache in {time.perf_counter()-t0:.4f} seconds"
            )
        else:
            self.build_font_manager_cache(fm_path)

    def build_font_manager_cache(self, path: pathlib.Path) -> None:
        t0 = time.perf_counter()
        self.font_manager.build()
        logger.info(
            f"build FontManager cache in {time.perf_counter() - t0:.4f} seconds"
        )
        s = self.font_manager.dumps()
        path.parent.mkdir(parents=True)
        path.write_text(s)
        logger.info(f"FontManger cache written: {path}")

    def get_text_renderer(self, font_face: fonts.FontFace) -> TTFontRenderer:
        font_name = pathlib.Path(font_face.ttf).name
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
    def default_font(self) -> fonts.FontFace:
        fallback_name = self.font_manager.fallback_font_name()
        return self.font_manager.get_font_face(fallback_name)

    def clear_cache(self):
        self._text_renderer_cache.clear()

    def get_scale(self, desired_cap_height: float, font: fonts.FontFace) -> float:
        # todo: will be removed - add argument cap_height to get_text_path()
        engine = self.get_text_renderer(font)
        return engine.get_scaling_factor(desired_cap_height)

    def get_font_properties(self, font: Optional[fonts.FontFace]) -> fonts.FontFace:
        # todo: will be removed
        if font is None:
            return self.default_font
        return font

    def get_font_measurements(self, font_face: fonts.FontFace) -> FontMeasurements:
        # will be removed
        ttf_font = self.font_manager.ttf_font_from_font_face(font_face)
        return TTFontRenderer(ttf_font).font_measurements
        # None is the default font.

    def get_text_path(self, text: str, font: fonts.FontFace) -> ezdxf.path.Path2d:
        # todo: add argument cap_height
        engine = self.get_text_renderer(font)
        return engine.get_text_path(text)

    def get_text_line_width(
        self,
        text: str,
        cap_height: float,
        font: Optional[fonts.FontFace] = None,
    ) -> float:
        engine = self.get_text_renderer(font)
        return engine.get_text_length(text, cap_height)

    def get_ezdxf_path(self, text: str, font: fonts.FontFace) -> ezdxf.path.Path:
        # todo: will be removed
        text_path = self.get_text_path(text, font)
        return text_path.to_3d_path()

    def get_tessellation(
        self,
        text: str,
        font: fonts.FontFace,
        *,
        max_flattening_distance: float = 0.01,
    ) -> Iterator[Sequence[Vec2]]:
        """Triangulate text into faces.

        !!! Does not work for any arbitrary text !!!
        """
        for polygon in ezdxf.path.nesting.group_paths(
            list(self.get_text_path(text, font).sub_paths())
        ):
            if len(polygon) == 0:
                continue
            exterior = polygon[0]
            holes = polygon[1:]
            yield from mapbox_earcut_2d(
                exterior.flattening(max_flattening_distance),
                [hole.flattening(max_flattening_distance) for hole in holes],
            )
