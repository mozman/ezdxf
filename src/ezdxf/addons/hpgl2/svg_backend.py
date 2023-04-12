#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Sequence, Iterable
from xml.etree import ElementTree as ET

from .deps import Vec2, Path, BoundingBox2d, AnyVec
from .backend import Backend
from .properties import Properties, RGB, RGB_NONE


class SVGBackend(Backend):
    def __init__(self, bbox: BoundingBox2d) -> None:
        assert bbox.has_data
        size = bbox.size
        sx = str(round(size.x))
        sy = str(round(size.y))

        self.root = ET.Element("svg", xmlns="http://www.w3.org/2000/svg")
        self.root.set("width", str(round(size.x / 40.0)) + "mm")
        self.root.set("height", str(round(size.y / 40.0)) + "mm")
        self.root.set("viewBox", f"0 0 {sx} {sy}")

        self.background = ET.SubElement(self.root, "rect")
        self.background.set("fill", "white")
        self.background.set("x", "0")
        self.background.set("y", "0")
        self.background.set("width", sx)
        self.background.set("height", sy)

        self.polygons = ET.SubElement(self.root, "g")
        self.polygons.set("stroke", "none")
        self.polygons.set("fill", "black")
        self.strokes = ET.SubElement(self.root, "g")
        self.strokes.set("fill", "none")
        self.strokes.set("stroke", "black")
        self.strokes.set("stroke-linecap", "round")
        self.strokes.set("stroke-linejoin", "round")

        self.max_y = bbox.extmax.y  # type: ignore
        self.min_x = bbox.extmin.x  # type: ignore

    def draw_polyline(self, properties: Properties, points: Sequence[Vec2]) -> None:
        if not points:
            return
        points = self.flip_points(points)
        path = ET.SubElement(self.strokes, "path", d=make_path_str(points))
        path.set("stroke-width", str(round(properties.pen_width * 40)))
        s = make_rgb(properties.pen_color)
        if s:
            path.set("stroke", s)

    def draw_outline_polygon_buffer(
        self, properties: Properties, paths: Sequence[Path]
    ) -> None:
        outlines = []
        for p in paths:
            points = self.flip_points(p.flattening(distance=10))
            s = make_path_str(points, close=True)
            if s:
                outlines.append(s)
        polygon = ET.SubElement(self.strokes, "path", d=" ".join(outlines))
        polygon.set("stroke-width", str(round(properties.pen_width * 40)))
        s = make_rgb(properties.pen_color)
        if s:
            polygon.set("stroke", s)

    def draw_filled_polygon_buffer(
        self, properties: Properties, paths: Sequence[Path], fill_method: int
    ) -> None:
        polygons = []
        for p in paths:
            points = self.flip_points(p.flattening(distance=10))
            s = make_path_str(points, close=True)
            if s:
                polygons.append(s)
        polygon = ET.SubElement(self.polygons, "path", d=" ".join(polygons))
        s = make_rgb(properties.pen_color)
        if s:
            polygon.set("fill", s)

    def get_string(self) -> str:
        return ET.tostring(self.root, encoding="unicode")

    def flip_points(self, points: Iterable[AnyVec]) -> Sequence[Vec2]:
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
        return ""
    return f"#{color.r:02x}{color.g:02x}{color.b:02x}"
