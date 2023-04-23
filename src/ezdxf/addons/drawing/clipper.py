#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import Optional, Iterable, Iterator, Sequence

from ezdxf.math import AnyVec, Matrix44, Vec2, BoundingBox2d
from ezdxf.math.clipping import ClippingRect2d
from ezdxf.path import Path, Path2d, bbox, from_vertices, single_paths

__all__ = ["ClippingRect"]


class ClippingRect:
    def __init__(self) -> None:
        self._stack: list[tuple[Optional[ClippingRect2d], Optional[Matrix44]]] = []
        self.view: Optional[ClippingRect2d] = None
        self.m: Optional[Matrix44] = None

    @property
    def is_active(self) -> bool:
        return self.view is not None

    def push(self, path: Path | Path2d, m: Optional[Matrix44]) -> None:
        if self.view is not None:
            self._stack.append((self.view, self.m))
        box = BoundingBox2d(path.control_vertices())
        self.view = ClippingRect2d(box.extmin, box.extmax)
        self.m = m

    def pop(self) -> None:
        if self._stack:
            self.view, self.m = self._stack.pop()
        else:
            self.view = None
            self.m = None

    def clip_point(self, point: AnyVec) -> Optional[AnyVec]:
        if self.m is not None:
            point = self.m.transform(point)
        if self.view is not None and not self.view.is_inside(Vec2(point)):
            return None
        return point

    def clip_line(self, start: AnyVec, end: AnyVec) -> Sequence[AnyVec]:
        # An arbitrary clipping polygon could return more than 1 line segment
        m = self.m
        if m is not None:
            start, end = m.fast_2d_transform((start, end))
        if self.view is not None:
            return self.view.clip_line(start, end)
        return start, end

    def clip_filled_paths(
        self, paths: Iterable[Path | Path2d], max_sagitta: float
    ) -> Iterator[Path | Path2d]:
        for path in paths:
            box = BoundingBox2d(path.control_vertices())
            view = self.view
            assert view is not None
            if view.is_inside(box.extmin) and view.is_inside(box.extmax):
                yield path
            else:
                yield from_vertices(
                    view.clip_polygon(
                        Vec2.list(path.flattening(max_sagitta, segments=16))
                    ),
                    close=True,
                )

    def clip_paths(
        self, paths: Iterable[Path | Path2d], max_sagitta: float
    ) -> Iterator[Path | Path2d]:
        view = self.view
        assert view is not None
        m = self.m

        for path in paths:
            if m is not None:
                path = path.transform(m)
            box = BoundingBox2d(path.control_vertices())
            if view.is_inside(box.extmin) and view.is_inside(box.extmax):
                yield path
            for sub_path in single_paths([path]):  # type: ignore
                polyline = Vec2.list(sub_path.flattening(max_sagitta, segments=16))
                for part in view.clip_polyline(polyline):
                    yield from_vertices(part, close=False)

    def clip_polygon(self, points: Iterable[AnyVec]) -> Sequence[Vec2]:
        if self.m is not None:
            points = self.m.fast_2d_transform(points)
        view = self.view
        if view is not None:
            box = BoundingBox2d(points)
            if not view.is_inside(box.extmin) or not view.is_inside(box.extmax):
                return view.clip_polygon(points)
        return list(points)
