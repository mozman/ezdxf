#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Sequence
import fitz
from ezdxf.version import __version__
from .deps import Vec2, Path, BoundingBox2d
from .properties import Properties, RGB
from .backend import Backend

# Page coordinates are always plot units:
# 1 plot unit (plu) = 0.025mm
# 40 plu = 1mm
# 1016 plu = 1 inch
# 3.39 plu = 1 dot @300 dpi
# positive x-axis is horizontal from left to right
# positive y-axis is vertical from bottom to top

# Plot units to PDF units 1 PU = 1/72 inch
PLU2PU = 72.0 / 1016.0
MM2PU = 72.0 / 25.4  # 1 inch = 25.4 mm


class PDFBackend(Backend):
    def __init__(self, bbox: BoundingBox2d) -> None:
        assert bbox.has_data is True, "extents of page are required"
        self.doc = fitz.open()
        self.doc.set_metadata({
            "producer": f"PyMuPDF {fitz.version[0]}",
            "creator": f"ezdxf {__version__}",
        })
        self.max_y = bbox.extmax.y  # type: ignore
        size = bbox.size
        self.page = self.doc.new_page(-1, int(size.x * PLU2PU), int(size.y * PLU2PU))

    def draw_polyline(self, properties: Properties, points: Sequence[Vec2]) -> None:
        # input coordinates are page coordinates
        # argument <points> can be zero, one, two or more points.
        count = len(points)
        if count == 0:
            return
        points = self.adjust_points(points)
        shape = self.page.new_shape()
        if count == 1:
            shape.drawLine(points[0], points[0])
        elif count == 2:
            shape.drawLine(points[0], points[1])
        else:
            shape.drawPolyline(points)
        shape.finish(
            width=properties.pen_width,
            color=properties.pen_color.to_floats(),
            lineJoin=1,
            lineCap=1,
            closePath=False,
        )
        shape.commit()

    def draw_filled_polygon(
        self, properties: Properties, paths: Sequence[Path]
    ) -> None:
        # input coordinates are page coordinates
        if len(paths) == 0:
            return
        shape = self.page.new_shape()
        for path in paths:
            points = self.adjust_points(path.flattening(distance=10))
            if len(points) < 3:
                continue
            shape.drawPolyline(points)
        shape.finish(
            width=properties.pen_width,
            fill=properties.pen_color.to_floats(),
        )
        shape.commit()

    def get_bytes(self) -> bytes:
        return self.doc.tobytes()

    def adjust_points(self, points) -> list[Vec2]:
        max_y = self.max_y
        return [Vec2(p.x * PLU2PU, (max_y - p.y) * PLU2PU) for p in points]
