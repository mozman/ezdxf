#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Iterable, Tuple
import math
from ezdxf.math import Vec3, Vec2, Matrix44, BoundingBox
from ezdxf.addons.drawing.backend import Backend
from ezdxf.addons.drawing.properties import Properties
from ezdxf.addons.drawing.type_hints import Color

from ezdxf.tools.fonts import FontFace, FontMeasurements

from PIL import Image, ImageDraw


class PillowBackend(Backend):
    def __init__(
        self,
        layout_bbox: BoundingBox,
        image_size: Tuple[int, int] = None,
        resolution: float = 1.0,
        margin: int = 10,
        stretch=False,
    ):
        """Experimental backend to use Pillow for image export.

        Current limitations:

            - no text support
            - no linetype support
            - no lineweight support
            - no hatch pattern support

        Args:
            layout_bbox: bounding box of the layout in DXF drawing units
            image_size: image output size in pixels or ``None`` to be calculated
                by the bounding box size and the `resolution`
            margin: image margin in pixels
            resolution: pixels per DXF drawing unit, e.g. 100 is for 100 pixels
                per drawing unit, "meter" as drawing unit means each pixel
                represents a size of 1cm x 1cm.
                If the `image_size` is given the `resolution` is calculated
                automatically
            stretch: `False` to adjust the image height according the DXF extends

        """
        super().__init__()
        self.layout_extends = Vec2(layout_bbox.size)
        self.layout_offset = Vec2(layout_bbox.extmin)
        self.margin = int(margin)

        if image_size is None:
            image_size = (
                math.ceil(self.layout_extends.x * resolution + 2 * self.margin),
                math.ceil(self.layout_extends.y * resolution + 2 * self.margin),
            )
            self.scale_x = self.layout_extends.x * resolution
            self.scale_y = self.layout_extends.y * resolution
        else:
            img_x, img_y = image_size
            if not stretch:
                ratio = self.layout_extends.y / self.layout_extends.x
                img_y = img_x * ratio
                image_size = (img_x, img_y)
            self.scale_x = (img_x - 2 * margin) / self.layout_extends.x
            self.scale_y = (img_y - 2 * margin) / self.layout_extends.y

        self.image_size = Vec2(image_size)
        self.bg_color: Color = "#000000"
        self.image_mode = "RGBA"
        self.clear()

    # noinspection PyAttributeOutsideInit,PyTypeChecker
    def clear(self):
        x = int(self.image_size.x)
        y = int(self.image_size.y)
        self.image = Image.new(
            self.image_mode, (x, y), color=self.bg_color
        )
        self.draw = ImageDraw.Draw(self.image)

    def set_background(self, color: Color) -> None:
        self.bg_color = color
        self.clear()

    def pixel_loc(self, point: Vec3) -> Tuple[int, int]:
        x = (point.x - self.layout_offset.x) * self.scale_x + self.margin
        y = (point.y - self.layout_offset.y) * self.scale_y + self.margin
        return int(x), int(
            self.image_size.y - y
        )  # image (0, 0) is the top-left corner

    def draw_point(self, pos: Vec3, properties: Properties) -> None:
        self.draw.point([self.pixel_loc(pos)], fill=properties.color)

    def draw_line(self, start: Vec3, end: Vec3, properties: Properties) -> None:
        self.draw.line(
            [self.pixel_loc(start), self.pixel_loc(end)], fill=properties.color
        )

    def draw_filled_polygon(
        self, points: Iterable[Vec3], properties: Properties
    ) -> None:
        self.draw.polygon(
            [self.pixel_loc(p) for p in points], fill=properties.color
        )

    def draw_text(
        self,
        text: str,
        transform: Matrix44,
        properties: Properties,
        cap_height: float,
    ) -> None:
        # text is not supported yet
        pass

    def get_font_measurements(
        self, cap_height: float, font: "FontFace" = None
    ) -> FontMeasurements:
        # text is not supported yet
        return FontMeasurements(0, 1, 0.5, 0)

    def get_text_line_width(
        self, text: str, cap_height: float, font: FontFace = None
    ) -> float:
        # text is not supported yet
        return 0.0

    def export(self, filename: str, **kwargs) -> None:
        self.image.save(filename, **kwargs)

    def finalize(self) -> None:
        pass
