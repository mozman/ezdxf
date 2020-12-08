// Copyright (c) 2020 Manfred Moitzi
// License: MIT License
// Fast cubic bezier curve library for ezdxf
// All required checks are done in the Cython code!

#include "_cpp_cubic_bezier.hpp"


CppCubicBezier::CppCubicBezier():
    p0(CppVec3()), p1(CppVec3()), p2(CppVec3()), p3(CppVec3()) {
}

CppCubicBezier::CppCubicBezier(CppVec3 v0, CppVec3 v1, CppVec3 v2, CppVec3 v3):
    p0(v0), p1(v1), p2(v2), p3(v3) {
}

void CppCubicBezier::bernstein_poly_d0(double t, double *weights) {
    // Required domain check for t has to be done by the caller!
    // 0 <= t <= 1
    double t2 = t * t;
    double _1_minus_t = 1.0 - t;
    double _1_minus_t_square = _1_minus_t * _1_minus_t;
    weights[0] = _1_minus_t_square * _1_minus_t;
    weights[1] = 3.0 * _1_minus_t_square * t;
    weights[2] = 3.0 * _1_minus_t * t2;
    weights[3] = t2 * t;
}

void CppCubicBezier::bernstein_poly_d1(double t, double *weights) {
    // Required domain check for t has to be done by the caller!
    // 0 <= t <= 1
    double t2 = t * t;
    weights[0] = -3.0 * (1.0 - t) * (1.0 - t);
    weights[1] = 3.0 * (1.0 - 4.0 * t + 3.0 * t2);
    weights[2] = 3.0 * t * (2.0 - 3.0 * t);
    weights[3] = 3.0 * t2;
}


CppVec3 CppCubicBezier::point(double t) {
    // Required domain check for t has to be done by the caller!
    // 0 <= t <= 1
    double weights[4];
    bernstein_poly_d0(t, weights);
    return p0 * weights[0] + p1 * weights[1] + p2 * weights[2] + p3 * weights[3];
}

CppVec3 CppCubicBezier::tangent(double t) {
    // Required domain check for t has to be done by the caller!
    // 0 <= t <= 1
    double weights[4];
    bernstein_poly_d1(t, weights);
    return p0 * weights[0] + p1 * weights[1] + p2 * weights[2] + p3 * weights[3];
}
