// Fast cubic bezier curve library for ezdxf
// All required checks are done in the Cython code!
#ifndef __EZDXF_CPP_CUBIC_BEZIER_HPP__
#define __EZDXF_CPP_CUBIC_BEZIER_HPP__

#include "_cpp_vec3.hpp"

class CppCubicBezier {
    public:
        CppVec3 p0, p1, p2, p3;
        CppCubicBezier();
        CppCubicBezier(CppVec3, CppVec3, CppVec3, CppVec3);
        ~CppCubicBezier() = default;
        CppVec3 point(double);
        CppVec3 tangent(double);

    private:
        void bernstein_poly_d0(double, double *);
        void bernstein_poly_d1(double, double *);
};
#endif