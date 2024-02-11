#  Copyright (c) 2024, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import (
    Optional,
    Iterable,
    Iterator,
    Sequence,
    NamedTuple,
    Callable,
    TYPE_CHECKING,
)
import abc

from ezdxf.math import (
    Matrix44,
    Vec2,
    BoundingBox2d,
    UVec,
    is_convex_polygon_2d,
    is_axes_aligned_rectangle_2d,
)
from ezdxf.npshapes import NumpyPath2d, NumpyPoints2d

if TYPE_CHECKING:
    from ezdxf.math.clipping import Clipping

__all__ = [
    "ClippingShape",
    "ClippingPortal",
    "ClippingRect",
    "ConvexClippingPolygon",
    "MultiClip",
    "find_best_clipping_shape",
    "make_inverted_clipping_shape",
]


class ClippingShape(abc.ABC):
    """The ClippingShape defines a single clipping path and executes the clipping on
    basic geometries:

    - point: a single point
    - line: a line between two vertices
    - polyline: open polyline with one or more straight line segments
    - polygon: closed shape with straight line as edges
    - path: open shape with straight lines and Bezier-curves as segments
    - filled-path: closed shape with straight lines and Bezier-curves as edges

    Difference between open and closed shapes:

        - an open shape is treated as a linear shape without a filling
        - clipping an open shape returns one or more open shapes
        - a closed shape is treated as a filled shape, where the first vertex is
          coincident to the last vertex.
        - clipping a closed shape returns one or more closed shapes

    Notes:

        An arbitrary clipping polygon can split any basic geometry (except point) into
        multiple parts.

        All current implemented clipping algorithms flatten Bezier-curves into polylines.

    """

    @abc.abstractmethod
    def bbox(self) -> BoundingBox2d: ...

    @abc.abstractmethod
    def clip_point(self, point: Vec2) -> Optional[Vec2]: ...

    @abc.abstractmethod
    def clip_line(self, start: Vec2, end: Vec2) -> Sequence[tuple[Vec2, Vec2]]: ...

    @abc.abstractmethod
    def clip_polyline(self, points: NumpyPoints2d) -> Sequence[NumpyPoints2d]: ...

    @abc.abstractmethod
    def clip_polygon(self, points: NumpyPoints2d) -> Sequence[NumpyPoints2d]: ...

    @abc.abstractmethod
    def clip_paths(
        self, paths: Iterable[NumpyPath2d], max_sagitta: float
    ) -> Iterator[NumpyPath2d]: ...

    @abc.abstractmethod
    def clip_filled_paths(
        self, paths: Iterable[NumpyPath2d], max_sagitta: float
    ) -> Iterator[NumpyPath2d]: ...


class ClippingStage(NamedTuple):
    portal: ClippingShape
    transform: Matrix44 | None


