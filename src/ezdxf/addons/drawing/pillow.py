#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Iterable, Optional
import sys
import enum
import itertools
import functools
import math
from ezdxf.math import (
    Vec3,
    Vec2,
    Matrix44,
    AbstractBoundingBox,
    AnyVec,
)
from ezdxf.math.clipping import ClippingRect2d
import ezdxf.path
from ezdxf.render import hatching
from ezdxf.addons.drawing.backend import Backend, prepare_string_for_rendering
from ezdxf.addons.drawing.properties import Properties
from ezdxf.addons.drawing.type_hints import Color

from ezdxf.tools.fonts import FontFace, FontMeasurements, MonospaceFont
from .config import Configuration

try:
    from PIL import Image, ImageDraw
except ImportError:
    # The original PIL package does not work with Python3!
    print(
        "require Pillow package not found, install by:\n\n"
        "    pip install Pillow"
    )
    sys.exit(1)

# Replace MplTextRender() by QtTextRenderer():
# from ezdxf.addons.xqt import QtWidgets as qw
# app = qw.QApplication(sys.argv)
# from .qt_text_renderer import QtTextRenderer as TextRenderer
from .mpl_text_renderer import MplTextRenderer as TextRenderer

INCH_TO_MM = 25.6


class TextMode(enum.IntEnum):
    IGNORE = 0
    PLACEHOLDER = 1
    OUTLINE = 2
    FILLED = 3


class PillowBackendException(Exception):
    pass


