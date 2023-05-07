#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Iterable, Any, Iterator
import enum
import dataclasses

from ezdxf.math import AnyVec, BoundingBox2d, Matrix44
from ezdxf.path import Path, Path2d
from ezdxf import npshapes
from ezdxf.tools import take2

from .backend import BackendInterface
from .config import Configuration
from .properties import BackendProperties
from .type_hints import Color


class RecordType(enum.Enum):
    POINTS = enum.auto()
    SOLID_LINES = enum.auto()
    PATH = enum.auto()
    FILLED_PATHS = enum.auto()


@dataclasses.dataclass
class DataRecord:
    type: RecordType
    property_hash: int
    data: Any


class Recorder(BackendInterface):
    def __init__(self) -> None:
        self.config = Configuration.defaults()
        self.background: Color = "#000000"
        self.records: list[DataRecord] = []
        self.properties: dict[int, BackendProperties] = dict()
        self._bbox = BoundingBox2d()

    def bbox(self) -> BoundingBox2d:
        """Returns the bounding box of all recorded shapes as
        :class:`~ezdxf.math.BoundingBox2d`.
        """
        if not self._bbox.has_data:
            self.update_bbox()
        return self._bbox

    def update_bbox(self) -> None:
        points: list[AnyVec] = []
        for record in self.records:
            if record.type == RecordType.FILLED_PATHS:
                for path in record.data[0]:  # only add paths, ignore holes
                    points.extend(path.extents())
            else:
                points.extend(record.data.extents())
        self._bbox = BoundingBox2d(points)

    def configure(self, config: Configuration) -> None:
        self.config = config

    def set_background(self, color: Color) -> None:
        self.background = color

    def store(
        self, type_: RecordType, properties: BackendProperties, data: Any
    ) -> None:
        prop_hash = hash(properties)
        self.records.append(DataRecord(type=type_, property_hash=prop_hash, data=data))
        self.properties[prop_hash] = properties

    def draw_point(self, pos: AnyVec, properties: BackendProperties) -> None:
        self.store(RecordType.POINTS, properties, npshapes.NumpyPoints2d((pos,)))

    def draw_line(
        self, start: AnyVec, end: AnyVec, properties: BackendProperties
    ) -> None:
        self.store(
            RecordType.POINTS, properties, npshapes.NumpyPoints2d((start, end))
        )

    def draw_solid_lines(
        self, lines: Iterable[tuple[AnyVec, AnyVec]], properties: BackendProperties
    ) -> None:
        def flatten() -> Iterator[AnyVec]:
            for s, e in lines:
                yield s
                yield e

        self.store(
            RecordType.SOLID_LINES, properties, npshapes.NumpyPoints2d(flatten())
        )

    def draw_path(self, path: Path | Path2d, properties: BackendProperties) -> None:
        self.store(RecordType.PATH, properties, npshapes.NumpyPath2d(path))

    def draw_filled_polygon(
        self, points: Iterable[AnyVec], properties: BackendProperties
    ) -> None:
        self.store(RecordType.POINTS, properties, npshapes.NumpyPoints2d(points))

    def draw_filled_paths(
        self,
        paths: Iterable[Path | Path2d],
        holes: Iterable[Path | Path2d],
        properties: BackendProperties,
    ) -> None:
        _paths = tuple(npshapes.NumpyPath2d(p) for p in paths)
        _holes = tuple(npshapes.NumpyPath2d(p) for p in holes)
        self.store(RecordType.FILLED_PATHS, properties, (_paths, _holes))

    def transform(self, m: Matrix44) -> None:
        """Transforms the recordings by a transformation matrix `m` of type
        :class:`~ezdxf.math.Matrix44`.
        """
        for record in self.records:
            if record.type == RecordType.FILLED_PATHS:
                for p in record.data[0]:
                    p.transform_inplace(m)
                for p in record.data[1]:
                    p.transform_inplace(m)
            else:
                record.data.transform_inplace(m)

        if self._bbox.has_data:
            # fast, but maybe inaccurate update
            self._bbox = BoundingBox2d(m.fast_2d_transform(self._bbox.rect_vertices()))

    def replay(self, backend: BackendInterface) -> None:
        """Replay the recording on another backend."""
        backend.configure(self.config)
        backend.set_background(self.background)
        props = self.properties
        for record in self.records:
            properties = props[record.property_hash]
            t = record.type
            if t == RecordType.POINTS:
                vertices = record.data.vertices()
                if len(vertices) == 1:
                    backend.draw_point(vertices[0], properties)
                elif len(vertices) == 2:
                    backend.draw_line(vertices[0], vertices[1], properties)
                else:
                    backend.draw_filled_polygon(vertices, properties)
            elif t == RecordType.SOLID_LINES:
                backend.draw_solid_lines(take2(record.data.vertices()), properties)
            elif t == RecordType.PATH:
                backend.draw_path(record.data.to_path2d(), properties)
            elif t == RecordType.FILLED_PATHS:
                paths = [p.to_path2d() for p in record.data[0]]
                holes = [p.to_path2d() for p in record.data[1]]
                backend.draw_filled_paths(paths, holes, properties)
        backend.finalize()

    def enter_entity(self, entity, properties) -> None:
        pass

    def exit_entity(self, entity) -> None:
        pass

    def clear(self) -> None:
        raise NotImplementedError()

    def finalize(self) -> None:
        pass