class ClippingPortal:
    """The ClippingPortal manages a clipping path stack."""

    def __init__(self) -> None:
        self._stages: list[ClippingStage] = []

    @property
    def is_active(self) -> bool:
        return bool(self._stages)

    def push(self, portal: ClippingShape, transform: Matrix44 | None) -> None:
        self._stages.append(ClippingStage(portal, transform))

    def pop(self) -> None:
        if self._stages:
            self._stages.pop()

    def foreach_stage(self, command: Callable[[ClippingStage], bool]) -> None:
        for stage in self._stages[::-1]:
            if not command(stage):
                return

    def clip_point(self, point: Vec2) -> Optional[Vec2]:
        result: Vec2 | None = point

        def do(stage: ClippingStage) -> bool:
            nonlocal result
            assert result is not None
            if stage.transform:
                result = Vec2(stage.transform.transform(result))
            result = stage.portal.clip_point(result)
            return result is not None

        self.foreach_stage(do)
        return result

    def clip_line(self, start: Vec2, end: Vec2) -> list[tuple[Vec2, Vec2]]:
        def do(stage: ClippingStage) -> bool:
            lines = list(result)
            result.clear()
            for s, e in lines:
                if stage.transform:
                    s, e = stage.transform.fast_2d_transform((s, e))
                result.extend(stage.portal.clip_line(s, e))
            return bool(result)

        result = [(start, end)]
        self.foreach_stage(do)
        return result

    def clip_polyline(self, points: NumpyPoints2d) -> list[NumpyPoints2d]:
        def do(stage: ClippingStage) -> bool:
            polylines = list(result)
            result.clear()
            for polyline in polylines:
                if stage.transform:
                    polyline.transform_inplace(stage.transform)
                result.extend(stage.portal.clip_polyline(polyline))
            return bool(result)

        result = [points]
        self.foreach_stage(do)
        return result

    def clip_polygon(self, points: NumpyPoints2d) -> list[NumpyPoints2d]:
        def do(stage: ClippingStage) -> bool:
            polygons = list(result)
            result.clear()
            for polygon in polygons:
                if stage.transform:
                    polygon.transform_inplace(stage.transform)
                result.extend(stage.portal.clip_polygon(polygon))
            return bool(result)

        result = [points]
        self.foreach_stage(do)
        return result

    def clip_paths(
        self, paths: Iterable[NumpyPath2d], max_sagitta: float
    ) -> list[NumpyPath2d]:
        def do(stage: ClippingStage) -> bool:
            paths = list(result)
            result.clear()
            for path in paths:
                if stage.transform:
                    path.transform_inplace(stage.transform)
            result.extend(stage.portal.clip_paths(paths, max_sagitta))
            return bool(result)

        result = list(paths)
        self.foreach_stage(do)
        return result

    def clip_filled_paths(
        self, paths: Iterable[NumpyPath2d], max_sagitta: float
    ) -> list[NumpyPath2d]:
        def do(stage: ClippingStage) -> bool:
            paths = list(result)
            result.clear()
            for path in paths:
                if stage.transform:
                    path.transform_inplace(stage.transform)
            result.extend(stage.portal.clip_filled_paths(paths, max_sagitta))
            return bool(result)

        result = list(paths)
        self.foreach_stage(do)
        return result

    def transform_matrix(self, m: Matrix44) -> Matrix44:
        for _, transform in self._stages[::-1]:
            if transform is not None:
                m @= transform
        return m


class ClippingPolygon(ClippingShape):
    """Represents an arbitrary polygon as clipping shape.  Removes the geometry
    outside the clipping polygon.

    """

    def __init__(self, bbox: BoundingBox2d, clipper: Clipping) -> None:
        if not bbox.has_data:
            raise ValueError("clipping box not detectable")
        self._bbox = bbox
        self.clipper = clipper

    def bbox(self) -> BoundingBox2d:
        return self._bbox

    def clip_point(self, point: Vec2) -> Optional[Vec2]:
        is_inside = self.clipper.is_inside(Vec2(point))
        if not is_inside:
            return None
        return point

    def clip_line(self, start: Vec2, end: Vec2) -> Sequence[tuple[Vec2, Vec2]]:
        return self.clipper.clip_line(start, end)

    def clip_polyline(self, points: NumpyPoints2d) -> Sequence[NumpyPoints2d]:
        clipper = self.clipper
        polyline_bbox = BoundingBox2d(points.extents())
        if not polyline_bbox.has_intersection(self._bbox):
            # polyline is complete outside
            return tuple()
        return [
            NumpyPoints2d(part)
            for part in clipper.clip_polyline(points.vertices())
            if len(part) > 0
        ]

    def clip_polygon(self, points: NumpyPoints2d) -> Sequence[NumpyPoints2d]:
        clipper = self.clipper
        polygon_bbox = BoundingBox2d(points.extents())
        if not polygon_bbox.has_intersection(self._bbox):
            # polygon is complete outside
            return tuple()
        return [
            NumpyPoints2d(part)
            for part in clipper.clip_polygon(points.vertices())
            if len(part) > 0
        ]

    def clip_paths(
        self, paths: Iterable[NumpyPath2d], max_sagitta: float
    ) -> Iterator[NumpyPath2d]:
        clipper = self.clipper
        for path in paths:
            for sub_path in path.sub_paths():
                path_bbox = BoundingBox2d(sub_path.control_vertices())
                if not path_bbox.has_intersection(self._bbox):
                    # path is complete outside
                    continue
                polyline = Vec2.list(sub_path.flattening(max_sagitta, segments=4))
                for part in clipper.clip_polyline(polyline):
                    if len(part) > 0:
                        yield NumpyPath2d.from_vertices(part, close=False)

    def clip_filled_paths(
        self, paths: Iterable[NumpyPath2d], max_sagitta: float
    ) -> Iterator[NumpyPath2d]:
        clipper = self.clipper
        for path in paths:
            for sub_path in path.sub_paths():
                path_bbox = BoundingBox2d(sub_path.control_vertices())
                if not path_bbox.has_intersection(self._bbox):
                    # path is complete outside
                    continue
                for part in clipper.clip_polygon(
                    Vec2.list(path.flattening(max_sagitta, segments=4))
                ):
                    if len(part) > 0:
                        yield NumpyPath2d.from_vertices(part, close=True)


