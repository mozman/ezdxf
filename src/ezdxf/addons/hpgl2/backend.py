#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Sequence, NamedTuple, Any
import abc
import enum
import math
import numpy as np
from .deps import (
    Vec2,
    Path,
    luminance,
    Matrix44,
    BoundingBox2d,
)
from .properties import Properties, Pen
from ezdxf.npshapes import NumpyPath, NumpyPolyline

# Page coordinates are always plot units:
# 1 plot unit (plu) = 0.025mm
# 40 plu = 1mm
# 1016 plu = 1 inch
# 3.39 plu = 1 dot @300 dpi
# positive x-axis is horizontal from left to right
# positive y-axis is vertical from bottom to top


class Backend(abc.ABC):
    """Abstract base class for implementing a low level output backends.

    All input coordinates are page coordinates:

        - 1 plot unit (plu) = 0.025mm
        - 40 plu = 1 mm
        - 1016 plu = 1 inch

    """

    @abc.abstractmethod
    def draw_polyline(self, properties: Properties, points: Sequence[Vec2]) -> None:
        """Draws a polyline from a sequence `points`. The input coordinates are page
        coordinates in plot units. The `points` sequence can contain 0 or more
        points!

        Args:
            properties: display :class:`Properties` for the polyline
            points: sequence of :class:`ezdxf.math.Vec2` instances

        """
        ...

    @abc.abstractmethod
    def draw_filled_polygon(
        self, properties: Properties, paths: Sequence[Path]
    ) -> None:
        """Draws a filled polygon from the sequence of `paths`. The input coordinates
        are page coordinates in plot units. The `paths` sequence can contain 0 or more
        single :class:`~ezdxf.path.Path` instances.

        Args:
            properties: display :class:`Properties` for the filled polygon
            paths: sequence of single :class:`ezdxf.path.Path` instances

        """
        ...


class RecordType(enum.Enum):
    POLYLINE = enum.auto()
    FILLED_POLYGON = enum.auto()


class DataRecord(NamedTuple):
    type: RecordType
    property_hash: int
    data: Any


class Recorder(Backend):
    """The :class:`Recorder` class records the output of the :class:`Plotter` and
    can replay this recording on another backend. The class can modify the recorded
    output.
    """

    def __init__(self) -> None:
        self.records: list[DataRecord] = []
        self.properties: dict[int, Properties] = {}
        self._bbox = BoundingBox2d()
        self.pens: Sequence[Pen] = []

    def bbox(self) -> BoundingBox2d:
        """Returns the bounding box of all recorded polylines and polygons as
        :class:`~ezdxf.math.BoundingBox2d`.
        """
        if not self._bbox.has_data:
            self.update_bbox()
        return self._bbox

    def update_bbox(self):
        for record in self.records:
            if record.type == RecordType.POLYLINE:
                self._bbox.extend(record.data.bbox())
            else:
                for path in record.data:
                    self._bbox.extend(path.bbox())

    def draw_polyline(self, properties: Properties, points: Sequence[Vec2]) -> None:
        self.store(RecordType.POLYLINE, properties, NumpyPolyline(points))

    def draw_filled_polygon(
        self, properties: Properties, paths: Sequence[Path]
    ) -> None:
        data = tuple(NumpyPath(p) for p in paths)
        self.store(RecordType.FILLED_POLYGON, properties, data)

    def store(self, record_type: RecordType, properties: Properties, args) -> None:
        prop_hash = properties.hash()
        if prop_hash not in self.properties:
            self.properties[prop_hash] = properties.copy()
        self.records.append(DataRecord(record_type, prop_hash, args))
        if len(self.pens) != len(properties.pen_table):
            self.pens = list(properties.pen_table.values())

    def replay(self, backend: Backend) -> None:
        """Replay the recording on another backend."""
        current_props = Properties()
        props = self.properties
        for record in self.records:
            current_props = props.get(record.property_hash, current_props)
            if record.type == RecordType.POLYLINE:
                backend.draw_polyline(current_props, record.data.vertices())
            else:
                paths = [p.to_path2d() for p in record.data]
                backend.draw_filled_polygon(current_props, paths)

    def transform(self, m: Matrix44) -> None:
        """Transforms the recordings by a transformation matrix `m` of type
        :class:`~ezdxf.math.Matrix44`.
        """
        np_mat = np.array(m.get_2d_transformation(), dtype=np.double)
        np_mat.shape = (3, 3)
        for record in self.records:
            if record.type == RecordType.POLYLINE:
                record.data.transform_inplace(np_mat)
            else:
                for path in record.data:
                    path.transform_inplace(np_mat)

        if self._bbox.has_data:
            self._bbox = BoundingBox2d(m.fast_2d_transform(self._bbox.rect_vertices()))

    def sort_filled_polygons(self) -> None:
        """Sort filled polygons by descending luminance (from light to dark).

        This also changes the plot order in the way that all filled polygons are plotted
        before the polylines.
        """
        polygons = []
        polylines = []
        current = Properties()
        props = self.properties
        for record in self.records:
            if record.type == RecordType.FILLED_POLYGON:
                current = props.get(record.property_hash, current)
                key = luminance(current.resolve_fill_color())
                polygons.append((key, record))
            else:
                polylines.append(record)

        polygons.sort(key=lambda r: r[0], reverse=True)
        records = [sort_rec[1] for sort_rec in polygons]
        records.extend(polylines)
        self.records = records


def placement_matrix(
    bbox: BoundingBox2d, sx: float = 1.0, sy: float = 1.0, rotation: float = 0.0
) -> Matrix44:
    """Returns a matrix to place the bbox in the first quadrant of the coordinate
    system (+x, +y).
    """
    if abs(sx) < 1e-9:
        sx = 1.0
    if abs(sy) < 1e-9:
        sy = 1.0
    m = Matrix44.scale(sx, sy, 1.0)
    if rotation:
        m @= Matrix44.z_rotate(math.radians(rotation))
    corners = m.transform_vertices(bbox.rect_vertices())
    tx, ty = BoundingBox2d(corners).extmin  # type: ignore
    return m @ Matrix44.translate(-tx, -ty, 0)
