# cython: language_level=3
# distutils: language = c++
# Copyright (c) 2020-2021, Manfred Moitzi
# License: MIT License
from typing import Sequence, Iterable, Tuple, TYPE_CHECKING
from itertools import chain
import math
from .vector cimport (
Vec3, v3_normalize, v3_isclose, v3_cross, v3_dot,
)
from .vector import X_AXIS, Y_AXIS, Z_AXIS, NULLVEC

from libc.math cimport fabs, sin, cos, tan

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex

DEF ABS_TOL = 1e-12
DEF REL_TOL = 1e-9

cdef double[16] IDENTITY = [
    1.0, 0.0, 0.0, 0.0,
    0.0, 1.0, 0.0, 0.0,
    0.0, 0.0, 1.0, 0.0,
    0.0, 0.0, 0.0, 1.0
]

cdef void set_floats(double *m, object values: Iterable[float]) except *:
    cdef int i = 0
    for v in values:
        if i < 16:  # Do not write beyond array bounds
            m[i] = v
        i += 1
    if i != 16:
        raise ValueError("invalid argument count")

cdef class Matrix44:
    def __cinit__(self, *args):
        cdef int nargs = len(args)
        if nargs == 0:  # default constructor Matrix44(): fastest setup
            self.m = IDENTITY  # memcopy!
        elif nargs == 1:  # 16 numbers: slow setup
            set_floats(self.m, args[0])
        elif nargs == 4:  # 4 rows of 4 numbers: slowest setup
            set_floats(self.m, chain(*args))
        else:
            raise ValueError("invalid argument count: 4 row vectors or "
                             "iterable of 16 numbers")

    def __reduce__(self):
        return Matrix44, (tuple(self),)

    def __getitem__(self, tuple index: Tuple[int, int]) -> float:
        cdef int row = index[0]
        cdef int col = index[1]
        cdef int i = row * 4 + col

        if 0 <= i < 16 and 0 <= col < 4:
            return self.m[i]
        else:
            raise IndexError(f'index out of range: {index}')

    def __setitem__(self, tuple index: Tuple[int, int], double value: float):
        cdef int row = index[0]
        cdef int col = index[1]
        cdef int i = row * 4 + col

        if 0 <= i < 16 and 0 <= col < 4:
            self.m[i] = value
        else:
            raise IndexError(f'index out of range: {index}')

    def __iter__(self):
        cdef int i
        for i in range(16):
            yield self.m[i]

    def __repr__(self) -> str:
        def format_row(row):
            return "(%s)" % ", ".join(str(value) for value in row)

        return "Matrix44(%s)" % \
               ", ".join(format_row(row) for row in self.rows())

    def get_2d_transformation(self) -> Tuple[float, ...]:
        cdef double *m = self.m
        return m[0], m[1], 0.0, m[4], m[5], 0.0, m[12], m[13], 1.0

    def get_row(self, int row) -> Tuple[float, ...]:
        cdef index = row * 4
        if 0 <= index < 13:
            return self.m[index], self.m[index + 1], self.m[index + 2], self.m[
                index + 3]
        else:
            raise IndexError(f'invalid row index: {row}')

    def set_row(self, int row, values: Sequence[float]) -> None:
        cdef Py_ssize_t count = len(values)
        cdef Py_ssize_t start = row * 4
        cdef Py_ssize_t i
        if 0 <= row < 4:
            if count > 4:
                count = 4
            for i in range(count):
                self.m[start + i] = values[i]
        else:
            raise IndexError(f'invalid row index: {row}')

    def get_col(self, int col) -> Tuple[float, ...]:
        if 0 <= col < 4:
            return self.m[col], self.m[col + 4], \
                   self.m[col + 8], self.m[col + 12]
        else:
            raise IndexError(f'invalid col index: {col}')

    def set_col(self, int col, values: Sequence[float]):
        cdef Py_ssize_t count = len(values)
        cdef Py_ssize_t i
        if 0 <= col < 4:
            if count > 4:
                count = 4
            for i in range(count):
                self.m[col + i * 4] = values[i]
        else:
            raise IndexError(f'invalid col index: {col}')

    def rows(self) -> Iterable[Tuple[float, ...]]:
        return (self.get_row(index) for index in (0, 1, 2, 3))

    def columns(self) -> Iterable[Tuple[float, ...]]:
        return (self.get_col(index) for index in (0, 1, 2, 3))

    def copy(self) -> 'Matrix44':
        cdef Matrix44 _copy = Matrix44()
        _copy.m = self.m
        return _copy

    __copy__ = copy

    @property
    def origin(self) -> 'Vec3':
        cdef Vec3 v = Vec3()
        v.x = self.m[12]
        v.y = self.m[13]
        v.z = self.m[14]
        return v

    @origin.setter
    def origin(self, v: 'Vertex') -> None:
        cdef Vec3 origin = Vec3(v)
        self.m[12] = origin.x
        self.m[13] = origin.y
        self.m[14] = origin.z

    @property
    def ux(self) -> Vec3:
        return self.get_ux()

    cdef Vec3 get_ux(self):
        cdef Vec3 v = Vec3()
        v.x = self.m[0]
        v.y = self.m[1]
        v.z = self.m[2]
        return v

    @property
    def uy(self) -> Vec3:
        return self.get_uy()

    cdef Vec3 get_uy(self):
        cdef Vec3 v = Vec3()
        v.x = self.m[4]
        v.y = self.m[5]
        v.z = self.m[6]
        return v

    @property
    def uz(self) -> Vec3:
        return self.get_uz()

    cdef Vec3 get_uz(self):
        cdef Vec3 v = Vec3()
        v.x = self.m[8]
        v.y = self.m[9]
        v.z = self.m[10]
        return v

    @property
    def is_cartesian(self) -> bool:
        cdef Vec3 x_axis = v3_cross(self.get_uy(), self.get_uz())
        return v3_isclose(x_axis, self.get_ux(), REL_TOL, ABS_TOL)

    @property
    def is_orthogonal(self) -> bool:
        cdef Vec3 ux = v3_normalize(self.get_ux(), 1.0)
        cdef Vec3 uy = v3_normalize(self.get_uy(), 1.0)
        cdef Vec3 uz = v3_normalize(self.get_uz(), 1.0)
        return fabs(v3_dot(ux, uy)) < 1e-9 and \
               fabs(v3_dot(ux, uz)) < 1e-9 and \
               fabs(v3_dot(uy, uz)) < 1e-9

    @staticmethod
    def scale(double sx, sy = None, sz = None) -> 'Matrix44':
        cdef Matrix44 mat = Matrix44()
        mat.m[0] = sx
        mat.m[5] = sx if sy is None else sy
        mat.m[10] = sx if sz is None else sz
        return mat

    @staticmethod
    def translate(double dx, double dy, double dz) -> 'Matrix44':
        cdef Matrix44 mat = Matrix44()
        mat.m[12] = dx
        mat.m[13] = dy
        mat.m[14] = dz
        return mat

    @staticmethod
    def x_rotate(double angle) -> 'Matrix44':
        cdef Matrix44 mat = Matrix44()
        cdef double cos_a = cos(angle)
        cdef double sin_a = sin(angle)
        mat.m[5] = cos_a
        mat.m[6] = sin_a
        mat.m[9] = -sin_a
        mat.m[10] = cos_a
        return mat

    @staticmethod
    def y_rotate(double angle) -> 'Matrix44':
        cdef Matrix44 mat = Matrix44()
        cdef double cos_a = cos(angle)
        cdef double sin_a = sin(angle)
        mat.m[0] = cos_a
        mat.m[2] = -sin_a
        mat.m[8] = sin_a
        mat.m[10] = cos_a
        return mat

    @staticmethod
    def z_rotate(double angle) -> 'Matrix44':
        cdef Matrix44 mat = Matrix44()
        cdef double cos_a = cos(angle)
        cdef double sin_a = sin(angle)
        mat.m[0] = cos_a
        mat.m[1] = sin_a
        mat.m[4] = -sin_a
        mat.m[5] = cos_a
        return mat

    @staticmethod
    def axis_rotate(axis: 'Vertex', double angle) -> 'Matrix44':
        cdef Matrix44 mat = Matrix44()
        cdef double cos_a = cos(angle)
        cdef double sin_a = sin(angle)
        cdef double one_m_cos = 1.0 - cos_a
        cdef Vec3 _axis = Vec3(axis).normalize()
        cdef double x = _axis.x
        cdef double y = _axis.y
        cdef double z = _axis.z

        mat.m[0] = x * x * one_m_cos + cos_a
        mat.m[1] = y * x * one_m_cos + z * sin_a
        mat.m[2] = x * z * one_m_cos - y * sin_a

        mat.m[4] = x * y * one_m_cos - z * sin_a
        mat.m[5] = y * y * one_m_cos + cos_a
        mat.m[6] = y * z * one_m_cos + x * sin_a

        mat.m[8] = x * z * one_m_cos + y * sin_a
        mat.m[9] = y * z * one_m_cos - x * sin_a
        mat.m[10] = z * z * one_m_cos + cos_a

        return mat

    @staticmethod
    def xyz_rotate(double angle_x, double angle_y,
                   double angle_z) -> 'Matrix44':
        cdef Matrix44 mat = Matrix44()
        cdef double cx = cos(angle_x)
        cdef double sx = sin(angle_x)
        cdef double cy = cos(angle_y)
        cdef double sy = sin(angle_y)
        cdef double cz = cos(angle_z)
        cdef double sz = sin(angle_z)
        cdef double sxsy = sx * sy
        cdef double cxsy = cx * sy

        mat.m[0] = cy * cz
        mat.m[1] = sxsy * cz + cx * sz
        mat.m[2] = -cxsy * cz + sx * sz
        mat.m[4] = -cy * sz
        mat.m[5] = -sxsy * sz + cx * cz
        mat.m[6] = cxsy * sz + sx * cz
        mat.m[8] = sy
        mat.m[9] = -sx * cy
        mat.m[10] = cx * cy
        return mat

    @staticmethod
    def shear_xy(double angle_x = 0, double angle_y = 0) -> 'Matrix44':
        cdef Matrix44 mat = Matrix44()
        cdef double tx = tan(angle_x)
        cdef double ty = tan(angle_y)
        mat.m[1] = ty
        mat.m[4] = tx
        return mat

    @staticmethod
    def perspective_projection(double left, double right, double top,
                               double bottom, double near,
                               double far) -> 'Matrix44':
        cdef Matrix44 mat = Matrix44()
        mat.m[0] = (2. * near) / (right - left)
        mat.m[5] = (2. * near) / (top - bottom)
        mat.m[8] = (right + left) / (right - left)
        mat.m[9] = (top + bottom) / (top - bottom)
        mat.m[10] = -((far + near) / (far - near))
        mat.m[11] = -1
        mat.m[14] = -((2. * far * near) / (far - near))
        return mat

    @staticmethod
    def perspective_projection_fov(fov: float, aspect: float, near: float,
                                   far: float) -> 'Matrix44':
        vrange = near * math.tan(fov / 2.)
        left = -vrange * aspect
        right = vrange * aspect
        bottom = -vrange
        top = vrange
        return Matrix44.perspective_projection(left, right, bottom, top, near,
                                               far)

    @staticmethod
    def chain(*matrices: 'Matrix44') -> 'Matrix44':
        cdef Matrix44 transformation = Matrix44()
        for matrix in matrices:
            transformation *= matrix
        return transformation

    def __imul__(self, Matrix44 other) -> 'Matrix44':
        cdef double[16] m1 = self.m
        cdef double *m2 = other.m

        self.m[0] = m1[0] * m2[0] + m1[1] * m2[4] + m1[2] * m2[8] + \
                    m1[3] * m2[12]
        self.m[1] = m1[0] * m2[1] + m1[1] * m2[5] + m1[2] * m2[9] + \
                    m1[3] * m2[13]
        self.m[2] = m1[0] * m2[2] + m1[1] * m2[6] + m1[2] * m2[10] + \
                    m1[3] * m2[14]
        self.m[3] = m1[0] * m2[3] + m1[1] * m2[7] + m1[2] * m2[11] + \
                    m1[3] * m2[15]

        self.m[4] = m1[4] * m2[0] + m1[5] * m2[4] + m1[6] * m2[8] + \
                    m1[7] * m2[12]
        self.m[5] = m1[4] * m2[1] + m1[5] * m2[5] + m1[6] * m2[9] + \
                    m1[7] * m2[13]
        self.m[6] = m1[4] * m2[2] + m1[5] * m2[6] + m1[6] * m2[10] + \
                    m1[7] * m2[14]
        self.m[7] = m1[4] * m2[3] + m1[5] * m2[7] + m1[6] * m2[11] + \
                    m1[7] * m2[15]

        self.m[8] = m1[8] * m2[0] + m1[9] * m2[4] + m1[10] * m2[8] + \
                    m1[11] * m2[12]
        self.m[9] = m1[8] * m2[1] + m1[9] * m2[5] + m1[10] * m2[9] + \
                    m1[11] * m2[13]
        self.m[10] = m1[8] * m2[2] + m1[9] * m2[6] + m1[10] * m2[10] + \
                     m1[11] * m2[14]
        self.m[11] = m1[8] * m2[3] + m1[9] * m2[7] + m1[10] * m2[11] + \
                     m1[11] * m2[15]

        self.m[12] = m1[12] * m2[0] + m1[13] * m2[4] + m1[14] * m2[8] + \
                     m1[15] * m2[12]
        self.m[13] = m1[12] * m2[1] + m1[13] * m2[5] + m1[14] * m2[9] + \
                     m1[15] * m2[13]
        self.m[14] = m1[12] * m2[2] + m1[13] * m2[6] + m1[14] * m2[10] + \
                     m1[15] * m2[14]
        self.m[15] = m1[12] * m2[3] + m1[13] * m2[7] + m1[14] * m2[11] + \
                     m1[15] * m2[15]
        return self

    def __mul__(self, Matrix44 other) -> 'Matrix44':
        cdef Matrix44 res_matrix = self.copy()
        return res_matrix.__imul__(other)

    # __matmul__ = __mul__ does not work!

    def __matmul__(self, Matrix44 other) -> 'Matrix44':
        cdef Matrix44 res_matrix = self.copy()
        return res_matrix.__imul__(other)

    def transpose(self) -> None:
        swap(&self.m[1], &self.m[4])
        swap(&self.m[2], &self.m[8])
        swap(&self.m[3], &self.m[12])
        swap(&self.m[6], &self.m[9])
        swap(&self.m[7], &self.m[13])
        swap(&self.m[11], &self.m[14])

    def determinant(self) -> float:
        cdef double *m = self.m
        return m[0] * m[5] * m[10] * m[15] - m[0] * m[5] * m[11] * m[14] + \
               m[0] * m[6] * m[11] * m[13] - m[0] * m[6] * m[9] * m[15] + \
               m[0] * m[7] * m[9] * m[14] - m[0] * m[7] * m[10] * m[13] - \
               m[1] * m[6] * m[11] * m[12] + m[1] * m[6] * m[8] * m[15] - \
               m[1] * m[7] * m[8] * m[14] + m[1] * m[7] * m[10] * m[12] - \
               m[1] * m[4] * m[10] * m[15] + m[1] * m[4] * m[11] * m[14] + \
               m[2] * m[7] * m[8] * m[13] - m[2] * m[7] * m[9] * m[12] + \
               m[2] * m[4] * m[9] * m[15] - m[2] * m[4] * m[11] * m[13] + \
               m[2] * m[5] * m[11] * m[12] - m[2] * m[5] * m[8] * m[15] - \
               m[3] * m[4] * m[9] * m[14] + m[3] * m[4] * m[10] * m[13] - \
               m[3] * m[5] * m[10] * m[12] + m[3] * m[5] * m[8] * m[14] - \
               m[3] * m[6] * m[8] * m[13] + m[3] * m[6] * m[9] * m[12]

    def inverse(self) -> None:
        cdef double[16] m = self.m  # memcopy
        cdef double det = self.determinant()
        cdef double f = 1. / det
        self.m[0] = (m[6] * m[11] * m[13] - m[7] * m[10] * m[13] + m[7] * m[9] *
                     m[14] - m[5] * m[11] * m[14] - m[6] * m[9] * m[15] + m[5] *
                     m[10] * m[15]) * f

        self.m[1] = (m[3] * m[10] * m[13] - m[2] * m[11] * m[13] - m[3] * m[9] *
                     m[14] + m[1] * m[11] * m[14] + m[2] * m[9] * m[15] -
                     m[1] * m[10] * m[15]) * f
        self.m[2] = (m[2] * m[7] * m[13] - m[3] * m[6] * m[13] + m[3] * m[5] *
                     m[14] - m[1] * m[7] * m[14] - m[2] * m[5] * m[15] +
                     m[1] * m[6] * m[15]) * f

        self.m[3] = (m[3] * m[6] * m[9] - m[2] * m[7] * m[9] - m[3] * m[5] *
                     m[10] + m[1] * m[7] * m[10] + m[2] * m[5] * m[11] - m[1] *
                     m[6] * m[11]) * f

        self.m[4] = (m[7] * m[10] * m[12] - m[6] * m[11] * m[12] - m[7] * m[8] *
                     m[14] + m[4] * m[11] * m[14] + m[6] * m[8] * m[15] -
                     m[4] * m[10] * m[15]) * f

        self.m[5] = (m[2] * m[11] * m[12] - m[3] * m[10] * m[12] + m[3] * m[8] *
                     m[14] - m[0] * m[11] * m[14] - m[2] * m[8] * m[15] +
                     m[0] * m[10] * m[15]) * f

        self.m[6] = (m[3] * m[6] * m[12] - m[2] * m[7] * m[12] - m[3] * m[4] *
                     m[14] + m[0] * m[7] * m[14] + m[2] * m[4] * m[15] -
                     m[0] * m[6] * m[15]) * f

        self.m[7] = (m[2] * m[7] * m[8] - m[3] * m[6] * m[8] + m[3] * m[4] *
                     m[10] - m[0] * m[7] * m[10] - m[2] * m[4] * m[11] +
                     m[0] * m[6] * m[11]) * f

        self.m[8] = (m[5] * m[11] * m[12] - m[7] * m[9] * m[12] + m[7] * m[8] *
                     m[13] - m[4] * m[11] * m[13] - m[5] * m[8] * m[15] +
                     m[4] * m[9] * m[15]) * f

        self.m[9] = (m[3] * m[9] * m[12] - m[1] * m[11] * m[12] - m[3] *
                     m[8] * m[13] + m[0] * m[11] * m[13] + m[1] * m[8] *
                     m[15] - m[0] * m[9] * m[15]) * f

        self.m[10] = (m[1] * m[7] * m[12] - m[3] * m[5] * m[12] + m[3] *
                      m[4] * m[13] - m[0] * m[7] * m[13] - m[1] * m[4] *
                      m[15] + m[0] * m[5] * m[15]) * f

        self.m[11] = (m[3] * m[5] * m[8] - m[1] * m[7] * m[8] - m[3] * m[4] *
                      m[9] + m[0] * m[7] * m[9] + m[1] * m[4] * m[11] -
                      m[0] * m[5] * m[11]) * f

        self.m[12] = (m[6] * m[9] * m[12] - m[5] * m[10] * m[12] - m[6] *
                      m[8] * m[13] + m[4] * m[10] * m[13] + m[5] * m[8] *
                      m[14] - m[4] * m[9] * m[14]) * f

        self.m[13] = (m[1] * m[10] * m[12] - m[2] * m[9] * m[12] + m[2] *
                      m[8] * m[13] - m[0] * m[10] * m[13] - m[1] * m[8] *
                      m[14] + m[0] * m[9] * m[14]) * f

        self.m[14] = (m[2] * m[5] * m[12] - m[1] * m[6] * m[12] - m[2] *
                      m[4] * m[13] + m[0] * m[6] * m[13] + m[1] * m[4] *
                      m[14] - m[0] * m[5] * m[14]) * f

        self.m[15] = (m[1] * m[6] * m[8] - m[2] * m[5] * m[8] + m[2] * m[4] *
                      m[9] - m[0] * m[6] * m[9] - m[1] * m[4] * m[10] +
                      m[0] * m[5] * m[10]) * f

    @staticmethod
    def ucs(ux=X_AXIS, uy=Y_AXIS, uz=Z_AXIS, origin=NULLVEC) -> 'Matrix44':
        cdef Matrix44 mat = Matrix44()
        cdef Vec3 _ux = Vec3(ux)
        cdef Vec3 _uy = Vec3(uy)
        cdef Vec3 _uz = Vec3(uz)
        cdef Vec3 _origin = Vec3(origin)

        mat.m[0] = _ux.x
        mat.m[1] = _ux.y
        mat.m[2] = _ux.z

        mat.m[4] = _uy.x
        mat.m[5] = _uy.y
        mat.m[6] = _uy.z

        mat.m[8] = _uz.x
        mat.m[9] = _uz.y
        mat.m[10] = _uz.z

        mat.m[12] = _origin.x
        mat.m[13] = _origin.y
        mat.m[14] = _origin.z

        return mat

    def transform(self, vector: 'Vertex') -> Vec3:
        cdef Vec3 res = Vec3(vector)
        cdef double x = res.x
        cdef double y = res.y
        cdef double z = res.z
        cdef double *m = self.m

        res.x = x * m[0] + y * m[4] + z * m[8] + m[12]
        res.y = x * m[1] + y * m[5] + z * m[9] + m[13]
        res.z = x * m[2] + y * m[6] + z * m[10] + m[14]
        return res

    def transform_direction(self, vector: 'Vertex', normalize=False) -> Vec3:
        cdef Vec3 res = Vec3(vector)
        cdef double x = res.x
        cdef double y = res.y
        cdef double z = res.z
        cdef double *m = self.m

        res.x = x * m[0] + y * m[4] + z * m[8]
        res.y = x * m[1] + y * m[5] + z * m[9]
        res.z = x * m[2] + y * m[6] + z * m[10]
        if normalize:
            return v3_normalize(res, 1.0)
        else:
            return res

    ocs_to_wcs = transform_direction

    def transform_vertices(self, vectors: Iterable['Vertex']) -> Iterable[Vec3]:
        cdef double *m = self.m
        cdef Vec3 res
        cdef double x, y, z

        for vector in vectors:
            res = Vec3(vector)
            x = res.x
            y = res.y
            z = res.z

            res.x = x * m[0] + y * m[4] + z * m[8] + m[12]
            res.y = x * m[1] + y * m[5] + z * m[9] + m[13]
            res.z = x * m[2] + y * m[6] + z * m[10] + m[14]
            yield res

    def transform_directions(self, vectors: Iterable['Vertex'],
                             normalize=False) -> Iterable[Vec3]:
        cdef double *m = self.m
        cdef Vec3 res
        cdef double x, y, z
        cdef bint _normalize = normalize

        for vector in vectors:
            res = Vec3(vector)
            x = res.x
            y = res.y
            z = res.z

            res.x = x * m[0] + y * m[4] + z * m[8]
            res.y = x * m[1] + y * m[5] + z * m[9]
            res.z = x * m[2] + y * m[6] + z * m[10]
            yield v3_normalize(res, 1.0) if _normalize else res

    def ucs_vertex_from_wcs(self, wcs: Vec3) -> Vec3:
        return self.ucs_direction_from_wcs(wcs - self.origin)

    def ucs_direction_from_wcs(self, wcs: 'Vertex') -> Vec3:
        cdef double *m = self.m
        cdef Vec3 res = Vec3(wcs)
        cdef double x = res.x
        cdef double y = res.y
        cdef double z = res.z

        res.x = x * m[0] + y * m[1] + z * m[2]
        res.y = x * m[4] + y * m[5] + z * m[6]
        res.z = x * m[8] + y * m[9] + z * m[10]
        return res

    ocs_from_wcs = ucs_direction_from_wcs
