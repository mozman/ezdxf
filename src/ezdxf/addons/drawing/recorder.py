#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, NamedTuple, Any
import enum
import dataclasses

import numpy as np
from ezdxf.math import AnyVec, BoundingBox2d, Matrix44
from ezdxf.path import Path, Path2d
from ezdxf import npshapes
from ezdxf.tools import take2

from .backend import BackendInterface
from .config import Configuration
from .properties import Properties
from .type_hints import Color


if TYPE_CHECKING:
    from ezdxf.entities import DXFGraphic


class RecordType(enum.Enum):
    POINT = enum.auto()
    LINE = enum.auto()
    SOLID_LINES = enum.auto()
    PATH = enum.auto()
    FILLED_PATHS = enum.auto()
    FILLED_POLYGON = enum.auto()


@dataclasses.dataclass
class DataRecord:
    type: RecordType
    property_hash: int
    data: Any


# Linetype, linetype_pattern and linetype_scale is not relevant, the frontend passes
# only solid lines to the backend.
# is_visible is handled by the frontend
# Fonts are rendered by the frontend into paths or filled polylines.
# Units are handled by the frontend.
# Filling has no meaning to the backend - fill-color is "color", patterns are rendered
# by the frontend as lines


class RecordProperties(NamedTuple):
    color: Color
    lineweight: float
    layer: str


class Recorder(BackendInterface):
    def __init__(self) -> None:
        self.config = Configuration.defaults()
        self.background: Color = "#000000"
        self.records: list[DataRecord] = []
        self.properties: dict[int, RecordProperties] = dict()
        self.bbox = BoundingBox2d()

    def configure(self, config: Configuration) -> None:
        self.config = config

    def set_background(self, color: Color) -> None:
        self.background = color

    def store(self, type_: RecordType, properties: Properties, data: Any) -> None:
        rec_props = RecordProperties(
            color=properties.color,
            lineweight=properties.lineweight,
            layer=properties.layer,
        )
        prop_hash = hash(rec_props)
        self.records.append(DataRecord(type=type_, property_hash=prop_hash, data=data))
        if prop_hash not in self.properties:
            self.properties[prop_hash] = rec_props

    def draw_point(self, pos: AnyVec, properties: Properties) -> None:
        self.bbox.extend((pos,))
        self.store(RecordType.POINT, properties, npshapes.NumpyPolyline((pos,)))

    def draw_line(self, start: AnyVec, end: AnyVec, properties: Properties) -> None:
        line = npshapes.NumpyPolyline((start, end))
        self.bbox.extend(line.bbox())
        self.store(RecordType.LINE, properties, line)

    def draw_solid_lines(
        self, lines: Iterable[tuple[AnyVec, AnyVec]], properties: Properties
    ) -> None:
        points: list[AnyVec] = []
        for line in lines:
            points.extend(line)
        pline = npshapes.NumpyPolyline(points)
        self.bbox.extend(pline.bbox())
        self.store(RecordType.SOLID_LINES, properties, pline)

    def draw_path(self, path: Path | Path2d, properties: Properties) -> None:
        npath = npshapes.NumpyPath(path)
        self.bbox.extend(npath.bbox())
        self.store(RecordType.PATH, properties, npath)

    def draw_filled_paths(
        self,
        paths: Iterable[Path | Path2d],
        holes: Iterable[Path | Path2d],
        properties: Properties,
    ) -> None:
        _paths = tuple(npshapes.NumpyPath(p) for p in paths)
        for p in _paths:
            self.bbox.extend(p.bbox())
        _holes = tuple(npshapes.NumpyPath(p) for p in holes)
        self.store(RecordType.FILLED_PATHS, properties, (_paths, _holes))

    def draw_filled_polygon(
        self, points: Iterable[AnyVec], properties: Properties
    ) -> None:
        polygon = npshapes.NumpyPolyline(points)
        self.bbox.extend(polygon.bbox())
        self.store(RecordType.FILLED_POLYGON, properties, polygon)

    def transform(self, m: Matrix44) -> None:
        """Transforms the recordings by a transformation matrix `m` of type
        :class:`~ezdxf.math.Matrix44`.
        """
        np_mat = np.array(m.get_2d_transformation(), dtype=np.double)
        np_mat.shape = (3, 3)
        for record in self.records:
            if record.type == RecordType.FILLED_PATHS:
                for p in record.data[0]:
                    p.transform_inplace(np_mat)
                for p in record.data[1]:
                    p.transform_inplace(np_mat)
            else:
                record.data.transform_inplace(np_mat)

        if self.bbox.has_data:
            self.bbox = BoundingBox2d(m.fast_2d_transform(self.bbox.rect_vertices()))

    def replay(self, backend: BackendInterface) -> None:
        """Replay the recording on another backend."""
        backend.configure(self.config)
        backend.set_background(self.background)

        properties = Properties()
        props = self.properties
        for record in self.records:
            properties.color, properties.lineweight, properties.layer = props[
                record.property_hash
            ]
            t = record.type
            if t == RecordType.POINT:
                point = record.data.vertices()[0]
                backend.draw_point(point, properties)
            elif t == RecordType.LINE:
                s, e = record.data.vertices()
                backend.draw_line(s, e, properties)
            elif t == RecordType.SOLID_LINES:
                backend.draw_solid_lines(take2(record.data.vertices()), properties)
            elif t == RecordType.PATH:
                backend.draw_path(record.data.to_path2d(), properties)
            elif t == RecordType.FILLED_POLYGON:
                backend.draw_filled_polygon(record.data.vertices(), properties)
            elif t == RecordType.FILLED_PATHS:
                paths = [p.to_path2d() for p in record.data[0]]
                holes = [p.to_path2d() for p in record.data[1]]
                backend.draw_filled_paths(paths, holes, properties)
        backend.finalize()

    def enter_entity(self, entity: DXFGraphic, properties: Properties) -> None:
        pass

    def exit_entity(self, entity: DXFGraphic) -> None:
        pass

    def clear(self) -> None:
        raise NotImplementedError()

    def finalize(self) -> None:
        pass
