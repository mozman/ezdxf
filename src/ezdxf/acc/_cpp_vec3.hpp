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

        CppVec3 operator+(const CppVec3& v) {
            return CppVec3(x + v.x, y + v.y, z + v.z);
        };

        CppVec3 operator-(const CppVec3& v) {
            return CppVec3(x - v.x, y - v.y, z - v.z);
        };

        CppVec3 operator*(double f) {
            return CppVec3(x * f, y * f, z * f);
        };
        double magnitude() {
            return sqrt(x * x + y * y + z * z);
        };

        CppVec3 normalize(double length) {
            double mag = magnitude();
            if (mag == 0.0) return *this;
            return (*this) * (length / mag);
        };

        double distance(const CppVec3 v) {
            double dx = x - v.x;
            double dy = y - v.y;
            double dz = z - v.z;
            return sqrt(dx * dx + dy * dy + dz * dz);
        };

        CppVec3 lerp(const CppVec3 v, double factor) {
            const double rx = this->x + (v.x - this->x) * factor;
            const double ry = this->y + (v.y - this->y) * factor;
            const double rz = this->z + (v.z - this->z) * factor;
            return CppVec3(rx, ry, rz);
        };
};
#endif