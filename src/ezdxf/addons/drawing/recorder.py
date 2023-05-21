#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Iterable, Any, Iterator, Callable, Optional, NamedTuple
from typing_extensions import Self, TypeAlias
import copy
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
    handle: str  # top-level entity handle
    data: Any


class Recorder(BackendInterface):
    """Records the output of the Frontend class."""

    def __init__(self) -> None:
        self.config = Configuration()
        self.background: Color = "#000000"
        self.records: list[DataRecord] = []
        self.properties: dict[int, BackendProperties] = dict()

    def player(self) -> Player:
        """Returns a :class:`Player` instance with the original recordings! Make a copy
        of this player to protect the original recordings from being modified::

            safe_player = recorder.player().copy()

        """
        player = Player()
        player.config = self.config
        player.background = self.background
        player.records = self.records
        player.properties = self.properties
        player.has_shared_recordings = True
        return player

    def configure(self, config: Configuration) -> None:
        self.config = config

    def set_background(self, color: Color) -> None:
        self.background = color

    def store(
        self, type_: RecordType, properties: BackendProperties, data: Any
    ) -> None:
        # exclude top-level entity handle to reduce the variance:
        # color, lineweight, layer, pen
        prop_hash = hash(properties[:4])
        self.records.append(
            DataRecord(
                type=type_, property_hash=prop_hash, handle=properties.handle, data=data
            )
        )
        self.properties[prop_hash] = properties

    def draw_point(self, pos: AnyVec, properties: BackendProperties) -> None:
        self.store(RecordType.POINTS, properties, npshapes.NumpyPoints2d((pos,)))

    def draw_line(
        self, start: AnyVec, end: AnyVec, properties: BackendProperties
    ) -> None:
        self.store(RecordType.POINTS, properties, npshapes.NumpyPoints2d((start, end)))

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

    def enter_entity(self, entity, properties) -> None:
        pass

    def exit_entity(self, entity) -> None:
        pass

    def clear(self) -> None:
        raise NotImplementedError()

    def finalize(self) -> None:
        pass


class Override(NamedTuple):
    """Represents the override state for a data record.

    Attributes:
        properties: original or modified :class:`BackendProperties`
        is_visible: override visibility e.g. switch layers on/off

    """

    properties: BackendProperties
    is_visible: bool = True


OverrideFunc: TypeAlias = Callable[[BackendProperties], Override]


class Player:
    """Plays the recordings of the :class:`Recorder` backend on another backend."""

    def __init__(self) -> None:
        self.config = Configuration()
        self.background: Color = "#000000"
        self.records: list[DataRecord] = []
        self.properties: dict[int, BackendProperties] = dict()
        self._bbox = BoundingBox2d()
        self.has_shared_recordings: bool = False

    def __copy__(self) -> Self:
        """Returns a copy of the player with non-shared recordings."""
        player = self.__class__()
        # config is a frozen dataclass:
        player.config = self.config
        player.background = self.background
        # recordings are mutable - transformed inplace:
        player.records = copy.deepcopy(self.records)
        # the properties dict may grow, but entries will never be removed:
        player.properties = self.properties
        player.has_shared_recordings = False
        return player

    copy = __copy__

    def replay(
        self, backend: BackendInterface, override: Optional[OverrideFunc] = None
    ) -> None:
        """Replay the recording on another backend that implements the
        :class:`BackendInterface`. The optional `override` function can be used to
        override the properties and state of data records, it gets the :class:`BackendProperties`
        as input and must return an :class:`Override` instance.
        """

        backend.configure(self.config)
        backend.set_background(self.background)
        props = self.properties
        for record in self.records:
            properties = BackendProperties(
                *props[record.property_hash][:4], record.handle
            )
            if override:
                state = override(properties)
                if not state.is_visible:
                    continue
                properties = state.properties
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

    def transform(self, m: Matrix44) -> None:
        """Transforms the recordings inplace by a transformation matrix `m` of type
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
            # works for 90-, 180- and 270-degree rotation
            self._bbox = BoundingBox2d(m.fast_2d_transform(self._bbox.rect_vertices()))

    def bbox(self) -> BoundingBox2d:
        """Returns the bounding box of all records as :class:`~ezdxf.math.BoundingBox2d`."""
        if not self._bbox.has_data:
            self.update_bbox()
        return self._bbox

    def update_bbox(self) -> None:
        points: list[AnyVec] = []
        for record in self.records:
            try:
                if record.type == RecordType.FILLED_PATHS:
                    for path in record.data[0]:  # only add paths, ignore holes
                        points.extend(path.extents())
                else:
                    points.extend(record.data.extents())
            except npshapes.EmptyShapeError:
                pass
        self._bbox = BoundingBox2d(points)
