# cython: language_level=3
# distutils: language = c++
# Copyright (c) 2021, Manfred Moitzi
# License: MIT License

from ._cpp_vec3 cimport CppVec3

cdef extern from "_cpp_quad_bezier.hpp":
    cdef cppclass CppQuadBezier:
        CppVec3 p0, p1, p2

        CppQuadBezier();
        CppQuadBezier(CppVec3, CppVec3, CppVec3);
        CppVec3 point(double t);
        CppVec3 tangent(double t);