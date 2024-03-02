#  Copyright (c) 2024, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Iterable, Sequence, no_type_check, Any

from ezdxf.math import Vec2
from ezdxf.path import Command
from ezdxf.npshapes import orient_paths

from .type_hints import Color
from .backend import BackendInterface, BkPath2d, BkPoints2d, ImageData
from .config import Configuration
from .properties import BackendProperties


__all__ = ["CustomJSONBackend"]

SPECS = """
JSON = [entity, entity, ...]

Linetypes (DASH, DOT, ...) are resolved into solid lines.

entity = {
    "type": point | lines | path | filled-paths | filled-polygon,
    "properties": {
        "color": "#RRGGBBAA",
        "stroke-width": 0.25, # in mm
        "layer": "name"
    },
    "geometry": depends on "type"
}

A single point:
point = {
    "type": "point",
    "properties": {...},
    "geometry": [x, y]
}

Multiple lines with common properties:
lines = {
    "type": "lines",
    "properties": {...},
    "geometry": [
        [x0, y0, x1, y1],  # 1. line
        [x0, y0, x1, y1],  # 2. line
        ....
    ]
}
Lines can contain points where x0 == x1 and y0 == y1!

A single linear path without filling:
path = {
    "type": "path",
    "properties": {...},
    "geometry": [path-command, ...]
}

SVG-like path structure:
- The first path-command is always an absolute move to "M"
- The "M" command does not appear inside a path, each path is a continuouse geometry (no 
  multi-paths).

path-command = 
    ["M", x, y] = absolute move to
    ["L", x, y] = absolute line to
    ["Q", x0, y0, x1, y1] = absolute quadratice Bezier curve to
    - (x0, y0) = control point
    - (x1, y1) = end point
    ["C", x0, y0, x1, y1, x2, y2] = absolute cubic Bezier curve to
    - (x0, y0) = control point 1
    - (x1, y1) = control point 2
    - (x2, y2) = end point

Multiple filled paths:

Outer paths and holes are mixed and NOT oriented (clockwise or counter-clockwise) by 
default - PyQt and SVG have no problem with that structure but matplotlib requires 
oriented paths.  When oriented paths are required the CustomJSONBackend can orient the 
paths on demand.

The paths are NOT explicit closed, so first vertex == last vertex is not guaranteed.

filled-paths = {
    "type": "filled-paths",
    "properties": {...},
    "geometry": [
        [path-command, ...],  # 1. path
        [path-command, ...],  # 2. path  
        ...
    ]
}

A single filled polygon:
A polygon is NOT explicit closed, so first vertex == last vertex is not guaranteed.
filled-polygon = {
    "type": "filled-polygon",
    "properties": {...},
    "geometry": [
        [x0, y0],
        [x1, y1],
        [x2, y2],
        ...
    ]
}

"""
MOVE_TO_ABS = "M"
LINE_TO_ABS = "L"
QUAD_TO_ABS = "Q"
CUBIC_TO_ABS = "C"


class CustomJSONBackend(BackendInterface):
    """Creates a custom JSON encoded output with a non-standard JSON scheme."""

    def __init__(self, orient_paths=False) -> None:
        self._entities: list[Any] = []
        self.orient_paths = orient_paths

    def get_json_data(self) -> list[Any]:
        return self._entities

    def add_entity(
        self, entity_type: str, geometry: Sequence[Any], properties: BackendProperties
    ):
        if not geometry:
            return
        self._entities.append(
            {
                "type": entity_type,
                "properties": make_properties_dict(properties),
                "geometry": geometry,
            }
        )

    def draw_point(self, pos: Vec2, properties: BackendProperties) -> None:
        self.add_entity("point", [pos.x, pos.y], properties)

    def draw_line(self, start: Vec2, end: Vec2, properties: BackendProperties) -> None:
        self.add_entity("lines", [[start.x, start.y, end.x, end.y]], properties)

    def draw_solid_lines(
        self, lines: Iterable[tuple[Vec2, Vec2]], properties: BackendProperties
    ) -> None:
        lines = list(lines)
        if len(lines) == 0:
            return
        lines = [(s.x, s.y, e.x, e.y) for s, e in lines]
        self.add_entity("lines", lines, properties)

    def draw_path(self, path: BkPath2d, properties: BackendProperties) -> None:
        self.add_entity("path", make_json_path(path), properties)

    def draw_filled_paths(
        self, paths: Iterable[BkPath2d], properties: BackendProperties
    ) -> None:
        paths = list(paths)
        if len(paths) == 0:
            return
        if self.orient_paths:
            paths = orient_paths(paths)
        json_paths: list[Any] = []
        for path in paths:
            if len(path):
                json_paths.append(make_json_path(path))
        if json_paths:
            self.add_entity("filled-paths", json_paths, properties)

    def draw_filled_polygon(
        self, points: BkPoints2d, properties: BackendProperties
    ) -> None:
        self.add_entity(
            "filled-polygon", [[v.x, v.y] for v in points.vertices()], properties
        )

    def draw_image(self, image_data: ImageData, properties: BackendProperties) -> None:
        pass  # not implemented

    def configure(self, config: Configuration) -> None:
        pass

    def set_background(self, color: Color) -> None:
        pass

    def clear(self) -> None:
        pass

    def finalize(self) -> None:
        pass

    def enter_entity(self, entity, properties) -> None:
        pass

    def exit_entity(self, entity) -> None:
        pass


def make_properties_dict(properties: BackendProperties) -> dict[str, Any]:
    return {
        "color": properties.color,
        "stroke-width": properties.lineweight,
        "layer": properties.layer,
    }


@no_type_check
def make_json_path(path: BkPath2d) -> list[Any]:
    if len(path) == 0:
        return []
    end: Vec2 = path.start
    commands: list = [(MOVE_TO_ABS, end.x, end.y)]
    for cmd in path.commands():
        end = cmd.end
        if cmd.type == Command.MOVE_TO:
            commands.append((MOVE_TO_ABS, end.x, end.y))
        elif cmd.type == Command.LINE_TO:
            commands.append((LINE_TO_ABS, end.x, end.y))
        elif cmd.type == Command.CURVE3_TO:
            c1 = cmd.ctrl
            commands.append((QUAD_TO_ABS, c1.x, c1.y, end.x, end.y))
        elif cmd.type == Command.CURVE4_TO:
            c1 = cmd.ctrl1
            c2 = cmd.ctrl2
            commands.append((CUBIC_TO_ABS, c1.x, c1.y, c2.x, c2.y, end.x, end.y))

    return commands
