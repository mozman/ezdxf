// Fast cubic bezier curve library for ezdxf
// All required checks are done in the Cython code!
#ifndef __EZDXF_CPP_QUAD_BEZIER_HPP__
#define __EZDXF_CPP_QUAD_BEZIER_HPP__

#include "_cpp_vec3.hpp"

class CppQuadBezier {
    public:
        CppVec3 p0, p1, p2;
        CppQuadBezier();
        CppQuadBezier(CppVec3, CppVec3, CppVec3);
        ~CppQuadBezier() = default;
        CppVec3 point(double);
        CppVec3 tangent(double);

};
#endif