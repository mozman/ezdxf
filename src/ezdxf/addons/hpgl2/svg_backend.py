#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Sequence, Iterable
from xml.etree import ElementTree as ET

from .deps import Vec2, Path, BoundingBox2d, AnyVec
from .backend import Backend
from .properties import Properties, RGB, RGB_NONE

LENGTH_MM = "{0:.0f}mm"


class SVGBackend(Backend):
    def __init__(self, bbox: BoundingBox2d) -> None:
        assert bbox.has_data
        size = bbox.size
        width = str(round(size.x))
        height = str(round(size.y))

        self.root = ET.Element(
            "svg",
            xmlns="http://www.w3.org/2000/svg",
            width=LENGTH_MM.format(size.x / 40.0),
            height=LENGTH_MM.format(size.y / 40.0),
            viewBox=f"0 0 {width} {height}",
        )
        self.background = ET.SubElement(
            self.root, "rect", fill="white", x="0", y="0", width=width, height=height
        )
        self.filled_polygons = ET.SubElement(
            self.root, "g", stroke="none", fill="black"
        )
        self.polylines = ET.SubElement(self.root, "g", stroke="black", fill="none")
        self.polylines.set("stroke-linecap", "round")
        self.polylines.set("stroke-linejoin", "round")

        self.max_y = bbox.extmax.y  # type: ignore
        self.min_x = bbox.extmin.x  # type: ignore

    def draw_polyline(self, properties: Properties, points: Sequence[Vec2]) -> None:
        if not points:
            return
        points = self.adjust_points(points)
        path = ET.SubElement(self.polylines, "path", d=make_path_str(points))
        path.set("stroke-width", str(round(properties.pen_width * 40)))
        s = make_rgb(properties.pen_color)
        if s:
            path.set("stroke", s)

    def draw_outline_polygon_buffer(
        self, properties: Properties, paths: Sequence[Path]
    ) -> None:
        outlines = []
        for p in paths:
            points = self.adjust_points(p.flattening(distance=10))
            s = make_path_str(points, close=True)
            if s:
                outlines.append(s)
        polygon = ET.SubElement(self.polylines, "path", d=" ".join(outlines))
        polygon.set("stroke-width", str(round(properties.pen_width * 40)))
        s = make_rgb(properties.pen_color)
        if s:
            polygon.set("stroke", s)

    def draw_filled_polygon_buffer(
        self, properties: Properties, paths: Sequence[Path]
    ) -> None:
        polygons = []
        for p in paths:
            points = self.adjust_points(p.flattening(distance=10))
            s = make_path_str(points, close=True)
            if s:
                polygons.append(s)
        polygon = ET.SubElement(self.filled_polygons, "path", d=" ".join(polygons))
        s = make_rgb(properties.pen_color)
        if s:
            polygon.set("fill", s)

    def get_string(self) -> str:
        return ET.tostring(self.root, encoding="unicode", xml_declaration=True)

    def adjust_points(self, points: Iterable[AnyVec]) -> Sequence[Vec2]:
        min_x = self.min_x
        max_y = self.max_y
        return [Vec2(p.x - min_x, max_y - p.y) for p in points]


CMD_1 = "{0} {1.x:.0f} {1.y:.0f}"
CMD_2 = "{0.x:.0f} {0.y:.0f}"


def make_path_str(points: Sequence[Vec2], close=False) -> str:
    if len(points) < 2:
        return ""
    current = points[0]
    # first move is absolute, consecutive lines are relative:
    path: list[str] = [CMD_1.format("M", current), "l"]
    for point in points[1:]:
        relative = point - current
        current = point
        path.append(CMD_2.format(relative))
    if close:
        path.append("Z")
    return " ".join(path)


def make_rgb(color: RGB) -> str:
    if color is RGB_NONE or color == (0, 0, 0):
        return ""  # use default color black
    return f"#{color.r:02x}{color.g:02x}{color.b:02x}"
