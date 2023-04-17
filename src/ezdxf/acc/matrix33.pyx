# cython: language_level=3
# distutils: language = c++
# Copyright (c) 2023, Manfred Moitzi
# License: MIT License
from typing import Optional, Iterable, Iterator, TYPE_CHECKING
import math

from .vector cimport Vec2, v2_normalize

from libc.math cimport sin, cos, tan

cdef double[9] IDENTITY = [
    1.0, 0.0, 0.0,
    0.0, 1.0, 0.0,
    0.0, 0.0, 1.0
]

if TYPE_CHECKING:
    from ezdxf.math import UVec

cdef void set_floats(double *m, object values: Iterable[float]) except *:
    cdef int i = 0
    for v in values:
        if i < 9:  # Do not write beyond array bounds
            m[i] = v
        i += 1
    if i != 9:
        raise ValueError(f"expected 9 floats,  got {i}")

cdef class Matrix33:
    cdef double m[9]

    def __cinit__(self, values: Optional[Iterable[float]] = None):
        if values is None:  # default constructor Matrix33(): fastest setup
            self.m = IDENTITY  # memcopy!
        else:
            set_floats(self.m, values)

    def __reduce__(self):
        return Matrix33, (tuple(self),)

    def __iter__(self) -> Iterator[float]:
        cdef int i
        for i in range(9):
            yield self.m[i]

    def isclose(self, m: Matrix33, abs_tol=1e-12) -> bool:
        return all(
            math.isclose(v1, v2, abs_tol=abs_tol)
            for v1, v2 in zip(self, m)
        )

    def __repr__(self) -> str:
        def format_row(row):
            return "(%s)" % ", ".join(str(value) for value in row)
        cdef double* m = self.m
        return "Matrix44(%s)" % ", ".join(
            (
                format_row((m[0], m[1], m[2])),
                format_row((m[3], m[4], m[5])),
                format_row((m[6], m[7], m[8])),
            )
        )

    @staticmethod
    def translate(double dx, double dy) -> Matrix33:
        cdef Matrix33 mat = Matrix33()
        mat.m[6] = dx
        mat.m[7] = dy
        return mat

    @staticmethod
    def scale(double sx, sy = None) -> Matrix33:
        cdef Matrix33 mat = Matrix33()
        mat.m[0] = sx
        mat.m[4] = sx if sy is None else sy
        return mat

    @staticmethod
    def rotate(double angle) -> Matrix33:
        cdef Matrix33 mat = Matrix33()
        cdef double cos_a = cos(angle)
        cdef double sin_a = sin(angle)
        mat.m[0] = cos_a
        mat.m[1] = sin_a
        mat.m[3] = -sin_a
        mat.m[4] = cos_a
        return mat

    @staticmethod
    def shear(double angle_x, double angle_y) -> Matrix33:
        cdef Matrix33 mat = Matrix33()
        cdef double tx = tan(angle_x)
        cdef double ty = tan(angle_y)
        mat.m[1] = tx
        mat.m[3] = ty
        return mat

    @staticmethod
    def chain(*matrices: Matrix33) -> Matrix33:
        cdef Matrix33 transformation = Matrix33()
        for matrix in matrices:
            transformation = transformation @ matrix
        return transformation

    def transform(self, vector: UVec) -> Vec2:
        cdef Vec2 res = Vec2(vector)
        cdef double x = res.x
        cdef double y = res.y
        cdef double *m = self.m

        res.x = x * m[0] + y * m[3] + m[6]
        res.y = x * m[1] + y * m[4] + m[7]
        return res

    def transform_direction(self, vector: UVec, normalize=False) -> Vec2:
        cdef Vec2 res = Vec2(vector)
        cdef double x = res.x
        cdef double y = res.y
        cdef double *m = self.m

        res.x = x * m[0] + y * m[3]
        res.y = x * m[1] + y * m[4]
        if normalize:
            return v2_normalize(res, 1.0)
        else:
            return res

    def transform_vertices(self, vertices: Iterable[UVec]) -> Iterator[Vec2]:
        cdef double *m = self.m
        cdef Vec2 res
        cdef double x, y

        for vector in vertices:
            res = Vec2(vector)
            x = res.x
            y = res.y

            res.x = x * m[0] + y * m[3] + m[6]
            res.y = x * m[1] + y * m[4] + m[7]
            yield res

    def __matmul__(Matrix33 self, Matrix33 other) -> Matrix33:
        """Matrix multiplication."""
        cdef Matrix33 res = Matrix33()
        cdef double *m1 = self.m
        cdef double *m2 = other.m
        cdef double *m3 = res.m

        m3[0] = m1[0] * m2[0] + m1[1] * m2[3] + m1[2] * m2[6]
        m3[1] = m1[0] * m2[1] + m1[1] * m2[4] + m1[2] * m2[7]
        m3[2] = m1[0] * m2[2] + m1[1] * m2[5] + m1[2] * m2[8]

        m3[3] = m1[3] * m2[0] + m1[4] * m2[3] + m1[5] * m2[6]
        m3[4] = m1[3] * m2[1] + m1[4] * m2[4] + m1[5] * m2[7]
        m3[5] = m1[3] * m2[2] + m1[4] * m2[5] + m1[5] * m2[8]

        m3[6] = m1[6] * m2[0] + m1[7] * m2[3] + m1[8] * m2[6]
        m3[7] = m1[6] * m2[1] + m1[7] * m2[4] + m1[8] * m2[7]
        m3[8] = m1[6] * m2[2] + m1[7] * m2[5] + m1[8] * m2[8]

        return res
