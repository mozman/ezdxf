#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import (
    Iterable,
    Any,
    Iterator,
    Sequence,
    Callable,
    Optional,
    NamedTuple,
)
from typing_extensions import Self, TypeAlias
import copy
import enum
import dataclasses

from ezdxf.math import BoundingBox2d, Matrix44, Vec2, UVec
from ezdxf.npshapes import NumpyPath2d, NumpyPoints2d, EmptyShapeError
from ezdxf.tools import take2

from .backend import BackendInterface
from .config import Configuration
from .properties import BackendProperties
from .type_hints import Color


class RecordType(enum.Enum):
    """Enum, determines the data record type.

    Attributes:
        POINTS:
        SOLID_LINES:
        PATH:
        FILLED_PATHS:
    """

    POINTS = enum.auto()  # n=1 point; n=2 line; n>2 filled polygon
    SOLID_LINES = enum.auto()
    PATH = enum.auto()
    FILLED_PATHS = enum.auto()


@dataclasses.dataclass
class DataRecord:
    type: RecordType
    property_hash: int
    handle: str  # top-level entity handle
    data: Any

    def bbox(self) -> BoundingBox2d:
        bbox = BoundingBox2d()
        try:
            if self.type == RecordType.FILLED_PATHS:
                for path in self.data:
                    bbox.extend(path.extents())
            else:
                bbox.extend(self.data.extents())
        except EmptyShapeError:
            pass
        return bbox


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

    def draw_point(self, pos: Vec2, properties: BackendProperties) -> None:
        self.store(RecordType.POINTS, properties, NumpyPoints2d((pos,)))

    def draw_line(self, start: Vec2, end: Vec2, properties: BackendProperties) -> None:
        self.store(RecordType.POINTS, properties, NumpyPoints2d((start, end)))

    def draw_solid_lines(
        self, lines: Iterable[tuple[Vec2, Vec2]], properties: BackendProperties
    ) -> None:
        def flatten() -> Iterator[Vec2]:
            for s, e in lines:
                yield s
                yield e

        self.store(RecordType.SOLID_LINES, properties, NumpyPoints2d(flatten()))

    def draw_path(self, path: NumpyPath2d, properties: BackendProperties) -> None:
        assert isinstance(path, NumpyPath2d)
        self.store(RecordType.PATH, properties, path)

    def draw_filled_polygon(
        self, points: NumpyPoints2d, properties: BackendProperties
    ) -> None:
        assert isinstance(points, NumpyPoints2d)
        self.store(RecordType.POINTS, properties, points)

    def draw_filled_paths(
        self, paths: Iterable[NumpyPath2d], properties: BackendProperties
    ) -> None:
        paths = tuple(paths)
        if len(paths) == 0:
            return

        assert isinstance(paths[0], NumpyPath2d)
        self.store(RecordType.FILLED_PATHS, properties, paths)

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

    def recordings(self) -> Iterator[tuple[RecordType, BackendProperties, Any]]:
        """Yields all recordings as `(RecordType, BackendProperties, Data)` tuples.

        The content of the `Data` field is determined by the enum :class:`RecordType`:

        - :attr:`RecordType.POINTS` returns a :class:`NumpyPoints2d` instance,
          len() == 1 is a point, len() == 2 is a line, len() > 2 is a filled polygon
        - :attr:`RecordType.SOLID_LINES` returns a :class:`NumpyPoints2d` instance
          where each pair (n, n+1) represents the start- and end point of a line
        - :attr:`RecordType.PATH`: returns a :class:`NumpyPath2d` instance that
          represents a linear 2D path
        - :attr:`RecordType.FILLED_PATHS` returns a tuple (exterior_paths, holes),
          where exterior_paths and holes are tuples of :class:`NumpyPath2d`.

        """
        props = self.properties
        for record in self.records:
            properties = BackendProperties(
                *props[record.property_hash][:4], record.handle
            )
            yield record.type, properties, record.data

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
        for record_type, properties, data in self.recordings():
            if override:
                state = override(properties)
                if not state.is_visible:
                    continue
                properties = state.properties
            if record_type == RecordType.POINTS:
                if len(data) == 0:
                    continue
                if len(data) > 2:
                    backend.draw_filled_polygon(data, properties)
                    continue
                vertices = data.vertices()
                if len(vertices) == 1:
                    backend.draw_point(vertices[0], properties)
                else:
                    backend.draw_line(vertices[0], vertices[1], properties)
            elif record_type == RecordType.SOLID_LINES:
                backend.draw_solid_lines(take2(data.vertices()), properties)
            elif record_type == RecordType.PATH:
                backend.draw_path(data, properties)
            elif record_type == RecordType.FILLED_PATHS:
                backend.draw_filled_paths(data, properties)
        backend.finalize()

    def transform(self, m: Matrix44) -> None:
        """Transforms the recordings inplace by a transformation matrix `m` of type
        :class:`~ezdxf.math.Matrix44`.
        """
        for record in self.records:
            if record.type == RecordType.FILLED_PATHS:
                for p in record.data:
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
        bbox = BoundingBox2d()
        for record in self.records:
            bbox.extend(record.bbox())
        self._bbox = bbox

    def crop_rect(self, p1: UVec, p2: UVec, distance: float) -> None:
        """Crop recorded shapes inplace by a rectangle defined by two points.

        The argument `distance` defines the approximation precision for paths which have
        to be approximated as polylines for cropping but only paths which are really get
        cropped are approximated, paths that are fully inside the crop box will not be
        approximated.

        Args:
            p1: first corner of the clipping rectangle
            p2: second corner of the clipping rectangle
            distance: maximum distance from the center of the curve to the
                center of the line segment between two approximation points to
                determine if a segment should be subdivided.

        """
        crop_rect = BoundingBox2d([Vec2(p1), Vec2(p2)])
        self.records = crop_records_rect(self.records, crop_rect, distance)
        self._bbox = BoundingBox2d()  # determine new bounding box on demand


