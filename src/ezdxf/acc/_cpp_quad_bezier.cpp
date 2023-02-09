// Copyright (c) 2021 Manfred Moitzi
// License: MIT License
// Fast cubic bezier curve library for ezdxf
// All required checks are done in the Cython code!

#include "_cpp_quad_bezier.hpp"


CppQuadBezier::CppQuadBezier():
    p0(CppVec3()), p1(CppVec3()), p2(CppVec3()) {
}

CppQuadBezier::CppQuadBezier(CppVec3 v0, CppVec3 v1, CppVec3 v2):
    p0(v0), p1(v1), p2(v2) {
}

CppVec3 CppQuadBezier::point(double t) {
    // Required domain check for t has to be done by the caller!
    // 0 <= t <= 1
    double _1_minus_t = 1.0 - t;
    double a = _1_minus_t * _1_minus_t;
    double b = 2.0 * t * _1_minus_t;
    double c = t * t;
    return p0 * a + p1 * b + p2 * c;
}

CppVec3 CppQuadBezier::tangent(double t) {
    // Required domain check for t has to be done by the caller!
    // 0 <= t <= 1
    double a = -2.0 * (1.0 - t);
    double b = 2.0 - 4.0 * t;
    double c = 2.0 * t;
    return p0 * a + p1 * b + p2 * c;
}
