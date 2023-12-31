#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Optional, Iterable, Iterator, Sequence, Protocol

from ezdxf.math import Matrix44, Vec2, BoundingBox2d, UVec
from ezdxf.math.clipping import ClippingRect2d
from ezdxf.npshapes import NumpyPath2d, NumpyPoints2d

__all__ = ["ClippingShape", "ClippingPortal", "ClippingRect"]


class ClippingShape(Protocol):
    def clip_point(self, point: Vec2) -> Optional[Vec2]:
        # Expected points outside the view to be removed!
        ...

    def clip_line(self, start: Vec2, end: Vec2) -> Sequence[Vec2]:
        # Expected lines outside the view to be removed!
        # An arbitrary clipping polygon could return more than 1 line segment
        ...

    def clip_filled_paths(
        self, paths: Iterable[NumpyPath2d], max_sagitta: float
    ) -> Iterator[NumpyPath2d]:
        ...

    def clip_paths(
        self, paths: Iterable[NumpyPath2d], max_sagitta: float
    ) -> Iterator[NumpyPath2d]:
        # Expected paths outside the view to be removed!
        ...

    def clip_polygon(self, points: NumpyPoints2d) -> NumpyPoints2d:
        # Expected polygons outside the view to be removed!
        ...


class ClippingPortal:
    def __init__(self) -> None:
        self._stack: list[tuple[ClippingShape, Matrix44 | None]] = []
        self.portal: ClippingShape | None = None
        self.transform: Matrix44 | None = None

    @property
    def is_active(self) -> bool:
        return self.portal is not None

    def push(self, portal: ClippingShape, transform: Matrix44 | None) -> None:
        if self.portal is not None:
            self._stack.append((self.portal, self.transform))
        self.portal = portal
        self.transform = transform

    def pop(self) -> None:
        if self._stack:
            self.portal, self.transform = self._stack.pop()
        else:
            self.portal = None
            self.transform = None

    def clip_point(self, point: Vec2) -> Optional[Vec2]:
        if self.transform:
            point = self.transform.transform(point)
        if self.portal:
            return self.portal.clip_point(point)
        return point

    def clip_line(self, start: Vec2, end: Vec2) -> Sequence[Vec2]:
        # An arbitrary clipping polygon could return more than 1 line segment
        m = self.transform
        if m:
            start, end = m.fast_2d_transform((start, end))
        if self.portal:
            return self.portal.clip_line(start, end)
        return start, end

    def clip_filled_paths(
        self, paths: Iterable[NumpyPath2d], max_sagitta: float
    ) -> Iterator[NumpyPath2d]:
        # Expected overall paths outside the view to be removed!
        paths = _transform_paths(list(paths), self.transform)
        if self.portal:
            return self.portal.clip_filled_paths(paths, max_sagitta)
        return iter(paths)

    def clip_paths(
        self, paths: Iterable[NumpyPath2d], max_sagitta: float
    ) -> Iterator[NumpyPath2d]:
        # Expected paths outside the view to be removed!
        paths = _transform_paths(list(paths), self.transform)
        if self.portal:
            return self.portal.clip_paths(paths, max_sagitta)
        return iter(paths)

    def clip_polygon(self, points: NumpyPoints2d) -> NumpyPoints2d:
        # Expected polygons outside the view to be removed!
        if self.transform is not None:
            points.transform_inplace(self.transform)
        if self.portal:
            return self.portal.clip_polygon(points)
        return points

    def transform_matrix(self, m: Matrix44) -> Matrix44:
        if self.transform is not None:
            return m @ self.transform
        return m


def _transform_paths(paths: list[NumpyPath2d], m: Matrix44 | None) -> list[NumpyPath2d]:
    if m is None:
        return paths
    for path in paths:
        path.transform_inplace(m)
    return paths


class ClippingRect:
    def __init__(self, vertices: Iterable[UVec]) -> None:
        bbox = BoundingBox2d(vertices)
        if bbox.extmin is None or bbox.extmax is None:
            raise ValueError("clipping box not detectable")
        size: Vec2 = bbox.size
        self.nothing_can_pass = size.x * size.y < 1e-9
        self.clipper: ClippingRect2d = ClippingRect2d(bbox.extmin, bbox.extmax)

    def clip_point(self, point: Vec2) -> Optional[Vec2]:
        # Expected points outside the view to be removed!
        if self.nothing_can_pass or not self.clipper.is_inside(Vec2(point)):
            return None
        return point

    def clip_line(self, start: Vec2, end: Vec2) -> Sequence[Vec2]:
        # Expected lines outside the view to be removed!
        # An arbitrary clipping polygon could return more than 1 line segment
        if self.nothing_can_pass:
            return start, end
        return self.clipper.clip_line(start, end)

    def clip_filled_paths(
        self, paths: Iterable[NumpyPath2d], max_sagitta: float
    ) -> Iterator[NumpyPath2d]:
        # Expected overall paths outside the view to be removed!
        if self.nothing_can_pass:
            return iter(paths)
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

    def clip_paths(
        self, paths: Iterable[NumpyPath2d], max_sagitta: float
    ) -> Iterator[NumpyPath2d]:
        # Expected paths outside the view to be removed!
        if self.nothing_can_pass:
            return iter(paths)

        clipper = self.clipper
        for path in paths:
            box = BoundingBox2d(path.control_vertices())
            if clipper.is_inside(box.extmin) and clipper.is_inside(box.extmax):
                yield path
            for sub_path in path.sub_paths():
                polyline = Vec2.list(sub_path.flattening(max_sagitta, segments=4))
                for part in clipper.clip_polyline(polyline):
                    yield NumpyPath2d.from_vertices(part, close=False)

    def clip_polygon(self, points: NumpyPoints2d) -> NumpyPoints2d:
        # Expected polygons outside the view to be removed!
        if self.nothing_can_pass:
            return NumpyPoints2d(tuple())
        clipper = self.clipper
        extmin, extmax = points.extents()
        if not clipper.is_inside(extmin) or not clipper.is_inside(extmax):
            return NumpyPoints2d(clipper.clip_polygon(points.vertices()))
        return points