def crop_records_rect(
    records: list[DataRecord], crop_rect: BoundingBox2d, distance: float
) -> list[DataRecord]:
    """Crop recorded shapes inplace by a rectangle."""
    from .clipper import ClippingRect

    def sort_paths(np_paths: Sequence[NumpyPath2d]):
        _inside: list[NumpyPath2d] = []
        _crop: list[NumpyPath2d] = []

        for np_path in np_paths:
            bbox = BoundingBox2d(np_path.extents())
            if not crop_rect.has_intersection(bbox):
                # path is complete outside the cropping rectangle
                pass
            elif crop_rect.inside(bbox.extmin) and crop_rect.inside(bbox.extmax):
                # path is complete inside the cropping rectangle
                _inside.append(np_path)
            else:
                _crop.append(np_path)

        return _crop, _inside

    def crop_paths(
        np_paths: Sequence[NumpyPath2d],
    ) -> list[NumpyPath2d]:
        return list(clipper.clip_filled_paths(np_paths, distance))

    # an undefined crop box crops nothing:
    if not crop_rect.has_data:
        return records
    cropped_records: list[DataRecord] = []
    size = crop_rect.size
    # a crop box size of zero in any dimension crops everything:
    if size.x < 1e-12 or size.y < 1e-12:
        return cropped_records

    clipper = ClippingRect()
    clipper.push(NumpyPath2d.from_vertices(crop_rect.rect_vertices()), None)
    for record in records:
        record_box = record.bbox()
        if not crop_rect.has_intersection(record_box):
            # record is complete outside the cropping rectangle
            continue
        if crop_rect.inside(record_box.extmin) and crop_rect.inside(record_box.extmax):
            # record is complete inside the cropping rectangle
            cropped_records.append(record)
            continue

        if record.type == RecordType.FILLED_PATHS:
            paths_to_crop, inside = sort_paths(record.data)
            cropped_paths = crop_paths(paths_to_crop) + inside
            if cropped_paths:
                record.data = tuple(cropped_paths)
                cropped_records.append(record)
        elif record.type == RecordType.PATH:
            # could be split into multiple parts
            for p in clipper.clip_paths([record.data], distance):  # type: ignore
                cropped_records.append(
                    DataRecord(
                        record.type,
                        record.property_hash,
                        record.handle,
                        p,
                    )
                )
        elif record.type == RecordType.POINTS:
            count = len(record.data)
            if count == 1:
                pass
            elif count == 2:
                s, e = record.data.vertices()
                record.data = NumpyPoints2d(clipper.clip_line(s, e))
            else:  # filled polygon
                record.data = clipper.clip_polygon(record.data)
            cropped_records.append(record)
        elif record.type == RecordType.SOLID_LINES:
            points: list[Vec2] = []  # type: ignore
            for s, e in take2(record.data.vertices()):
                points.append(clipper.clip_line(s, e))  # type: ignore
            record.data = NumpyPoints2d(points)
            cropped_records.append(record)
        else:
            raise ValueError("invalid record type")
    return cropped_records
