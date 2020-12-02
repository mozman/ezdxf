# distutils: language = c++
# distutils: sources = cvec.cpp
# cython: language_level=3
# Copyright (c) 2020, Manfred Moitzi
# License: MIT License

cdef extern from "cvec.cpp":
    pass

cdef extern from "cvec.hpp":
    cdef cppclass CVec3:
        CVec3()
        CVec3(double, double, double)
        double x, y, z
        CVec3 operator+(CVec3&)
        CVec3 operator-(CVec3&)
        CVec3 operator*(double)
        double magnitude()
        CVec3 normalize(double)