class ClippingRect(ClippingPolygon):
    """Represents a rectangle as clipping shape where the edges are parallel to
    the x- and  y-axis of the coordinate system.  Removes the geometry outside the
    clipping rectangle.

    """

    def __init__(self, vertices: Iterable[UVec]) -> None:
        from ezdxf.math.clipping import ClippingRect2d

        polygon = Vec2.list(vertices)
        bbox = BoundingBox2d(polygon)
        if not bbox.has_data:
            raise ValueError("clipping box not detectable")
        size: Vec2 = bbox.size
        self.remove_all = size.x * size.y < 1e-9

        super().__init__(bbox, ClippingRect2d(bbox.extmin, bbox.extmax))

    def clip_point(self, point: Vec2) -> Optional[Vec2]:
        if self.remove_all:
            return None
        return super().clip_point(point)

    def clip_line(self, start: Vec2, end: Vec2) -> Sequence[tuple[Vec2, Vec2]]:
        if self.remove_all:
            return tuple()
        return self.clipper.clip_line(start, end)

    def clip_polyline(self, points: NumpyPoints2d) -> Sequence[NumpyPoints2d]:
        if self.remove_all:
            return (NumpyPoints2d(tuple()),)
        return super().clip_polyline(points)

    def clip_polygon(self, points: NumpyPoints2d) -> Sequence[NumpyPoints2d]:
        if self.remove_all:
            return (NumpyPoints2d(tuple()),)
        return super().clip_polygon(points)

    def clip_paths(
        self, paths: Iterable[NumpyPath2d], max_sagitta: float
    ) -> Iterator[NumpyPath2d]:
        if self.remove_all:
            return iter(tuple())
        return super().clip_paths(paths, max_sagitta)

    def clip_filled_paths(
        self, paths: Iterable[NumpyPath2d], max_sagitta: float
    ) -> Iterator[NumpyPath2d]:
        if self.remove_all:
            return iter(tuple())
        return super().clip_filled_paths(paths, max_sagitta)


class ConvexClippingPolygon(ClippingPolygon):
    """Represents an arbitrary convex polygon as clipping shape.  Removes the geometry
    outside the clipping polygon.

    """

    def __init__(self, vertices: Iterable[UVec]) -> None:
        from ezdxf.math.clipping import ConvexClippingPolygon2d

        polygon = Vec2.list(vertices)
        super().__init__(BoundingBox2d(polygon), ConvexClippingPolygon2d(polygon))


