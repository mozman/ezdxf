# cython: language_level=3
# distutils: language = c++
# Copyright (c) 2020, Manfred Moitzi
# License: MIT License

from ._cpp_vec3 cimport CppVec3

cdef extern from "_cpp_cubic_bezier.hpp":
    cdef cppclass CppCubicBezier:
        CppVec3 p0, p1, p2, p3

        CppCubicBezier();
        CppCubicBezier(CppVec3, CppVec3, CppVec3, CppVec3);
        CppVec3 point(double t);
        CppVec3 tangent(double t);