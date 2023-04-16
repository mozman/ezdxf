#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, Optional
import enum

from functools import lru_cache
from ezdxf.gfxattribs import GfxAttribs
from ezdxf.lldxf.const import VALID_DXF_LINEWEIGHTS, BYLAYER
from ezdxf.entities import Hatch
import ezdxf.path

from .deps import Vec2, Path
from .properties import Properties, RGB_NONE, RGB
from .backend import Backend

if TYPE_CHECKING:
    from ezdxf.eztypes import GenericLayoutType


class ColorMode(enum.Enum):
    # Use color index as primary color, ignores RGB color except for solid fill
    ACI = enum.auto()

    # Use always the RGB value
    RGB = enum.auto()


BLACK_RGB = RGB(0, 0, 0)
WHITE_RGB = RGB(255, 255, 255)


class DXFBackend(Backend):
    """DXF backend.

    The page content will be created in any given layout and 1 drawing unit is 1 plot
    unit (1 plu = 0.025mm).

    All entities are assigned to a layer according to the pen number with the name schema
    ``COLOR_<#>``. In order to be able to process the file better, it is also possible to
    assign an :term:`ACI` color to the DXF entities according to the pen number by setting
    the argument `color_mode` to :attr:`ColorMode.ACI`, but then the RGB color is lost
    because the RGB color has always the higher priority over the :term:`ACI`.

    Args:
        layout: any layout, modelspace, paperspace or block
        color_mode: class:`ColorMode`
        map_black_rgb_to_white_rgb: maps black fillings and lines to white.

    """
    def __init__(
        self,
        layout: GenericLayoutType,
        color_mode=ColorMode.RGB,
        map_black_rgb_to_white_rgb=False,
    ) -> None:
        super().__init__()
        self.layout = layout

        doc = layout.doc
        if doc is not None:
            self.layers = doc.layers
        else:
            self.layers = None
        self.color_mode = color_mode

        # map black RGB to white RGB, does not affect ACI colors:
        self.map_black_rgb_to_white_rgb = map_black_rgb_to_white_rgb

    def draw_polyline(self, properties: Properties, points: Sequence[Vec2]) -> None:
        count = len(points)
        if count == 0:
            return
        attribs = self.make_dxf_attribs(properties)
        if count > 2:
            self.layout.add_lwpolyline(points, dxfattribs=attribs)
        elif count == 2:
            self.layout.add_line(points[0], points[1], dxfattribs=attribs)
        else:
            self.layout.add_point(points[0], dxfattribs=attribs)

    def draw_filled_polygon(
        self, properties: Properties, paths: Sequence[Path]
    ) -> None:
        attribs = self.make_dxf_attribs(properties)
        # max sagitta distance of 10 plu = 0.25 mm
        hatches = ezdxf.path.render_hatches(
            self.layout, paths, edge_path=False, dxfattribs=attribs, distance=10
        )
        for hatch in hatches:
            assert isinstance(hatch, Hatch)
            rgb: Optional[RGB] = properties.pen_color
            if self.color_mode == ColorMode.ACI:
                rgb = RGB_NONE
            if self.map_black_rgb_to_white_rgb and rgb == BLACK_RGB:
                rgb = WHITE_RGB
            if rgb is RGB_NONE:
                rgb = None
            hatch.set_solid_fill(color=attribs.color, style=0, rgb=rgb)

    def make_dxf_attribs(self, properties: Properties):
        aci = properties.pen_index
        if aci < 1 or aci > 255:
            aci = 7

        layer = f"COLOR_{aci}"
        if self.layers and not self.layers.has_entry(layer):
            self.layers.add(name=layer, color=aci)

        attribs = GfxAttribs(
            color=BYLAYER,
            lineweight=make_lineweight(properties.pen_width),
            layer=layer,
        )
        if self.color_mode == ColorMode.RGB:
            color = properties.pen_color
            if color is not RGB_NONE:
                if self.map_black_rgb_to_white_rgb and color == BLACK_RGB:
                    color = WHITE_RGB
                attribs.rgb = color
        return attribs


@lru_cache(maxsize=None)
def make_lineweight(width: float) -> int:
    width_int = int(width * 100)
    for lw in VALID_DXF_LINEWEIGHTS:
        if width_int <= lw:
            return lw
    return VALID_DXF_LINEWEIGHTS[-1]
