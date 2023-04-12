#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Sequence, NamedTuple, Any
import abc
import enum

from .deps import Vec2, Path, Bezier4P, BoundingBox2d
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
    def draw_filled_polygon_buffer(
        self, properties: Properties, paths: Sequence[Path], fill_method: int
    ) -> None:
        # input coordinates are page coordinates
        ...

    @abc.abstractmethod
    def draw_outline_polygon_buffer(
        self, properties: Properties, paths: Sequence[Path]
    ) -> None:
        # input coordinates are page coordinates
        ...

class RecordType(enum.Enum):
    POLYLINE = enum.auto()
    FILLED_POLYGON = enum.auto()
    OUTLINE_POLYGON = enum.auto()

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


    def draw_filled_polygon_buffer(
        self, properties: Properties, paths: Sequence[Path], fill_method: int
    ) -> None:
        self.store(RecordType.FILLED_POLYGON, properties, tuple(paths), fill_method)

    def draw_outline_polygon_buffer(
        self, properties: Properties, paths: Sequence[Path]
    ) -> None:
        self.store(RecordType.OUTLINE_POLYGON, properties, tuple(paths))

    def store(self, record_type: RecordType, properties: Properties, *args) -> None:
        prop_hash = properties.hash()
        if prop_hash not in self.properties:
            self.properties[prop_hash] = properties.copy()
        self.records.append(DataRecord(record_type, prop_hash, args))

    def replay(self, backend: Backend) -> None:
        properties = Properties()
        draw = {
            RecordType.POLYLINE: backend.draw_polyline,
            RecordType.FILLED_POLYGON: backend.draw_filled_polygon_buffer,
            RecordType.OUTLINE_POLYGON: backend.draw_outline_polygon_buffer,
        }
        for record in self.records:
            properties = self.properties.get(record.property_hash, properties)
            draw[record.type](properties, *record.args)  # type: ignore
