#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Sequence, NamedTuple, Any
import abc
import enum
import math

from .deps import Vec2, Path, luminance, Matrix44, transform_paths, BoundingBox2d
from .properties import Properties

# Page coordinates are always plot units:
# 1 plot unit (plu) = 0.025mm
# 40 plu = 1mm
# 1016 plu = 1 inch
# 3.39 plu = 1 dot @300 dpi
# positive x-axis is horizontal from left to right
# positive y-axis is vertical from bottom to top


class Backend(abc.ABC):
    @abc.abstractmethod
    def draw_polyline(self, properties: Properties, points: Sequence[Vec2]) -> None:
        # input coordinates are page coordinates
        # argument <points> can be zero, one, two or more points.
        ...

    @abc.abstractmethod
    def draw_filled_polygon(
        self, properties: Properties, paths: Sequence[Path]
    ) -> None:
        # input coordinates are page coordinates
        ...


class RecordType(enum.Enum):
    POLYLINE = enum.auto()
    FILLED_POLYGON = enum.auto()


class DataRecord(NamedTuple):
    type: RecordType
    property_hash: int
    args: Any


class Recorder(Backend):
    def __init__(self) -> None:
        self.records: list[DataRecord] = []
        self.properties: dict[int, Properties] = {}

    def draw_polyline(self, properties: Properties, points: Sequence[Vec2]) -> None:
        self.store(RecordType.POLYLINE, properties, tuple(points))

    def draw_filled_polygon(
        self, properties: Properties, paths: Sequence[Path]
    ) -> None:
        self.store(RecordType.FILLED_POLYGON, properties, tuple(paths))

    def store(self, record_type: RecordType, properties: Properties, args) -> None:
        prop_hash = properties.hash()
        if prop_hash not in self.properties:
            self.properties[prop_hash] = properties.copy()
        self.records.append(DataRecord(record_type, prop_hash, args))

    def replay(self, backend: Backend) -> None:
        current_props = Properties()
        props = self.properties
        draw = {
            RecordType.POLYLINE: backend.draw_polyline,
            RecordType.FILLED_POLYGON: backend.draw_filled_polygon,
        }
        for record in self.records:
            current_props = props.get(record.property_hash, current_props)
            draw[record.type](current_props, record.args)  # type: ignore

    def transform(self, m: Matrix44) -> None:
        records: list[DataRecord] = []
        for record in self.records:
            if record.type == RecordType.POLYLINE:
                vertices = Vec2.list(m.transform_vertices(record.args))
                records.append(DataRecord(record.type, record.property_hash, vertices))
            else:
                paths = transform_paths(record.args, m)
                records.append(DataRecord(record.type, record.property_hash, paths))
        self.records = records

    def sort_filled_polygons(self, reverse=True) -> None:
        polygons = []
        polylines = []
        current = Properties()
        props = self.properties
        for record in self.records:
            if record.type == RecordType.FILLED_POLYGON:
                current = props.get(record.property_hash, current)
                key = luminance(current.pen_color)
                polygons.append((key, record))
            else:
                polylines.append(record)

        polygons.sort(key=lambda r: r[0], reverse=reverse)
        records = [sort_rec[1] for sort_rec in polygons]
        records.extend(polylines)
        self.records = records


def placement_matrix(
    bbox: BoundingBox2d, sx: float = 1.0, sy: float = 1.0, rotation: float = 0.0
) -> Matrix44:
    """Returns a matrix to place the bbox in the first quadrant of the coordinate
    system (+x, +y).
    """
    m = Matrix44.scale(sx, sy, 1.0)
    if rotation:
        m @= Matrix44.z_rotate(math.radians(rotation))
    corners = m.transform_vertices(bbox.rect_vertices())
    tx, ty = BoundingBox2d(corners).extmin  # type: ignore
    return m @ Matrix44.translate(-tx, -ty, 0)
