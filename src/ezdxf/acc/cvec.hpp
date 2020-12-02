// Fast vector library for usage in C only code.
#ifndef __EZDXF_CVEC__
#define __EZDXF_CVEC__

#include <math.h>

class CVec3 {
    public:
        double x;
        double y;
        double z;

        CVec3() {};
        CVec3(double x, double y, double z): x(x), y(y), z(z) {};
        ~CVec3() {}

        CVec3 operator+(CVec3& v) {
            return CVec3(x + v.x, y + v.y, z + v.z);
        };

        CVec3 operator-(CVec3& v) {
            return CVec3(x - v.x, y - v.y, z - v.z);
        };

        CVec3 operator*(double f) {
            return CVec3(x * f, y * f, z * f);
        };
        double magnitude() {
            return sqrt(x * x + y * y + z* z);
        };

        CVec3 normalize(double length) {
            double mag = magnitude();
            if (mag == 0.0) return *this;
            double f = length / mag;
            return (*this) * f;
        };
};
#endif