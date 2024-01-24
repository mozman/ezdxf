# cython: language_level=3
# distutils: language = c++
# Copyright (c) 2022-2023, Manfred Moitzi
# License: MIT License
# type: ignore -- pylance sucks at type-checking cython files
from typing import Tuple, Iterable, TYPE_CHECKING, Sequence
import cython
from .vector cimport Vec3, isclose, v3_from_cpp_vec3
from ._cpp_vec3 cimport CppVec3
from libcpp.vector cimport vector

if TYPE_CHECKING:
    from ezdxf.math import UVec

LineSegment = Tuple[Vec3, Vec3]

cdef extern from "constants.h":
    const double ABS_TOL
    const double REL_TOL

cdef class _LineTypeRenderer:
    cdef vector[double] _dashes
    cdef int _dash_count
    cdef readonly bint is_solid
    cdef bint _is_dash
    cdef int _current_dash
    cdef double _current_dash_length

    def __init__(self, dashes: Sequence[float]):
        self._dashes = dashes  # this really works!!
        self._dash_count = self._dashes.size()

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
        cdef CppVec3 cpp_start = CppVec3(_start.x, _start.y, _start.z)
        cdef CppVec3 cpp_end = CppVec3(_end.x, _end.y, _end.z)
        cdef CppVec3 segment_vec, segment_dir
        cdef double segment_length, dash_length
        cdef vector[double] dashes

        if self.is_solid or cpp_start.isclose(cpp_end, ABS_TOL):
            yield v3_from_cpp_vec3(cpp_start), v3_from_cpp_vec3(cpp_end)
            return

        segment_vec = cpp_end - cpp_start
        segment_length = segment_vec.magnitude()
        with cython.cdivision:
            segment_dir = segment_vec * (1.0 / segment_length)  # normalize

        self._render_dashes(segment_length, dashes)
        for dash_length in dashes:
            cpp_end = cpp_start + (segment_dir * abs(dash_length))
            if dash_length > 0:
                yield v3_from_cpp_vec3(cpp_start), v3_from_cpp_vec3(cpp_end)
            cpp_start = cpp_end

    cdef _render_dashes(self, double length, vector[double] &dashes):
        if length <= self._current_dash_length:
            self._current_dash_length -= length
            dashes.push_back(length if self._is_dash else -length)
            if self._current_dash_length < ABS_TOL:
                self._cycle_dashes()
        else:
            # Avoid deep recursions!
            while length > self._current_dash_length:
                length -= self._current_dash_length
                self._render_dashes(self._current_dash_length, dashes)
            if length > 0.0:
                self._render_dashes(length, dashes)

    cdef _cycle_dashes(self):
        with cython.cdivision:
            self._current_dash = (self._current_dash + 1) % self._dash_count
        self._current_dash_length = self._dashes[self._current_dash]
        self._is_dash = not self._is_dash
