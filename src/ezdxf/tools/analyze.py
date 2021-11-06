#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
#  Debugging tools to analyze DXF entities.

import ezdxf
from ezdxf.math import Vec2
from ezdxf.lldxf import const

from ezdxf.entities import (
    Hatch,
    EdgePath,
    PolylinePath,
    LineEdge,
    ArcEdge,
    EllipseEdge,
    SplineEdge,
)

EDGE_START_MARKER = "EDGE_START_MARKER"
EDGE_END_MARKER = "EDGE_END_MARKER"
HATCH_LAYER = "HATCH"
POLYLINE_LAYER = "POLYLINE_MARKER"
LINE_LAYER = "LINE_MARKER"
ARC_LAYER = "ARC_MARKER"
ELLIPSE_LAYER = "ELLIPSE_MARKER"
SPLINE_LAYER = "SPLINE_MARKER"


class HatchAnalyzer:
    def __init__(
        self,
        *,
        marker_size: float = 1.0,
        angle: float = 45,
    ):
        self.marker_size = marker_size
        self.angle = angle
        self.doc = ezdxf.new()
        self.msp = self.doc.modelspace()
        self._setup_doc()

    def _setup_doc(self):
        self.init_layers()
        self.init_markers()

    def add_hatch(self, hatch: Hatch) -> None:
        hatch.dxf.discard("extrusion")
        hatch.dxf.layer = HATCH_LAYER
        self.msp.add_foreign_entity(hatch)

    def add_boundary_markers(self, hatch: Hatch) -> None:
        hatch.dxf.discard("extrusion")
        path_num: int = 0

        for p in hatch.paths:
            path_num += 1
            if isinstance(p, PolylinePath):
                self.add_polyline_markers(p, path_num)
            elif isinstance(p, EdgePath):
                self.add_edge_markers(p, path_num)
            else:
                raise TypeError(f"unknown boundary path type: {type(p)}")

    def export(self, name: str) -> None:
        self.doc.saveas(name)

    def init_layers(self):
        self.doc.layers.add(POLYLINE_LAYER, color=const.YELLOW)
        self.doc.layers.add(LINE_LAYER, color=const.RED)
        self.doc.layers.add(ARC_LAYER, color=const.GREEN)
        self.doc.layers.add(ELLIPSE_LAYER, color=const.MAGENTA)
        self.doc.layers.add(SPLINE_LAYER, color=const.CYAN)
        self.doc.layers.add(HATCH_LAYER)

    def init_markers(self):
        blk = self.doc.blocks.new(EDGE_START_MARKER)
        attribs = {"layer": "0"}  # from INSERT
        radius = self.marker_size / 2.0
        height = radius

        # start marker: 0-- name
        blk.add_circle(
            center=(0, 0),
            radius=radius,
            dxfattribs=attribs,
        )
        text_start = radius * 4
        blk.add_line(
            start=(radius, 0),
            end=(text_start - radius / 2.0, 0),
            dxfattribs=attribs,
        )
        text = blk.add_attdef(
            tag="NAME",
            dxfattribs=attribs,
        )
        text.dxf.height = height
        text.set_pos((text_start, 0), align="MIDDLE_LEFT")

        # end marker: name --X
        blk = self.doc.blocks.new(EDGE_END_MARKER)
        attribs = {"layer": "0"}  # from INSERT
        blk.add_line(
            start=(-radius, -radius),
            end=(radius, radius),
            dxfattribs=attribs,
        )
        blk.add_line(
            start=(-radius, radius),
            end=(radius, -radius),
            dxfattribs=attribs,
        )
        text_start = -radius * 4
        blk.add_line(
            start=(-radius, 0),
            end=(text_start + radius / 2.0, 0),
            dxfattribs=attribs,
        )
        text = blk.add_attdef(
            tag="NAME",
            dxfattribs=attribs,
        )
        text.dxf.height = height
        text.set_pos((text_start, 0), align="MIDDLE_RIGHT")

    def add_start_marker(self, location: Vec2, name: str, layer: str) -> None:
        self.add_marker(EDGE_START_MARKER, location, name, layer)

    def add_end_marker(self, location: Vec2, name: str, layer: str) -> None:
        self.add_marker(EDGE_END_MARKER, location, name, layer)

    def add_marker(self, blk_name: str, location: Vec2, name: str, layer: str) -> None:
        blkref = self.msp.add_blockref(
            name=blk_name,
            insert=location,
            dxfattribs={
                "layer": layer,
                "rotation": self.angle,
            },
        )
        blkref.add_auto_attribs({"NAME": name})

    def add_polyline_markers(self, p: PolylinePath, num: int) -> None:
        self.add_start_marker(Vec2(p.vertices[0]), f"Poly-S({num})", POLYLINE_LAYER)
        self.add_end_marker(Vec2(p.vertices[0]), f"Poly-E({num})", POLYLINE_LAYER)

    def add_edge_markers(self, p: EdgePath, num: int) -> None:
        edge_num: int = 0
        for edge in p.edges:
            edge_num += 1
            name = f"({num}.{edge_num})"
            if isinstance(
                edge,
                LineEdge,
            ):
                self.add_line_edge_markers(edge, name)
            elif isinstance(edge, ArcEdge):
                self.add_arc_edge_markers(edge, name)
            elif isinstance(edge, EllipseEdge):
                self.add_ellipse_edge_markers(edge, name)
            elif isinstance(edge, SplineEdge):
                self.add_spline_edge_markers(edge, name)
            else:
                raise TypeError(f"unknown edge type: {type(edge)}")

    def add_line_edge_markers(self, line: LineEdge, name: str) -> None:
        self.add_start_marker(line.start, "Line-S" + name, LINE_LAYER)
        self.add_end_marker(line.end, "Line-E" + name, LINE_LAYER)

    def add_arc_edge_markers(self, arc: ArcEdge, name: str) -> None:
        ctool = arc.construction_tool()
        self.add_start_marker(ctool.start_point, "Arc-S" + name, ARC_LAYER)
        self.add_end_marker(ctool.end_point, "Arc-E" + name, ARC_LAYER)

    def add_ellipse_edge_markers(self, ellipse: EllipseEdge, name: str) -> None:
        ctool = ellipse.construction_tool()
        self.add_start_marker(ctool.start_point.vec2, "Ellipse-S" + name, ELLIPSE_LAYER)
        self.add_end_marker(ctool.end_point.vec2, "Ellipse-E" + name, ELLIPSE_LAYER)

    def add_spline_edge_markers(self, spline: SplineEdge, name: str) -> None:
        if len(spline.control_points):
            # Assuming a clamped B-spline, because this is the only practical
            # usable B-spline for edges.
            self.add_start_marker(spline.control_points[0], "SplineS" + name, SPLINE_LAYER)
            self.add_end_marker(spline.control_points[-1], "SplineE" + name, SPLINE_LAYER)