class ConcaveClippingPolygon(ClippingPolygon):
    """Represents an arbitrary concave polygon as clipping shape.  Removes the geometry
    outside the clipping polygon.

    """

    def __init__(self, vertices: Iterable[UVec]) -> None:
        from ezdxf.math.clipping import ConcaveClippingPolygon2d

        polygon = Vec2.list(vertices)
        super().__init__(BoundingBox2d(polygon), ConcaveClippingPolygon2d(polygon))


class MultiClip(ClippingShape):
    """The MultiClip combines multiple clipping shapes into a single clipping shape.

    Overlapping clipping shapes will yield strange results but are not actively
    prevented.

    """

    def __init__(self, shapes: Iterable[ClippingShape]) -> None:
        self._clipping_ranges: list[tuple[ClippingShape, BoundingBox2d]] = [
            (shape, shape.bbox()) for shape in shapes if not shape.bbox().is_empty
        ]

    def bbox(self) -> BoundingBox2d:
        bbox = BoundingBox2d()
        for _, extents in self._clipping_ranges:
            bbox.extend(extents)
        return bbox

    def shapes_in_range(self, bbox: BoundingBox2d) -> list[ClippingShape]:
        return [
            shape
            for shape, extents in self._clipping_ranges
            if bbox.has_intersection(extents)
        ]

    def clip_point(self, point: Vec2) -> Optional[Vec2]:
        for shape, _ in self._clipping_ranges:
            clipped_point = shape.clip_point(point)
            if clipped_point is not None:
                return clipped_point
        return None

    def clip_line(self, start: Vec2, end: Vec2) -> Sequence[tuple[Vec2, Vec2]]:
        result: list[tuple[Vec2, Vec2]] = []
        for clipper in self.shapes_in_range(BoundingBox2d((start, end))):
            result.extend(clipper.clip_line(start, end))
        return result

    def clip_polyline(self, points: NumpyPoints2d) -> Sequence[NumpyPoints2d]:
        result: list[NumpyPoints2d] = []
        for shape in self.shapes_in_range(points.bbox()):
            result.extend(shape.clip_polyline(points))
        return result

    def clip_polygon(self, points: NumpyPoints2d) -> Sequence[NumpyPoints2d]:
        result: list[NumpyPoints2d] = []
        for shape in self.shapes_in_range(points.bbox()):
            result.extend(shape.clip_polygon(points))
        return result

    def clip_paths(
        self, paths: Iterable[NumpyPath2d], max_sagitta: float
    ) -> Iterator[NumpyPath2d]:
        for path in paths:
            for shape in self.shapes_in_range(path.bbox()):
                yield from shape.clip_paths((path,), max_sagitta)

    def clip_filled_paths(
        self, paths: Iterable[NumpyPath2d], max_sagitta: float
    ) -> Iterator[NumpyPath2d]:
        for path in paths:
            for shape in self.shapes_in_range(path.bbox()):
                yield from shape.clip_filled_paths((path,), max_sagitta)


def find_best_clipping_shape(polygon: Iterable[UVec]) -> ClippingShape:
    """Returns the best clipping shape for the given clipping polygon.

    The function analyses the given polygon (rectangular, convex or concave polygon, ...)
    and returns the optimized (fastest) clipping shape.

    Args:
        polygon: clipping polygon as iterable vertices

    """
    points = Vec2.list(polygon)
    if is_axes_aligned_rectangle_2d(points):
        return ClippingRect(points)
    elif is_convex_polygon_2d(points, strict=False):
        return ConvexClippingPolygon(points)
    return ConcaveClippingPolygon(points)


def make_inverted_clipping_shape(
    polygon: Iterable[UVec], extents: BoundingBox2d
) -> ClippingShape:
    """Returns an inverted clipping shape that removes the geometry outside the clipping
    polygon but inside the given extents.

    .. note::

        Not implemented yet!

    Args:
        polygon: clipping polygon as iterable vertices
        extends: outer bounds of the clipping shape

    """

    # not supported/implemented yet and function signature may change!
    return find_best_clipping_shape(polygon)
