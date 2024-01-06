#  Copyright (c) 2024, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Optional, Iterable, Iterator, Sequence, NamedTuple, Callable
import abc

from ezdxf.math import Matrix44, Vec2, BoundingBox2d, UVec
from ezdxf.npshapes import NumpyPath2d, NumpyPoints2d

__all__ = [
    "ClippingShape",
    "ClippingPortal",
    "ClippingRect",
    "ConvexClippingPolygon",
    "MultiClip",
    "find_best_clipping_shape",
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

    remove_outside: bool = True
    # - True: remove geometry outside the clipping shape
    # - False: remove geometry inside the clipping shape

    @abc.abstractmethod
    def bbox(self) -> BoundingBox2d:
        ...

    @abc.abstractmethod
    def clip_point(self, point: Vec2) -> Optional[Vec2]:
        ...

    @abc.abstractmethod
    def clip_line(self, start: Vec2, end: Vec2) -> Sequence[tuple[Vec2, Vec2]]:
        ...

    @abc.abstractmethod
    def clip_polyline(self, points: NumpyPoints2d) -> Sequence[NumpyPoints2d]:
        ...

    @abc.abstractmethod
    def clip_polygon(self, points: NumpyPoints2d) -> Sequence[NumpyPoints2d]:
        ...

    @abc.abstractmethod
    def clip_paths(
        self, paths: Iterable[NumpyPath2d], max_sagitta: float
    ) -> Iterator[NumpyPath2d]:
        ...

    @abc.abstractmethod
    def clip_filled_paths(
        self, paths: Iterable[NumpyPath2d], max_sagitta: float
    ) -> Iterator[NumpyPath2d]:
        ...


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


class ClippingRect(ClippingShape):
    """Represents a rectangle as clipping shape where the edges are parallel to
    the x- and  y-axis of the coordinate system.

    The current implementation does not support removing the content inside the
    clipping shape (remove_outside=False).

    """

    def __init__(self, vertices: Iterable[UVec], remove_outside=True) -> None:
        from ezdxf.math.clipping import ClippingRect2d

        self.remove_outside = remove_outside
        self.remove_all = False
        self.remove_none = False
        bbox = BoundingBox2d(vertices)
        if not bbox.has_data:
            raise ValueError("clipping box not detectable")
        size: Vec2 = bbox.size
        if size.x * size.y < 1e-9:
            if self.remove_outside:
                self.remove_all = True
            else:  # remove inside
                self.remove_none = True
        self._bbox = bbox
        self.clipper = ClippingRect2d(bbox.extmin, bbox.extmax)

    def bbox(self) -> BoundingBox2d:
        return self._bbox

    def clip_point(self, point: Vec2) -> Optional[Vec2]:
        if self.remove_all:
            return None
        elif self.remove_none:
            return point

        is_inside = self.clipper.is_inside(Vec2(point))
        if self.remove_outside:
            if not is_inside:
                return None
        else:  # remove inside
            if is_inside:
                return None
        return point

    def clip_line(self, start: Vec2, end: Vec2) -> Sequence[tuple[Vec2, Vec2]]:
        if self.remove_all:
            return tuple()
        if self.remove_none:
            return ((start, end),)

        # rectangular clipping box returns always a single line segment or an empty tuple
        cropped_segment = self.clipper.clip_line(start, end)
        if cropped_segment:
            return (cropped_segment,)  # type: ignore
        return tuple()

    def clip_polyline(self, points: NumpyPoints2d) -> Sequence[NumpyPoints2d]:
        if self.remove_all:
            return (NumpyPoints2d(tuple()),)
        if self.remove_none:
            return (points,)

        clipper = self.clipper
        extmin, extmax = points.extents()
        if not clipper.is_inside(extmin) or not clipper.is_inside(extmax):
            return [
                NumpyPoints2d(part) for part in clipper.clip_polyline(points.vertices())
            ]
        return (points,)

    def clip_polygon(self, points: NumpyPoints2d) -> Sequence[NumpyPoints2d]:
        if self.remove_all:
            return (NumpyPoints2d(tuple()),)
        if self.remove_none:
            return (points,)

        clipper = self.clipper
        extmin, extmax = points.extents()
        if not clipper.is_inside(extmin) or not clipper.is_inside(extmax):
            # ClippingRect2d handles only convex clipping paths and returns always a
            # single polygon:
            points = NumpyPoints2d(clipper.clip_polygon(points.vertices()))
        return (points,)

    def clip_paths(
        self, paths: Iterable[NumpyPath2d], max_sagitta: float
    ) -> Iterator[NumpyPath2d]:
        if self.remove_all:
            return tuple()
        if self.remove_none:
            return paths

        clipper = self.clipper
        for path in paths:
            box = BoundingBox2d(path.control_vertices())
            if clipper.is_inside(box.extmin) and clipper.is_inside(box.extmax):
                yield path
            for sub_path in path.sub_paths():
                polyline = Vec2.list(sub_path.flattening(max_sagitta, segments=4))
                for part in clipper.clip_polyline(polyline):
                    yield NumpyPath2d.from_vertices(part, close=False)

    def clip_filled_paths(
        self, paths: Iterable[NumpyPath2d], max_sagitta: float
    ) -> Iterator[NumpyPath2d]:
        if self.remove_all:
            return tuple()
        if self.remove_none:
            return paths

        clipper = self.clipper
        for path in paths:
            box = path.bbox()
            if not clipper.has_intersection(box):
                # path is complete outside the view
                continue
            if clipper.is_inside(box.extmin) and clipper.is_inside(box.extmax):
                # path is complete inside the view, no clipping required
                yield path
            else:
                # clipping is required, but only clipping of polygons is supported
                if path.has_sub_paths:
                    yield from self.clip_filled_paths(path.sub_paths(), max_sagitta)
                else:
                    yield NumpyPath2d.from_vertices(
                        clipper.clip_polygon(
                            Vec2.list(path.flattening(max_sagitta, segments=4))
                        ),
                        close=True,
                    )


class ConvexClippingPolygon(ClippingShape):
    """Represents an arbitrary convex polygon as clipping shape.

    The current implementation does not support removing the content inside the
    clipping shape (remove_outside=False).

    """

    def __init__(self, vertices: Iterable[UVec], remove_outside=True) -> None:
        from ezdxf.math.clipping import ClippingPolygon2d

        self.remove_outside = remove_outside
        bbox = BoundingBox2d(vertices)
        if not bbox.has_data:
            raise ValueError("clipping box not detectable")
        self._bbox = bbox
        self.clipper = ClippingPolygon2d(Vec2.generate(vertices))

    def bbox(self) -> BoundingBox2d:
        return self._bbox

    def clip_point(self, point: Vec2) -> Optional[Vec2]:
        is_inside = self.clipper.is_inside(Vec2(point))
        if self.remove_outside:
            if not is_inside:
                return None
        else:  # remove inside
            if is_inside:
                return None
        return point

    def clip_line(self, start: Vec2, end: Vec2) -> Sequence[tuple[Vec2, Vec2]]:
        cropped_segment = self.clipper.clip_line(start, end)
        if cropped_segment:
            return (cropped_segment,)  # type: ignore
        return tuple()

    def clip_polyline(self, points: NumpyPoints2d) -> Sequence[NumpyPoints2d]:
        clipper = self.clipper
        polyline_bbox = BoundingBox2d(points.extents())
        if not polyline_bbox.has_intersection(self._bbox):
            # polyline is complete outside
            return tuple()
        return [
            NumpyPoints2d(part) for part in clipper.clip_polyline(points.vertices())
        ]

    def clip_polygon(self, points: NumpyPoints2d) -> Sequence[NumpyPoints2d]:
        clipper = self.clipper
        polygon_bbox = BoundingBox2d(points.extents())
        if not polygon_bbox.has_intersection(self._bbox):
            # polygon is complete outside
            return tuple()
        points = NumpyPoints2d(clipper.clip_polygon(points.vertices()))
        return (points,)

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
                yield NumpyPath2d.from_vertices(
                    clipper.clip_polygon(
                        Vec2.list(path.flattening(max_sagitta, segments=4))
                    ),
                    close=True,
                )


class MultiClip(ClippingShape):
    """The MultiClip combines multiple clipping shapes into a single clipping shape.

    Overlapping clipping shapes and clipping shapes that "remove_inside" will yield
    strange results but are not actively prevented.

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


def find_best_clipping_shape(
    polygon: Iterable[UVec], remove_outside=True
) -> ClippingShape:
    """Returns the best clipping shape for the given clipping polygon.

    The function analyses the given polygon (rectangular, convex or concave polygon, ...)
    and returns the optimized (fastest) clipping shape.

    Args:
        polygon: clipping polygon as iterable vertices
        remove_outside: remove objects outside the clipping shape or inside the clipping
            shape (inverted clipping shape)

    """
    # That's all I got so far:
    return ClippingRect(polygon, remove_outside=remove_outside)
