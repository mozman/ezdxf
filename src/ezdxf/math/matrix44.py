# original code from package: gameobjects
# Home-page: http://code.google.com/p/gameobjects/
# Author: Will McGugan
# Download-URL: http://code.google.com/p/gameobjects/downloads/list
# Created: 19.04.2010
# Copyright (c) 2010-2020 Manfred Moitzi
# License: MIT License
from typing import Sequence, Iterable, List, Tuple, TYPE_CHECKING
import math
from math import sin, cos, tan
from itertools import chain
from .vector import Vector, X_AXIS, Y_AXIS, Z_AXIS, NULLVEC

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex

__all__ = ['Matrix44']


# removed array.array because array is optimized for space not speed, and space optimization is not needed

def floats(items: Iterable) -> List[float]:
    return [float(v) for v in items]


class Matrix44:
    """
    This is a pure Python implementation for 4x4 transformation matrices, to avoid dependency to big numerical packages
    like :mod:`numpy`, before binary wheels, installation of these packages wasn't always easy on Windows.

    The utility functions for constructing transformations and transforming vectors and points assumes that vectors
    are stored as row vectors, meaning when multiplied, transformations are applied left to right
    (e.g. vAB transforms v by A then by B).

    Matrix44 initialization:

        - ``Matrix44()`` returns the identity matrix.
        - ``Matrix44(values)`` values is an iterable with the 16 components of the matrix.
        - ``Matrix44(row1, row2, row3, row4)`` four rows, each row with four values.

    """
    _identity = (
        1.0, 0.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        0.0, 0.0, 0.0, 1.0
    )
    __slots__ = ('matrix',)

    def __init__(self, *args):
        """
        Matrix44() is the identity matrix.

        Matrix44(values) values is an iterable with the 16 components of the matrix.

        Matrix44(row1, row2, row3, row4) four rows, each row with four values.

        """
        self.matrix: List[float] = None
        self.set(*args)

    def set(self, *args) -> None:
        """
        Set matrix values.

            - ``set()`` creates the identity matrix.
            - ``set(values)`` values is an iterable with the 16 components of the matrix.
            - ``set(row1, row2, row3, row4)`` four rows, each row with four values.

        """
        nargs = len(args)
        if nargs == 0:
            self.matrix = floats(Matrix44._identity)
        elif nargs == 1:
            self.matrix = floats(args[0])
        elif nargs == 4:
            self.matrix = floats(chain(*args))
        else:
            raise ValueError("Invalid count of arguments (4 row vectors or one list with 16 values).")
        if len(self.matrix) != 16:
            raise ValueError("Invalid matrix count")

    def __repr__(self) -> str:
        """ Returns the representation string of the matrix:
        ``Matrix44((col0, col1, col2, col3), (...), (...), (...))``
        """

        def format_row(row):
            return "(%s)" % ", ".join(str(value) for value in row)

        return "Matrix44(%s)" % \
               ", ".join(format_row(row) for row in self.rows())

    def get_2d_transformation(self) -> Tuple[float, ...]:
        """ Returns a the 2D transformation as a row-major matrix in a linear array (tuple).

        A more correct transformation could be implemented like so:
        https://stackoverflow.com/questions/10629737/convert-3d-4x4-rotation-matrix-into-2d
        """
        m = self.matrix
        return m[0], m[1], 0.0, m[4], m[5], 0.0, m[12], m[13], 1.0

    def get_row(self, row: int) -> Tuple[float, ...]:
        """ Get row as list of of four float values.

        Args:
            row: row index [0 .. 3]

        """
        index = row * 4
        return tuple(self.matrix[index:index + 4])

    def set_row(self, row: int, values: Sequence[float]) -> None:
        """
        Sets the values in a row.

        Args:
            row: row index [0 .. 3]
            values: iterable of four row values

        """
        index = row * 4
        self.matrix[index:index + len(values)] = floats(values)

    def get_col(self, col: int) -> Tuple[float, ...]:
        """
        Returns a column as a tuple of four floats.

        Args:
            col: column index [0 .. 3]
        """
        m = self.matrix
        return m[col], m[col + 4], m[col + 8], m[col + 12]

    def set_col(self, col: int, values: Sequence[float]):
        """
        Sets the values in a column.

        Args:
            col: column index [0 .. 3]
            values: iterable of four column values

        """
        m = self.matrix
        a, b, c, d = values
        m[col] = float(a)
        m[col + 4] = float(b)
        m[col + 8] = float(c)
        m[col + 12] = float(d)

    def copy(self) -> 'Matrix44':
        """ Returns a copy of same type. """
        return self.__class__(self.matrix)

    __copy__ = copy

    @property
    def origin(self) -> Vector:
        m = self.matrix
        return Vector(m[12], m[13], m[14])

    @origin.setter
    def origin(self, v: 'Vertex') -> None:
        m = self.matrix
        m[12], m[13], m[14] = Vector(v)

    @property
    def ux(self) -> Vector:
        return Vector(self.matrix[0:3])

    @property
    def uy(self) -> Vector:
        return Vector(self.matrix[4:7])

    @property
    def uz(self) -> Vector:
        return Vector(self.matrix[8:11])

    @property
    def is_cartesian(self) -> bool:
        """ Returns ``True`` if target coordinate system is a right handed orthogonal coordinate system. """
        return self.uy.cross(self.uz).normalize().isclose(self.ux.normalize())

    @property
    def is_orthogonal(self) -> bool:
        """ Returns ``True`` if target coordinate system has orthogonal axis.

        Does not check for left- or right handed orientation, any orientation of the axis valid.

        """
        ux = self.ux.normalize()
        uy = self.uy.normalize()
        uz = self.uz.normalize()
        return math.isclose(ux.dot(uy), 0.0, abs_tol=1e-9) and \
               math.isclose(ux.dot(uz), 0.0, abs_tol=1e-9) and \
               math.isclose(uy.dot(uz), 0.0, abs_tol=1e-9)

    @classmethod
    def scale(cls, sx: float, sy: float = None, sz: float = None) -> 'Matrix44':
        """
        Returns a scaling transformation matrix. If `sy` is ``None``, `sy` = `sx`, and if `sz` is ``None`` `sz` = `sx`.

        """
        if sy is None:
            sy = sx
        if sz is None:
            sz = sx

        m = cls([
            float(sx), 0., 0., 0.,
            0., float(sy), 0., 0.,
            0., 0., float(sz), 0.,
            0., 0., 0., 1.
        ])
        return m

    @classmethod
    def translate(cls, dx: float, dy: float, dz: float) -> 'Matrix44':
        """ Returns a translation matrix for translation vector (dx, dy, dz). """
        return cls([
            1., 0., 0., 0.,
            0., 1., 0., 0.,
            0., 0., 1., 0.,
            float(dx), float(dy), float(dz), 1.
        ])

    @classmethod
    def x_rotate(cls, angle: float) -> 'Matrix44':
        """
        Returns a rotation matrix about the x-axis.

        Args:
            angle: rotation angle in radians

        """
        cos_a = cos(angle)
        sin_a = sin(angle)
        return cls([
            1., 0., 0., 0.,
            0., cos_a, sin_a, 0.,
            0., -sin_a, cos_a, 0.,
            0., 0., 0., 1.
        ])

    @classmethod
    def y_rotate(cls, angle: float) -> 'Matrix44':
        """
        Returns a rotation matrix about the y-axis.

        Args:
            angle: rotation angle in radians

        """
        cos_a = cos(angle)
        sin_a = sin(angle)
        return cls([
            cos_a, 0., -sin_a, 0.,
            0., 1., 0., 0.,
            sin_a, 0., cos_a, 0.,
            0., 0., 0., 1.
        ])

    @classmethod
    def z_rotate(cls, angle: float) -> 'Matrix44':
        """
        Returns a rotation matrix about the z-axis.

        Args:
            angle: rotation angle in radians

        """
        cos_a = cos(angle)
        sin_a = sin(angle)
        return cls([
            cos_a, sin_a, 0., 0.,
            -sin_a, cos_a, 0., 0.,
            0., 0., 1., 0.,
            0., 0., 0., 1.
        ])

    @classmethod
    def axis_rotate(cls, axis: 'Vertex', angle: float) -> 'Matrix44':
        """
        Returns a rotation matrix about an arbitrary `axis`.

        Args:
            axis: rotation axis as ``(x, y, z)`` tuple or :class:`Vector` object
            angle: rotation angle in radians

        """
        c = cos(angle)
        s = sin(angle)
        omc = 1. - c
        x, y, z = axis
        return cls([
            x * x * omc + c, y * x * omc + z * s, x * z * omc - y * s, 0.,
            x * y * omc - z * s, y * y * omc + c, y * z * omc + x * s, 0.,
            x * z * omc + y * s, y * z * omc - x * s, z * z * omc + c, 0.,
            0., 0., 0., 1.
        ])

    @classmethod
    def xyz_rotate(cls, angle_x: float, angle_y: float, angle_z: float) -> 'Matrix44':
        """
        Returns a rotation matrix for rotation about each axis.

        Args:
            angle_x: rotation angle about x-axis in radians
            angle_y: rotation angle about y-axis in radians
            angle_z: rotation angle about z-axis in radians

        """
        cx = cos(angle_x)
        sx = sin(angle_x)
        cy = cos(angle_y)
        sy = sin(angle_y)
        cz = cos(angle_z)
        sz = sin(angle_z)

        sxsy = sx * sy
        cxsy = cx * sy

        return cls([
            cy * cz, sxsy * cz + cx * sz, -cxsy * cz + sx * sz, 0.,
            -cy * sz, -sxsy * sz + cx * cz, cxsy * sz + sx * cz, 0.,
            sy, -sx * cy, cx * cy, 0.,
            0., 0., 0., 1.])

    @classmethod
    def perspective_projection(cls, left: float, right: float, top: float, bottom: float, near: float,
                               far: float) -> 'Matrix44':
        """
        Returns a matrix for a 2D projection.

        Args:
            left: Coordinate of left of screen
            right: Coordinate of right of screen
            top: Coordinate of the top of the screen
            bottom: Coordinate of the bottom of the screen
            near: Coordinate of the near clipping plane
            far: Coordinate of the far clipping plane

        """
        return cls([
            (2. * near) / (right - left), 0., 0., 0.,
            0., (2. * near) / (top - bottom), 0., 0.,
            (right + left) / (right - left), (top + bottom) / (top - bottom), -((far + near) / (far - near)), -1.,
            0., 0., -((2. * far * near) / (far - near)), 0.
        ])

    @classmethod
    def perspective_projection_fov(cls, fov: float, aspect: float, near: float, far: float) -> 'Matrix44':
        """
        Returns a matrix for a 2D projection.

        Args:
            fov: The field of view (in radians)
            aspect: The aspect ratio of the screen (width / height)
            near: Coordinate of the near clipping plane
            far: Coordinate of the far clipping plane

        """
        vrange = near * tan(fov / 2.)
        left = -vrange * aspect
        right = vrange * aspect
        bottom = -vrange
        top = vrange
        return cls.perspective_projection(left, right, bottom, top, near, far)

    @staticmethod
    def chain(*matrices: 'Matrix44') -> 'Matrix44':
        """ Compose a transformation matrix from one or more `matrices`. """
        transformation = Matrix44()
        for matrix in matrices:
            transformation *= matrix
        return transformation

    @staticmethod
    def ucs(ux=X_AXIS, uy=Y_AXIS, uz=Z_AXIS, origin=NULLVEC) -> 'Matrix44':
        """
        Returns a matrix for coordinate transformation from WCS to UCS.
        For transformation from UCS to WCS, transpose the returned matrix.

        Args:
            ux: x-axis for UCS as unit vector
            uy: y-axis for UCS as unit vector
            uz: z-axis for UCS as unit vector
            origin: UCS origin as location vector

        """
        ux_x, ux_y, ux_z = ux
        uy_x, uy_y, uy_z = uy
        uz_x, uz_y, uz_z = uz
        or_x, or_y, or_z = origin
        return Matrix44((
            ux_x, ux_y, ux_z, 0,
            uy_x, uy_y, uy_z, 0,
            uz_x, uz_y, uz_z, 0,
            or_x, or_y, or_z, 1,
        ))

    def __hash__(self) -> int:
        """ Returns hash value of matrix. """
        return self.matrix.__hash__()

    def __setitem__(self, index: Tuple[int, int], value: float):
        """ Set (row, column) element. """
        row, col = index
        self.matrix[row * 4 + col] = float(value)

    def __getitem__(self, index: Tuple[int, int]):
        """ Get (row, column) element. """
        row, col = index
        return self.matrix[row * 4 + col]

    def __iter__(self) -> Iterable[float]:
        """ Iterates over all matrix values. """
        return iter(self.matrix)

    def __matmul__(self, other: 'Matrix44') -> 'Matrix44':
        res_matrix = self.copy()
        res_matrix.__imul__(other)
        return res_matrix

    def __mul__(self, other: 'Matrix44') -> 'Matrix44':
        """ Returns a new matrix as result of the matrix multiplication with another matrix. """
        res_matrix = self.copy()
        res_matrix.__imul__(other)
        return res_matrix

    def __imul__(self, other: 'Matrix44') -> 'Matrix44':
        """ Inplace multiplication with another matrix. """
        m1 = self.matrix
        m2 = other.matrix
        self.matrix = [
            m1[0] * m2[0] + m1[1] * m2[4] + m1[2] * m2[8] + m1[3] * m2[12],
            m1[0] * m2[1] + m1[1] * m2[5] + m1[2] * m2[9] + m1[3] * m2[13],
            m1[0] * m2[2] + m1[1] * m2[6] + m1[2] * m2[10] + m1[3] * m2[14],
            m1[0] * m2[3] + m1[1] * m2[7] + m1[2] * m2[11] + m1[3] * m2[15],

            m1[4] * m2[0] + m1[5] * m2[4] + m1[6] * m2[8] + m1[7] * m2[12],
            m1[4] * m2[1] + m1[5] * m2[5] + m1[6] * m2[9] + m1[7] * m2[13],
            m1[4] * m2[2] + m1[5] * m2[6] + m1[6] * m2[10] + m1[7] * m2[14],
            m1[4] * m2[3] + m1[5] * m2[7] + m1[6] * m2[11] + m1[7] * m2[15],

            m1[8] * m2[0] + m1[9] * m2[4] + m1[10] * m2[8] + m1[11] * m2[12],
            m1[8] * m2[1] + m1[9] * m2[5] + m1[10] * m2[9] + m1[11] * m2[13],
            m1[8] * m2[2] + m1[9] * m2[6] + m1[10] * m2[10] + m1[11] * m2[14],
            m1[8] * m2[3] + m1[9] * m2[7] + m1[10] * m2[11] + m1[11] * m2[15],

            m1[12] * m2[0] + m1[13] * m2[4] + m1[14] * m2[8] + m1[15] * m2[12],
            m1[12] * m2[1] + m1[13] * m2[5] + m1[14] * m2[9] + m1[15] * m2[13],
            m1[12] * m2[2] + m1[13] * m2[6] + m1[14] * m2[10] + m1[15] * m2[14],
            m1[12] * m2[3] + m1[13] * m2[7] + m1[14] * m2[11] + m1[15] * m2[15]
        ]
        return self

    def fast_mul(self, other: 'Matrix44') -> 'Matrix44':
        """
        Multiplies this matrix with other matrix.

        Assumes that both matrices have a right column of (0, 0, 0, 1). This is True for matrices composed of
        rotations,  translations and scales. fast_mul is approximately 25% quicker than the ``*=`` operator.

        """
        m1 = self.matrix
        m2 = other.matrix
        self.matrix = [
            m1[0] * m2[0] + m1[1] * m2[4] + m1[2] * m2[8],
            m1[0] * m2[1] + m1[1] * m2[5] + m1[2] * m2[9],
            m1[0] * m2[2] + m1[1] * m2[6] + m1[2] * m2[10],
            0.0,

            m1[4] * m2[0] + m1[5] * m2[4] + m1[6] * m2[8],
            m1[4] * m2[1] + m1[5] * m2[5] + m1[6] * m2[9],
            m1[4] * m2[2] + m1[5] * m2[6] + m1[6] * m2[10],
            0.0,

            m1[8] * m2[0] + m1[9] * m2[4] + m1[10] * m2[8],
            m1[8] * m2[1] + m1[9] * m2[5] + m1[10] * m2[9],
            m1[8] * m2[2] + m1[9] * m2[6] + m1[10] * m2[10],
            0.0,

            m1[12] * m2[0] + m1[13] * m2[4] + m1[14] * m2[8] + m2[12],
            m1[12] * m2[1] + m1[13] * m2[5] + m1[14] * m2[9] + m2[13],
            m1[12] * m2[2] + m1[13] * m2[6] + m1[14] * m2[10] + m2[14],
            1.0
        ]
        return self

    def rows(self) -> Iterable[Tuple[float, ...]]:
        """ Iterate over rows as 4-tuples. """
        return (self.get_row(index) for index in (0, 1, 2, 3))

    def columns(self) -> Iterable[Tuple[float, ...]]:
        """ Iterate over columns as 4-tuples. """
        return (self.get_col(index) for index in (0, 1, 2, 3))

    def transform(self, vector: 'Vertex') -> Vector:
        """ Returns a transformed vertex. """
        m = self.matrix
        x, y, z = vector
        return Vector(x * m[0] + y * m[4] + z * m[8] + m[12],
                      x * m[1] + y * m[5] + z * m[9] + m[13],
                      x * m[2] + y * m[6] + z * m[10] + m[14])

    def transform_direction(self, vector: 'Vertex', normalize=False) -> Vector:
        """ Returns a transformed direction vector without translation. """
        m = self.matrix
        x, y, z = vector
        v = Vector(x * m[0] + y * m[4] + z * m[8],
                   x * m[1] + y * m[5] + z * m[9],
                   x * m[2] + y * m[6] + z * m[10])
        return v.normalize() if normalize else v

    ocs_to_wcs = transform_direction

    def transform_vertices(self, vectors: Iterable['Vertex']) -> Iterable[Vector]:
        """ Returns an iterable of transformed vertices. """
        m0, m1, m2, m3, m4, m5, m6, m7, m8, m9, m10, m11, m12, m13, m14, m15 = self.matrix
        for vector in vectors:
            x, y, z = vector
            yield Vector(
                x * m0 + y * m4 + z * m8 + m12,
                x * m1 + y * m5 + z * m9 + m13,
                x * m2 + y * m6 + z * m10 + m14
            )

    def transform_directions(self, vectors: Iterable['Vertex'], normalize=False) -> Iterable[Vector]:
        """
        Returns an iterable of transformed direction vectors without translation.

        """
        m0, m1, m2, m3, m4, m5, m6, m7, m8, m9, m10, *_ = self.matrix
        for vector in vectors:
            x, y, z = vector
            v = Vector(
                x * m0 + y * m4 + z * m8,
                x * m1 + y * m5 + z * m9,
                x * m2 + y * m6 + z * m10
            )
            yield v.normalize() if normalize else v

    def ucs_vertex_from_wcs(self, wcs: Vector) -> Vector:
        """
        Returns an UCS vector from WCS vertex.

        Works only if matrix is used as cartesian UCS without scaling.

        (internal API)

        """
        return self.ucs_direction_from_wcs(wcs - self.origin)

    def ucs_direction_from_wcs(self, wcs: Vector) -> Vector:
        """
        Returns UCS direction vector from WCS direction.

        Works only if matrix is used as cartesian UCS without scaling.

        (internal API)

        """
        m0, m1, m2, m3, m4, m5, m6, m7, m8, m9, m10, *_ = self.matrix
        x, y, z = wcs
        return Vector(
            x * m0 + y * m1 + z * m2,
            x * m4 + y * m5 + z * m6,
            x * m8 + y * m9 + z * m10,
        )

    ocs_from_wcs = ucs_direction_from_wcs

    def transpose(self) -> None:
        """ Swaps the rows for columns inplace. """
        m00, m01, m02, m03, \
        m10, m11, m12, m13, \
        m20, m21, m22, m23, \
        m30, m31, m32, m33 = self.matrix

        self.matrix = [
            m00, m10, m20, m30,
            m01, m11, m21, m31,
            m02, m12, m22, m32,
            m03, m13, m23, m33
        ]

    def determinant(self) -> float:
        """ Returns determinant. """
        m00, m01, m02, m03, \
        m10, m11, m12, m13, \
        m20, m21, m22, m23, \
        m30, m31, m32, m33 = self.matrix
        return m00 * m11 * m22 * m33 - m00 * m11 * m23 * m32 + \
               m00 * m12 * m23 * m31 - m00 * m12 * m21 * m33 + \
               m00 * m13 * m21 * m32 - m00 * m13 * m22 * m31 - \
               m01 * m12 * m23 * m30 + m01 * m12 * m20 * m33 - \
               m01 * m13 * m20 * m32 + m01 * m13 * m22 * m30 - \
               m01 * m10 * m22 * m33 + m01 * m10 * m23 * m32 + \
               m02 * m13 * m20 * m31 - m02 * m13 * m21 * m30 + \
               m02 * m10 * m21 * m33 - m02 * m10 * m23 * m31 + \
               m02 * m11 * m23 * m30 - m02 * m11 * m20 * m33 - \
               m03 * m10 * m21 * m32 + m03 * m10 * m22 * m31 - \
               m03 * m11 * m22 * m30 + m03 * m11 * m20 * m32 - \
               m03 * m12 * m20 * m31 + m03 * m12 * m21 * m30

    def inverse(self) -> None:
        """
        Calculates the inverse of the matrix.

        Raises:
             ZeroDivisionError: if matrix has no inverse.

        """
        det = self.determinant()
        f = 1. / det  # catch ZeroDivisionError by caller
        m00, m01, m02, m03, \
        m10, m11, m12, m13, \
        m20, m21, m22, m23, \
        m30, m31, m32, m33 = self.matrix
        self.matrix = [
            (m12 * m23 * m31 - m13 * m22 * m31 + m13 * m21 * m32 - m11 * m23 * m32 - m12 * m21 * m33 +
             m11 * m22 * m33) * f,
            (m03 * m22 * m31 - m02 * m23 * m31 - m03 * m21 * m32 + m01 * m23 * m32 + m02 * m21 * m33 -
             m01 * m22 * m33) * f,
            (m02 * m13 * m31 - m03 * m12 * m31 + m03 * m11 * m32 - m01 * m13 * m32 - m02 * m11 * m33 +
             m01 * m12 * m33) * f,
            (m03 * m12 * m21 - m02 * m13 * m21 - m03 * m11 * m22 + m01 * m13 * m22 + m02 * m11 * m23 -
             m01 * m12 * m23) * f,
            (m13 * m22 * m30 - m12 * m23 * m30 - m13 * m20 * m32 + m10 * m23 * m32 + m12 * m20 * m33 -
             m10 * m22 * m33) * f,
            (m02 * m23 * m30 - m03 * m22 * m30 + m03 * m20 * m32 - m00 * m23 * m32 - m02 * m20 * m33 +
             m00 * m22 * m33) * f,
            (m03 * m12 * m30 - m02 * m13 * m30 - m03 * m10 * m32 + m00 * m13 * m32 + m02 * m10 * m33 -
             m00 * m12 * m33) * f,
            (m02 * m13 * m20 - m03 * m12 * m20 + m03 * m10 * m22 - m00 * m13 * m22 - m02 * m10 * m23 +
             m00 * m12 * m23) * f,
            (m11 * m23 * m30 - m13 * m21 * m30 + m13 * m20 * m31 - m10 * m23 * m31 - m11 * m20 * m33 +
             m10 * m21 * m33) * f,
            (m03 * m21 * m30 - m01 * m23 * m30 - m03 * m20 * m31 + m00 * m23 * m31 + m01 * m20 * m33 -
             m00 * m21 * m33) * f,
            (m01 * m13 * m30 - m03 * m11 * m30 + m03 * m10 * m31 - m00 * m13 * m31 - m01 * m10 * m33 +
             m00 * m11 * m33) * f,
            (m03 * m11 * m20 - m01 * m13 * m20 - m03 * m10 * m21 + m00 * m13 * m21 + m01 * m10 * m23 -
             m00 * m11 * m23) * f,
            (m12 * m21 * m30 - m11 * m22 * m30 - m12 * m20 * m31 + m10 * m22 * m31 + m11 * m20 * m32 -
             m10 * m21 * m32) * f,
            (m01 * m22 * m30 - m02 * m21 * m30 + m02 * m20 * m31 - m00 * m22 * m31 - m01 * m20 * m32 +
             m00 * m21 * m32) * f,
            (m02 * m11 * m30 - m01 * m12 * m30 - m02 * m10 * m31 + m00 * m12 * m31 + m01 * m10 * m32 -
             m00 * m11 * m32) * f,
            (m01 * m12 * m20 - m02 * m11 * m20 + m02 * m10 * m21 - m00 * m12 * m21 - m01 * m10 * m22 +
             m00 * m11 * m22) * f,
        ]
