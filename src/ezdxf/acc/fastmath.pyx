# cython: language_level=3
# Copyright (c) 2020, Manfred Moitzi
# License: MIT License

from libc.math cimport fabs

cdef double abs_tol = 1e-12

cdef bint isclose(double a, double b):
    return fabs(a - b) < abs_tol

cdef class Vec2:
    """ Immutable 2D vector.

    Init:

    - Vec2()
    - Vec2(vec2)
    - Vec2(vec3)
    - Vec2((x, y))
    - Vec2((x, y, z)), ignore z-axis
    - Vec2(x, y)
    - Vec2(x, y, z), ignore z-axis

    """
    cdef readonly double x, y

    def __cinit__(self, *args):
        cdef Py_ssize_t count = len(<tuple> args)

        if count == 0:  # fastest init - default constructor
            self.x = 0
            self.y = 0
            return

        if count == 1:
            arg = args[0]
            if isinstance(arg, Vec2):
                # fast init by Vec2()
                self.x = (<Vec2> arg).x
                self.y = (<Vec2> arg).y
                return
            if isinstance(arg, Vec3):
                # fast init by Vec3()
                self.x = (<Vec3> arg).x
                self.y = (<Vec3> arg).y
                return
            args = arg
            count = len(args)

        # ignore z-axis but raise error for 4 or more arguments
        if count > 3:
            raise TypeError('invalid argument count')

        # slow init by sequence
        self.x = args[0]
        self.y = args[1]

    def __str__(self) -> str:
        return '({}, {})'.format(self.x, self.y)

    def __repr__(self) -> str:
        return 'Vec2' + self.__str__()

    def __len__(self) -> int:
        return 2

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __eq__(self, other) -> bool:
        if not isinstance(other, Vec2):
            other = Vec2(other)
        return bool(v2isclose(self, other))

    def __lt__(self, other) -> bool:
        cdef Vec2 o = Vec2(other)
        if self.x == o.x:
            return self.y < o.y
        else:
            return self.x < o.x

    def __bool__(self) -> bool:
        return self.x != 0 or self.y != 0

    @property
    def is_null(self) -> bool:
        return self.x == 0 and self.y == 0

cdef class Vec3:
    """ Immutable 3D vector.

    Init:

    - Vec3()
    - Vec3(vec3)
    - Vec3(vec2)
    - Vec3((x, y))
    - Vec3((x, y, z))
    - Vec3(x, y)
    - Vec3(x, y, z)

    """
    cdef readonly double x, y, z

    def __cinit__(self, *args):
        cdef Py_ssize_t count = len(<tuple> args)
        if count == 0:  # fastest init - default constructor
            self.x = 0
            self.y = 0
            self.z = 0
            return

        if count == 1:
            arg0 = args[0]
            if isinstance(arg0, Vec3):
                # fast init by Vec3()
                self.x = (<Vec3> arg0).x
                self.y = (<Vec3> arg0).y
                self.z = (<Vec3> arg0).z
                return
            if isinstance(arg0, Vec2):
                # fast init by Vec2()
                self.x = (<Vec2> arg0).x
                self.y = (<Vec2> arg0).y
                self.z = 0
                return
            args = arg0
            count = len(args)

        if count > 3:
            raise TypeError('invalid argument count')

        # slow init by sequence
        self.x = args[0]
        self.y = args[1]
        if count > 2:
            self.z = args[2]
        else:
            self.z = 0.0

    def __repr__(self)-> str:
        return f"Vec3({self.x}, {self.y}, {self.z})"

    def __add__(self, other) -> 'Vec3':
        if not isinstance(other, Vec3):
            other = Vec3(other)
        return v3add(self, other)

    def __radd__(self, other) -> 'Vec3':
        if not isinstance(other, Vec3):
            other = Vec3(other)
        return v3add(other, self)

    def __sub__(self, other) -> 'Vec3':
        if not isinstance(other, Vec3):
            other = Vec3(other)
        return v3sub(self, other)

    def __rsub__(self, other) -> 'Vec3':
        if not isinstance(other, Vec3):
            other = Vec3(other)
        return v3sub(other, self)

cdef Vec3 v3add(Vec3 a, Vec3 b):
    res = Vec3()
    res.x = a.x + b.x
    res.y = a.y + b.y
    res.z = a.z + b.z
    return res

cdef Vec3 v3sub(Vec3 a, Vec3 b):
    res = Vec3()
    res.x = a.x - b.x
    res.y = a.y - b.y
    res.z = a.z - b.z
    return res

cdef Vec2 v2add(Vec2 a, Vec2 b):
    res = Vec2()
    res.x = a.x + b.x
    res.y = a.y + b.y
    return res

cdef bint v2isclose(Vec2 a, Vec2 b):
    return isclose(a.x, b.x) and isclose(a.y, b.y)
