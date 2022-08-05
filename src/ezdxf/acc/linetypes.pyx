# cython: language_level=3
# distutils: language = c++
#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import Tuple, Iterable, TYPE_CHECKING, Sequence
from .vector cimport Vec3, v3_isclose, v3_sub, v3_magnitude, v3_mul, isclose
import cython

if TYPE_CHECKING:
    from ezdxf.math import UVec

LineSegment = Tuple[Vec3, Vec3]

DEF ABS_TOL = 1e-12
DEF REL_TOL = 1e-9
DEF MAX_DASHES = 32

cdef class _LineTypeRenderer:
    cdef double _dashes[MAX_DASHES]
    cdef int _dash_count
    cdef readonly bint is_solid
    cdef bint _is_dash
    cdef int _current_dash
    cdef double _current_dash_length

    def __init__(self, dashes: Sequence[float]):
        cdef int i
        self._dash_count = len(dashes)
        if self._dash_count > MAX_DASHES:
            raise ValueError(
                f"line pattern too long, maximum of len(dashes) is 32"
            )
        for i in range(self._dash_count):
            self._dashes[i] = dashes[i]

        self.is_solid = True
        self._is_dash = False
        self._current_dash = 0
        self._current_dash_length = 0.0

        if self._dash_count > 1:
            self.is_solid = False
            self._current_dash_length = self._dashes[0]
            self._is_dash = True

    def line_segment(self, start: UVec, end: UVec) -> Iterable[LineSegment]:
        cdef Vec3 _start = Vec3(start)
        cdef Vec3 _end = Vec3(end)
        cdef Vec3 segment_vec, segment_dir
        cdef double segment_length

        if self.is_solid or v3_isclose(_start, _end, ABS_TOL, REL_TOL):
            yield _start, _end
            return

        segment_vec = v3_sub(_end, _start)
        segment_length = v3_magnitude(segment_vec)
        with cython.cdivision:
            segment_dir = v3_mul(segment_vec, 1.0 / segment_length)  # normalize

        for is_dash, dash_length in self._render_dashes(segment_length):
            _end = _start + segment_dir * dash_length
            if is_dash:
                yield _start, _end
            _start = _end

    def _render_dashes(self, double length):
        if length <= self._current_dash_length:
            self._current_dash_length -= length
            yield self._is_dash, length
            if self._current_dash_length < ABS_TOL:
                self._cycle_dashes()
        else:
            # Avoid deep recursions!
            while length > self._current_dash_length:
                length -= self._current_dash_length
                yield from self._render_dashes(self._current_dash_length)
            if length > 0.0:
                yield from self._render_dashes(length)

    cdef _cycle_dashes(self):
        with cython.cdivision:
            self._current_dash = (self._current_dash + 1) % self._dash_count
        self._current_dash_length = self._dashes[self._current_dash]
        self._is_dash = not self._is_dash
