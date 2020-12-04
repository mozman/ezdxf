cdef extern from "_cpp_vec3.hpp":
    cdef cppclass CppVec3:
        double x, y, z
        CppVec3()
        CppVec3(double, double, double)
        CppVec3 operator+(const CppVec3&)
        CppVec3 operator-(const CppVec3&)
        CppVec3 operator*(double)
        double magnitude()
        CppVec3 normalize(double)
        double distance(const CppVec3 &)
        CppVec3 lerp(const CppVec3&, double)

