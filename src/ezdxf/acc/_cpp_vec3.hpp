// Copyright (c) 2020 Manfred Moitzi
// License: MIT License
// Fast vector library for usage in C only code - header only!
#ifndef __EZDXF_CPP_VEC3_HPP__
#define __EZDXF_CPP_VEC3_HPP__

#include <math.h>

const double static rel_tol = 1e-9;

int _isclose(const double a, const double b, const double abs_tol) {
    // Has to match the Python implementation!
    double diff = fabs(b - a);
    return diff <= fabs(rel_tol * b) ||
           diff <= fabs(rel_tol * a) ||
           diff <= abs_tol;
}

class CppVec3 {
    public:
        double x;
        double y;
        double z;

        CppVec3() = default;
        CppVec3(double x, double y, double z): x(x), y(y), z(z) {};
        ~CppVec3() = default;

        CppVec3 operator+(const CppVec3& other) const{
            return CppVec3(x + other.x, y + other.y, z + other.z);
        };

        CppVec3 operator-(const CppVec3& other) const{
            return CppVec3(x - other.x, y - other.y, z - other.z);
        };

        CppVec3 operator*(double factor) const {
            return CppVec3(x * factor, y * factor, z * factor);
        };

        double magnitude_sqr() const {
            return x * x + y * y + z * z;
        };

        double magnitude() const {
            return sqrt(x * x + y * y + z * z);
        };

        CppVec3 normalize(double length) const {
            double mag = magnitude();
            if (mag == 0.0) return *this;
            return *this * (length / mag);
        };

        double distance(const CppVec3& other) const {
            return (*this - other).magnitude();
        };

        CppVec3 lerp(const CppVec3& other, double factor) const {
            return *this + (other - *this) * factor;
        };

        int isclose(const CppVec3& other, double abs_tol) const {
            return _isclose(x, other.x, abs_tol) &&
            _isclose(y, other.y, abs_tol) &&
            _isclose(z, other.z, abs_tol);
        };
};
#endif