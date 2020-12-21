// Copyright (c) 2020 Manfred Moitzi
// License: MIT License
// Fast vector library for usage in C only code - header only!
#ifndef __EZDXF_CPP_VEC3_HPP__
#define __EZDXF_CPP_VEC3_HPP__

#include <math.h>

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

        CppVec3 cross(const CppVec3& other) const {
            return CppVec3(
                y * other.z - z * other.y,
                z * other.x - x * other.z,
                x * other.y - y * other.x
            );
        };

        double dot(const CppVec3& other) const {
            return x * other.x + y * other.y + z * other.z;
        };

        double distance(const CppVec3& other) const {
            return (*this - other).magnitude();
        };

        CppVec3 lerp(const CppVec3& other, double factor) const {
            return *this + (other - *this) * factor;
        };

        int isclose(const CppVec3& other, double abs_tol) const {
            const CppVec3 diff = *this - other;
            return
                fabs(diff.x) <= abs_tol &&
                fabs(diff.y) <= abs_tol &&
                fabs(diff.z) <= abs_tol;
        };
};
#endif