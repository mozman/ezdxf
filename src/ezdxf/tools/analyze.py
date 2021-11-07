#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
#  Debugging tools to analyze DXF entities.
from typing import List
import ezdxf
from ezdxf.math import Vec2
from ezdxf.lldxf import const

from ezdxf.entities import (
    EdgePath,
    PolylinePath,
    LineEdge,
    ArcEdge,
    EllipseEdge,
    SplineEdge,
)
from ezdxf.entities.polygon import DXFPolygon

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

    def add_hatch(self, hatch: DXFPolygon) -> None:
        hatch.dxf.discard("extrusion")
        hatch.dxf.layer = HATCH_LAYER
        self.msp.add_foreign_entity(hatch)

    def add_boundary_markers(self, hatch: DXFPolygon) -> None:
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

    def add_marker(
        self, blk_name: str, location: Vec2, name: str, layer: str
    ) -> None:
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
        self.add_start_marker(
            Vec2(p.vertices[0]), f"Poly-S({num})", POLYLINE_LAYER
        )
        self.add_end_marker(
            Vec2(p.vertices[0]), f"Poly-E({num})", POLYLINE_LAYER
        )

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
        self.add_start_marker(arc.start_point, "Arc-S" + name, ARC_LAYER)
        self.add_end_marker(arc.end_point, "Arc-E" + name, ARC_LAYER)

    def add_ellipse_edge_markers(self, ellipse: EllipseEdge, name: str) -> None:
        self.add_start_marker(
            ellipse.start_point, "Ellipse-S" + name, ELLIPSE_LAYER
        )
        self.add_end_marker(
            ellipse.end_point, "Ellipse-E" + name, ELLIPSE_LAYER
        )

    def add_spline_edge_markers(self, spline: SplineEdge, name: str) -> None:
        if len(spline.control_points):
            # Assuming a clamped B-spline, because this is the only practical
            # usable B-spline for edges.
            self.add_start_marker(
                spline.start_point, "SplineS" + name, SPLINE_LAYER
            )
            self.add_end_marker(
                spline.end_point, "SplineE" + name, SPLINE_LAYER
            )

    @staticmethod
    def report(hatch: DXFPolygon):
        return hatch_report(hatch)

    @staticmethod
    def print_report(hatch: DXFPolygon) -> None:
        print("\n".join(hatch_report(hatch)))


def hatch_report(hatch: DXFPolygon) -> List[str]:
    dxf = hatch.dxf
    style = const.ISLAND_DETECTION[dxf.hatch_style]
    pattern_type = const.HATCH_PATTERN_TYPE[dxf.pattern_type]
    text = [
        f"{str(hatch)}",
        f"   solid fill: {bool(dxf.solid_fill)}",
        f"   pattern type: {pattern_type}",
        f"   pattern name: {dxf.pattern_name}",
        f"   associative: {bool(dxf.associative)}",
        f"   island detection: {style}",
        f"   has pattern data: {hatch.pattern is not None}",
        f"   has gradient data: {hatch.gradient is not None}",
        f"   seed value count: {len(hatch.seeds)}",
        f"   boundary path count: {len(hatch.paths)}",
    ]
    num = 0
    for path in hatch.paths:
        num += 1
        if isinstance(path, PolylinePath):
            text.extend(polyline_path_report(path, num))
        elif isinstance(path, EdgePath):
            text.extend(edge_path_report(path, num))
    return text


def polyline_path_report(p: PolylinePath, num: int) -> List[str]:
    path_type = ", ".join(const.boundary_path_flag_names(p.path_type_flags))
    return [
        f"{num}. Polyline Path, vertex count: {len(p.vertices)}",
        f"   path type:                      {path_type}",
    ]


def edge_path_report(p: EdgePath, num: int) -> List[str]:
    closed = False
    connected = False
    path_type = ", ".join(const.boundary_path_flag_names(p.path_type_flags))
    edges = p.edges
    if len(edges):
        closed = edges[0].start_point.isclose(edges[-1].end_point)
        connected = all(
            e1.end_point.isclose(e2.start_point)
            for e1, e2 in zip(edges, edges[1:])
        )

    return [
        f"{num}. Edge Path, edge count: {len(p.edges)}",
        f"   path type:                      {path_type}",
        f"   continuously connected edges:   {connected}",
        f"   closed edge loop:               {closed}",
    ]