class PillowBackend(Backend):
    """Backend which uses the :mod:`Pillow` package for image export.

    For linetype support configure the line_policy in the frontend as
    ACCURATE.

    Args:
        region: output region of the layout in DXF drawing units
        image_size: image output size in pixels or ``None`` to be
            calculated by the region size and the `resolution`
        margin: image margin in pixels, same margin for all four borders
        resolution: pixels per DXF drawing unit, e.g. a resolution of 100
            for the drawing unit "meter" means, each pixel represents an
            area of 1cm x 1cm (1m is 100cm).
            If the `image_size` is given the `resolution` is calculated
            automatically
        dpi: output image resolution in dots per inch. The pixel width of
            lines is determined by the DXF lineweight (in mm) and this image
            resolution (dots/pixels per inch). The line width is independent
            of the drawing scale!
        oversampling: multiplier of the final image size to define the
            render canvas size (e.g. 1, 2, 3, ...), the final image will
            be scaled down by the LANCZOS method
        text_mode: text rendering mode

            - IGNORE: do not draw text
            - PLACEHOLDER: draw text as filled rectangles
            - OUTLINE: draw text as outlines (recommended)
            - FILLED: simulate text filling by hatching the text outline with
              dense lines - has some issues

    """

    def __init__(
        self,
        region: AbstractBoundingBox,
        image_size: Optional[tuple[int, int]] = None,
        resolution: float = 1.0,
        margin: int = 10,
        dpi: int = 300,
        oversampling: int = 1,
        text_mode=TextMode.OUTLINE,
    ):
        super().__init__()
        self.region = Vec2(0, 0)
        if region.has_data:
            self.region = Vec2(region.size)
        if self.region.x <= 0.0 or self.region.y <= 0.0:
            raise PillowBackendException("drawing region is empty")
        self.extmin = Vec2(region.extmin)
        self.margin_x = float(margin)
        self.margin_y = float(margin)
        self.dpi = int(dpi)
        self.oversampling = max(int(oversampling), 1)
        self.text_mode = text_mode
        # The lineweight is stored im mm,
        # line_pixel_factor * lineweight is the width in pixels
        self.line_pixel_factor = self.dpi / INCH_TO_MM  # pixel per mm
        # resolution: pixels per DXF drawing units, same resolution in all
        # directions
        self.resolution = float(resolution)
        if image_size is None:
            image_size = (
                math.ceil(self.region.x * resolution + 2.0 * self.margin_x),
                math.ceil(self.region.y * resolution + 2.0 * self.margin_y),
            )
        else:
            img_x, img_y = image_size
            if img_y < 1:
                raise ValueError(f"invalid image size: {image_size}")
            img_ratio = img_x / img_y
            region_ratio = self.region.x / self.region.y
            if img_ratio >= region_ratio:  # image fills the height
                self.resolution = (img_y - 2.0 * self.margin_y) / self.region.y
                self.margin_x = (img_x - self.resolution * self.region.x) * 0.5
            else:  # image fills the width
                self.resolution = (img_x - 2.0 * self.margin_x) / self.region.x
                self.margin_y = (img_y - self.resolution * self.region.y) * 0.5

        # angle for solid fill hatching, see method draw_filled_paths()
        self.solid_fill_hatching_angle = 0.0
        # distance to fill solid areas by hatching:
        self.solid_fill_one_pixel = 1.0 / (self.resolution * self.oversampling)
        # hatch baseline for solid fill by hatching:
        self.solid_fill_baseline = self._solid_fill_hatch_baseline(
            self.solid_fill_one_pixel
        )
        self.image_size = Vec2(image_size)
        self.bg_color: Color = "#000000"
        self.image_mode = "RGBA"
        self.text_renderer = TextRenderer(use_cache=True)

        # dummy values for declaration, both are set in clear()
        self.image = Image.new("RGBA", (10, 10))
        self.draw = ImageDraw.Draw(self.image)

        # VIEWPORT support
        self.clipper: Optional[ClippingRect2d] = None
        self.viewport_scaling: float = 1.0

    def _solid_fill_hatch_baseline(self, one_px: float):
        direction = Vec2.from_deg_angle(self.solid_fill_hatching_angle)
        offset = direction.orthogonal() * one_px
        return hatching.HatchBaseLine(Vec2(0, 0), direction, offset)

    def configure(self, config: Configuration) -> None:
        super().configure(config)
        self.line_pixel_factor *= self.config.lineweight_scaling
        # set max flattening distance for Path() objects to 1 pixel
        one_px = 1.0 / self.resolution
        self.config = self.config.with_changes(max_flattening_distance=one_px)

    # noinspection PyTypeChecker
    def clear(self):
        x = int(self.image_size.x) * self.oversampling
        y = int(self.image_size.y) * self.oversampling
        self.image = Image.new(self.image_mode, (x, y), color=self.bg_color)
        self.draw = ImageDraw.Draw(self.image)

    def set_background(self, color: Color) -> None:
        self.bg_color = color
        self.clear()

    def set_clipping_path(
        self,
        clipping_path: Optional[ezdxf.path.Path] = None,
        scale: float = 1.0,
    ) -> bool:
        if clipping_path:
            bbox = ezdxf.path.bbox((clipping_path,), fast=True)
            self.clipper = ClippingRect2d(bbox.extmin, bbox.extmax)
        else:
            self.clipper = None
        self.viewport_scaling = scale
        return True  # confirm clipping support

    def width(self, lineweight: float) -> int:
        return max(int(lineweight * self.line_pixel_factor), 1)

    def pixel_loc(self, point: AnyVec) -> tuple[float, float]:
        # Source: https://pillow.readthedocs.io/en/stable/handbook/concepts.html#coordinate-system
        # The Python Imaging Library uses a Cartesian pixel coordinate system,
        # with (0,0) in the upper left corner. Note that the coordinates refer
        # to the implied pixel corners; the centre of a pixel addressed as
        # (0, 0) actually lies at (0.5, 0.5).
        x = (point.x - self.extmin.x) * self.resolution + self.margin_x
        y = (point.y - self.extmin.y) * self.resolution + self.margin_y
        return (
            x * self.oversampling,
            # (0, 0) is the top-left corner:
            (self.image_size.y - y) * self.oversampling,
        )

    def draw_point(self, pos: Vec3, properties: Properties) -> None:
        if self.clipper and not self.clipper.is_inside(Vec2(pos)):
            return
        self.draw.point([self.pixel_loc(pos)], fill=properties.color)

    def draw_line(self, start: Vec3, end: Vec3, properties: Properties) -> None:
        if self.clipper:
            result = self.clipper.clip_line(Vec2(start), Vec2(end))
            if len(result) == 2:
                start, end = result
            else:
                return
        self.draw.line(
            [self.pixel_loc(start), self.pixel_loc(end)],
            fill=properties.color,
            width=self.width(properties.lineweight),
        )

    def draw_filled_polygon(
        self, points: Iterable[Vec3], properties: Properties
    ) -> None:
        if self.clipper:
            points = self.clipper.clip_polygon(Vec2.generate(points))
            if not len(points) < 3:
                return
        points = [self.pixel_loc(p) for p in points]
        if len(points) > 2:
            self.draw.polygon(
                points,
                fill=properties.color,
                outline=properties.color,
            )

    def draw_filled_paths(
        self,
        paths: Iterable[ezdxf.path.Path],
        holes: Iterable[ezdxf.path.Path],
        properties: Properties,
    ) -> None:
        # Uses the hatching module to draw filled paths by hatching paths with
        # solid lines with an offset of one pixel.
        all_paths = list(itertools.chain(paths, holes))
        draw_line = functools.partial(
            self.draw.line, fill=properties.color, width=self.oversampling
        )
        clip = None
        if self.clipper:
            clip = self.clipper.clip_line
        for line in hatching.hatch_paths(self.solid_fill_baseline, all_paths):
            if clip:  # todo: clip paths -> polygons
                result = clip(line.start, line.end)
                if len(result) == 2:
                    draw_line(
                        (self.pixel_loc(result[0]), self.pixel_loc(result[1]))
                    )
            else:
                draw_line(
                    (self.pixel_loc(line.start), self.pixel_loc(line.end))
                )

    def draw_text(
        self,
        text: str,
        transform: Matrix44,
        properties: Properties,
        cap_height: float,
    ) -> None:
        if self.text_mode == TextMode.IGNORE:
            return
        if self.text_mode == TextMode.PLACEHOLDER:
            # draws a placeholder rectangle as text
            width = self.get_text_line_width(text, cap_height, properties.font)
            height = cap_height
            points = Vec3.list(
                [(0, 0), (width, 0), (width, height), (0, height)]
            )
            points = list(transform.transform_vertices(points))
            self.draw_filled_polygon(points, properties)
            return

        tr = self.text_renderer
        text = self._prepare_text(text)
        font_properties = tr.get_font_properties(properties.font)
        scale = tr.get_scale(cap_height, font_properties)
        m = Matrix44.scale(scale) @ transform
        if self.text_mode == TextMode.OUTLINE:
            ezdxf_path = tr.get_ezdxf_path(text, font_properties)
            if len(ezdxf_path) == 0:
                return
            ezdxf_path = ezdxf_path.transform(m)
            for path in ezdxf_path.sub_paths():
                self.draw_path(path, properties)
        else:  # render Text as filled polygons
            ezdxf_path = tr.get_ezdxf_path(text, font_properties)
            if len(ezdxf_path) == 0:
                return
            self.draw_filled_paths(
                (p for p in ezdxf_path.transform(m).sub_paths()), [], properties
            )

    def get_font_measurements(
        self, cap_height: float, font: Optional[FontFace] = None
    ) -> FontMeasurements:
        if self.text_mode == TextMode.PLACEHOLDER:
            return MonospaceFont(cap_height).measurements
        return self.text_renderer.get_font_measurements(
            self.text_renderer.get_font_properties(font)
        ).scale_from_baseline(desired_cap_height=cap_height)

    def _prepare_text(self, text: str) -> str:
        dxftype = (
            self.current_entity.dxftype() if self.current_entity else "TEXT"
        )
        return prepare_string_for_rendering(text, dxftype)

    def get_text_line_width(
        self, text: str, cap_height: float, font: Optional[FontFace] = None
    ) -> float:
        if not text.strip():
            return 0.0
        text = self._prepare_text(text)
        if self.text_mode == TextMode.PLACEHOLDER:
            return MonospaceFont(cap_height).text_width(text) * 0.8
        return self.text_renderer.get_text_line_width(text, cap_height, font)

    def export(self, filename: str, **kwargs) -> None:
        image = self.resize()
        if not supports_transparency(filename):
            # remove alpha channel if not supported
            image = image.convert("RGB")
        dpi = kwargs.pop("dpi", self.dpi)
        image.save(filename, dpi=(dpi, dpi), **kwargs)

    def resize(self):
        image = self.image
        if self.oversampling > 1:
            x = int(self.image_size.x)
            y = int(self.image_size.y)
            image = self.image.resize((x, y), resample=Image.LANCZOS)
        return image


SUPPORT_TRANSPARENCY = [".png", ".tif", ".tiff"]


def supports_transparency(filename: str) -> bool:
    filename = filename.lower()
    return any(filename.endswith(ftype) for ftype in SUPPORT_TRANSPARENCY)
