#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
from typing import Tuple, Iterable
import math
from ezdxf.math import Vec3, Vertex

LineSegment = Tuple[Vec3, Vec3]


class LineTypeRenderer:
    def __init__(self, dashes: Iterable[float]):
        # Simplified dash pattern: line-gap-line-gap
        # Dash pattern should end with a gap (even count).
        # Dash length in drawing units.

        self._dashes = tuple(dashes)
        self._dash_count = len(self._dashes)
        self.is_solid = True
        self._current_dash = 0
        self._current_dash_length = 0
        if self._dash_count > 1:
            self.is_solid = False
            self._current_dash_length = self._dashes[0]
            self._is_dash = True

    def line_segment(
            self, start: Vertex, end: Vertex) -> Iterable[LineSegment]:
        start = Vec3(start)
        end = Vec3(end)
        if self.is_solid or start.isclose(end):
            yield start, end
            return

        segment_vec = end - start
        segment_length = segment_vec.magnitude
        segment_dir = segment_vec / segment_length  # normalize

        for is_dash, dash_length in self._render_dashes(segment_length):
            end = start + segment_dir * dash_length
            if is_dash:
                yield start, end
            start = end

    def line_segments(
            self, vertices: Iterable[Vertex]) -> Iterable[LineSegment]:
        last = None
        for vertex in vertices:
            if last is not None:
                yield from self.line_segment(last, vertex)
            last = vertex

    def _render_dashes(self, length: float) -> Tuple[bool, float]:
        if length <= self._current_dash_length:
            self._current_dash_length -= length
            yield self._is_dash, length
            if math.isclose(self._current_dash_length, 0.0):
                self._cycle_dashes()
        else:
            # Avoid deep recursions!
            while length > self._current_dash_length:
                length -= self._current_dash_length
                yield from self._render_dashes(self._current_dash_length)
            if length > 0.0:
                yield from self._render_dashes(length)

    def _cycle_dashes(self):
        self._current_dash = (self._current_dash + 1) % self._dash_count
        self._current_dash_length = self._dashes[self._current_dash]
        self._is_dash = not self._is_dash
