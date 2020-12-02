# cython: language_level=3
# distutils: language = c++
# Copyright (c) 2020, Manfred Moitzi
# License: MIT License

cdef extern from "cvec.hpp":
    cdef cppclass CppVec3:
        double x, y, z
        CppVec3()
        CppVec3(double, double, double)
        CppVec3 operator+(CppVec3&)
        CppVec3 operator*(double)


