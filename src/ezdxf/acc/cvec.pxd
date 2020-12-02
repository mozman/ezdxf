# distutils: language = c++
# distutils: sources = cvec.cpp
# cython: language_level=3
# Copyright (c) 2020, Manfred Moitzi
# License: MIT License

cdef extern from "cvec.cpp":
    pass

cdef extern from "cvec.hpp":
    cdef cppclass CppVec3:
        CppVec3()
        CppVec3(double, double, double)
        double x, y, z
        CppVec3 operator+(CppVec3&)
        CppVec3 operator-(CppVec3&)
        CppVec3 operator*(double)
        double magnitude()
        CppVec3 normalize(double)
