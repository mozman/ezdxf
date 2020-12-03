# cython: language_level=3
# distutils: language = c++
# Copyright (c) 2020, Manfred Moitzi
# License: MIT License

cdef extern from "_cpp_vec3.hpp":
    cdef cppclass CppVec3:
        double x, y, z
        CppVec3()
        CppVec3(double, double, double)
        CppVec3 operator+(const CppVec3&)
        CppVec3 operator*(double)
        double distance(const CppVec3 &)
        CppVec3 lerp(const CppVec3&, double)



cdef extern from "_cpp_cubic_bezier.hpp":
    cdef cppclass CppCubicBezier:
        CppVec3 p0, p1, p2, p3

        CppCubicBezier();
        CppCubicBezier(CppVec3, CppVec3, CppVec3, CppVec3);
        CppVec3 point(double t);
        CppVec3 tangent(double t);