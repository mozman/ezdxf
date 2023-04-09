#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence

from ezdxf.gfxattribs import GfxAttribs
from ezdxf.lldxf.const import VALID_DXF_LINEWEIGHTS
from ezdxf.entities import Hatch
import ezdxf.path

from .deps import Vec2, Path
from .properties import RGB, Properties
from .backend import Backend

if TYPE_CHECKING:
    from ezdxf.eztypes import GenericLayoutType


class DXFBackend(Backend):
    def __init__(self, layout: GenericLayoutType) -> None:
        super().__init__()
        self.layout = layout

    def draw_cubic_bezier(
        self, properties: Properties, start: Vec2, ctrl1: Vec2, ctrl2: Vec2, end: Vec2
    ) -> None:
        pass

    def draw_circle(
        self, properties: Properties, center: Vec2, rx: float, ry: float
    ) -> None:
        pass

    def draw_polyline(self, properties: Properties, points: Sequence[Vec2]) -> None:
        if len(points) == 0:
            return

        attribs = self.make_dxf_attribs(properties)
        if len(points) > 2:
            self.layout.add_lwpolyline(points, dxfattribs=attribs)
        elif len(points) == 2:
            self.layout.add_line(points[0], points[1], dxfattribs=attribs)
        else:
            self.layout.add_point(points[0], dxfattribs=attribs)

    def make_dxf_attribs(self, properties: Properties):
        aci = properties.pen_index
        if aci < 1 or aci > 255:
            aci = 7
        attribs = GfxAttribs(
            color=aci,
            lineweight=self.make_lineweight(properties.pen_width),
            layer=f"COLOR_{aci}",
        )
        color = properties.pen_color
        if color != RGB(0, 0, 0):
            attribs.rgb = color
        return attribs

    @staticmethod
    def make_lineweight(width: float) -> int:
        width_int = int(width * 100)
        for lw in VALID_DXF_LINEWEIGHTS:
            if width_int <= lw:
                return lw
        return VALID_DXF_LINEWEIGHTS[-1]

    def draw_filled_polygon(
        self, properties: Properties, paths: Sequence[Path], fill_method: int
    ) -> None:
        # path in page coordinates!
        attribs = self.make_dxf_attribs(properties)
        hatches = ezdxf.path.render_hatches(self.layout, paths, dxfattribs=attribs)
        for hatch in hatches:
            assert isinstance(hatch, Hatch)
            hatch.set_solid_fill(color=attribs.color, style=0, rgb=attribs.rgb)

    def draw_outline_polygon(
        self, properties: Properties, paths: Sequence[Path]
    ) -> None:
        # path in page coordinates!
        attribs = self.make_dxf_attribs(properties)
        ezdxf.path.render_splines_and_polylines(self.layout, paths, dxfattribs=attribs)
