#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Optional, Iterable, Iterator, Sequence

from ezdxf.math import Matrix44, Vec2, BoundingBox2d
from ezdxf.math.clipping import ClippingRect2d
from ezdxf.npshapes import NumpyPath2d, NumpyPoints2d, single_paths
from ezdxf.protocols import SupportsBoundingBox

__all__ = ["ClippingRect"]


class ClippingRect:
    def __init__(self) -> None:
        self._stack: list[tuple[Optional[ClippingRect2d], Optional[Matrix44]]] = []
        self.view: Optional[ClippingRect2d] = None
        self.m: Optional[Matrix44] = None

    @property
    def is_active(self) -> bool:
        return self.view is not None

    def push(self, path: SupportsBoundingBox, m: Optional[Matrix44]) -> None:
        if self.view is not None:
            self._stack.append((self.view, self.m))
        box = path.bbox()
        self.view = ClippingRect2d(box.extmin, box.extmax)
        self.m = m

    def pop(self) -> None:
        if self._stack:
            self.view, self.m = self._stack.pop()
        else:
            self.view = None
            self.m = None

    def clip_point(self, point: Vec2) -> Optional[Vec2]:
        # Expected points outside the view to be removed!
        if self.m is not None:
            point = self.m.transform(point)
        if self.view is not None and not self.view.is_inside(Vec2(point)):
            return None
        return point

    def clip_line(self, start: Vec2, end: Vec2) -> Sequence[Vec2]:
        # Expected lines outside the view to be removed!
        # An arbitrary clipping polygon could return more than 1 line segment
        m = self.m
        if m is not None:
            start, end = m.fast_2d_transform((start, end))
        if self.view is not None:
            return self.view.clip_line(start, end)
        return start, end

    def clip_filled_paths(
        self, paths: Iterable[NumpyPath2d], max_sagitta: float
    ) -> Iterator[NumpyPath2d]:
        # Expected overall paths outside the view to be removed!
        view = self.view
        assert view is not None
        m = self.m
        for path in paths:
            if m is not None:
                path.transform_inplace(m)
            # path in paperspace units!
            box = path.bbox()
            if not view.has_intersection(box):
                # path is complete outside the view
                continue
            if view.is_inside(box.extmin) and view.is_inside(box.extmax):
                # path is complete inside the view, no clipping required
                yield path
            else:
                # clipping is required, but only clipping of polygons is supported
                if path.has_sub_paths:
                    yield from self.clip_filled_paths(path.sub_paths(), max_sagitta)
                else:
                    yield NumpyPath2d.from_vertices(
                        view.clip_polygon(
                            Vec2.list(path.flattening(max_sagitta, segments=4))
                        ),
                        close=True,
                    )

    def clip_paths(
        self, paths: Iterable[NumpyPath2d], max_sagitta: float
    ) -> Iterator[NumpyPath2d]:
        # Expected paths outside the view to be removed!
        view = self.view
        assert view is not None
        m = self.m

        for path in paths:
            if m is not None:
                path.transform_inplace(m)
            # path in paperspace units!
            box = BoundingBox2d(path.control_vertices())
            if view.is_inside(box.extmin) and view.is_inside(box.extmax):
                yield path
            for sub_path in path.sub_paths():
                polyline = Vec2.list(sub_path.flattening(max_sagitta, segments=4))
                for part in view.clip_polyline(polyline):
                    yield NumpyPath2d.from_vertices(part, close=False)

    def clip_polygon(self, points: NumpyPoints2d) -> NumpyPoints2d:
        # Expected polygons outside the view to be removed!
        if self.m is not None:
            points.transform_inplace(self.m)
            # points in paperspace units!
        view = self.view
        if view is not None:
            extmin, extmax = points.extents()
            if not view.is_inside(extmin) or not view.is_inside(extmax):
                return NumpyPoints2d(view.clip_polygon(points.vertices()))
        return points
