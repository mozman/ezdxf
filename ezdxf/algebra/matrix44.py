# original code from package: gameobjects
# Home-page: http://code.google.com/p/gameobjects/
# Author: Will McGugan
# Download-URL: http://code.google.com/p/gameobjects/downloads/list
# Adaptation for package geoalg (ezdxf), API is not compatible to gameobjects.Matrix44
# Author: mozman
# Created: 19.04.2010
# Purpose: 4x4 matrix math
# module belongs to package ezdxf
# License: MIT License

from math import sin, cos, tan
from array import array


class Matrix44(object):
    _identity = (
        1.0, 0.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        0.0, 0.0, 0.0, 1.0
    )
    __slots__ = ('matrix',)

    def __init__(self, *args):
        """
        If no parameteres are given, the Matrix44 is initialised to identity.

        If 1 parameter is given it should be an iterable with the 16 components
        of the matrix.

        If 4 parameters are given they should be 4 sequences of up to 4 values.
        Missing values in each row are padded out with values from the identity matrix
        (so you can use Vector3's or tuples of 3 values).

        """
        self.matrix = array('d', Matrix44._identity)
        nargs = len(args)
        if nargs == 0:
            return
        elif nargs == 1:
            self.matrix = array('d', args[0])
        elif nargs == 4:
            for index, row in enumerate(args):
                self.set_row(index, row)
        else:
            raise ValueError("Invalid count of arguments (4 row vectors or one list with 16 values).")

    def __repr__(self):
        def format_row(row):
            return "(%s)" % ", ".join(str(value) for value in row )
        return "Matrix44(%s)" % \
               ", ".join(format_row(row) for row in self.rows())

    def get_row(self, row):
        index = row * 4
        return tuple(self.matrix[index:index+4])

    def set_row(self, row, values):
        index = row * 4
        self.matrix[index:index+len(values)] = array('d', values)

    def get_col(self, col):
        """Returns a column as a tuple of 4 values."""
        m = self.matrix
        return m[col], m[col+4], m[col+8], m[col+12]

    def set_col(self, col, values):
        """Sets the values in a column."""
        m = self.matrix
        a, b, c, d = values
        m[col] = float(a)
        m[col + 4] = float(b)
        m[col + 8] = float(c)
        m[col + 12] = float(d)

    def set(self, row0, row1, row2, row3):
        """
        Sets all four rows of the matrix.
        """
        for index, row in enumerate((row0, row1, row2, row3)):
            self.set_row(index, row)

    @classmethod
    def from_iter(cls, iterable):
        """
        Creates a Matrix44 from an iterable of 16 values.
        """
        matrix = cls()
        matrix.matrix = array('d', iterable)
        if len(matrix.matrix) != 16:
            raise ValueError("Iterable must have 16 values")
        return matrix

    def copy(self):
        return self.from_iter(self.matrix)
    __copy__ = copy

    @classmethod
    def identity(cls):
        """
        Creates and identity Matrix44.
        """
        return Matrix44()

    @classmethod
    def scale(cls, scale_x, scale_y=None, scale_z=None):
        """
        Creates a scale Matrix44.

        If one parameter is given the scale is uniform, if three parameters are give the scale is different (potentialy)
        on each x axis.
        """
        if scale_y is None:
            scale_y = scale_x
        if scale_z is None:
            scale_z = scale_x

        return cls.from_iter([
            float(scale_x), 0., 0., 0.,
            0., float(scale_y), 0., 0.,
            0., 0., float(scale_z), 0.,
            0., 0., 0., 1.
        ])

    @classmethod
    def translate(cls, x, y, z):
        """
        Creates a translation Matrix44 to (x, y, z).
        """
        return cls.from_iter([
            1., 0., 0., 0.,
            0., 1., 0., 0.,
            0., 0., 1., 0.,
            float(x), float(y), float(z), 1.
        ])

    @classmethod
    def x_rotate(cls, angle):
        """
        Creates a Matrix44 that does a rotation about the x axis.

        angle -- Angle of rotation (in radians)

        """
        cos_a = cos(angle)
        sin_a = sin(angle)
        return cls.from_iter([
            1., 0., 0., 0.,
            0., cos_a, sin_a, 0.,
            0., -sin_a, cos_a, 0.,
            0., 0., 0., 1.
        ])

    @classmethod
    def y_rotate(cls, angle):
        """
        Creates a Matrix44 that does a rotation about the y axis.

        angle -- Angle of rotation (in radians)

        """
        cos_a = cos(angle)
        sin_a = sin(angle)
        return cls.from_iter([
            cos_a, 0., -sin_a, 0.,
            0., 1., 0., 0.,
            sin_a, 0., cos_a, 0.,
            0., 0., 0., 1.
        ])

    @classmethod
    def z_rotate(cls, angle):
        """
        Creates a Matrix44 that does a rotation about the z axis.

        angle -- Angle of rotation (in radians)

        """
        cos_a = cos(angle)
        sin_a = sin(angle)
        return cls.from_iter([
            cos_a, sin_a, 0., 0.,
            -sin_a, cos_a, 0., 0.,
            0., 0., 1., 0.,
            0., 0., 0., 1.
        ])

    @classmethod
    def axis_rotate(cls, axis, angle):
        """
        Creates a Matrix44 that does a rotation about an axis.

        axis -- A vector of the axis
        angle -- Angle of rotation

        """
        c = cos(angle)
        s = sin(angle)
        omc = 1. - c
        x, y, z = axis
        return cls.from_iter([
            x*x*omc+c, y*x*omc+z*s, x*z*omc-y*s, 0.,
            x*y*omc-z*s, y*y*omc+c, y*z*omc+x*s, 0.,
            x*z*omc+y*s, y*z*omc-x*s, z*z*omc+c, 0.,
            0., 0., 0., 1.
        ])

    @classmethod
    def xyz_rotate(cls, angle_x, angle_y, angle_z):
        """
        Creates a Matrix44 that does a rotation about each axis.

        angle_x -- Angle of rotation, about x
        angle_y -- Angle of rotation, about y
        angle_z -- Angle of rotation, about z

        """
        cx = cos(angle_x)
        sx = sin(angle_x)
        cy = cos(angle_y)
        sy = sin(angle_y)
        cz = cos(angle_z)
        sz = sin(angle_z)

        sxsy = sx*sy
        cxsy = cx*sy

        return cls.from_iter([
            cy*cz, sxsy*cz+cx*sz, -cxsy*cz+sx*sz, 0.,
            -cy*sz, -sxsy*sz+cx*cz, cxsy*sz+sx*cz, 0.,
            sy, -sx*cy, cx*cy, 0.,
            0., 0., 0., 1.])

    @classmethod
    def perspective_projection(cls, left, right, top, bottom, near, far):
        """
        Creates a Matrix44 that projects points in to 2d space.

        left -- Coordinate of left of screen
        right -- Coordination of right of screen
        top -- Coordination of the top of the screen
        bottom -- Coordination of the borrom of the screen
        near -- Coordination of the near clipping plane
        far -- Coordinate of the far clipping plane

        """
        return cls.from_iter([
            (2.*near)/(right-left), 0., 0., 0.,
            0., (2.*near)/(top-bottom), 0., 0.,
            (right+left)/(right-left), (top+bottom)/(top-bottom), -((far+near)/(far-near)), -1.,
            0., 0., -((2.*far*near)/(far-near)), 0.
        ])

    @classmethod
    def perspective_projection_fov(cls, fov, aspect, near, far):
        """
        Creates a Matrix44 that projects points in to 2d space

        fov -- The field of view (in radians)
        aspect -- The aspect ratio of the screen (width / height)
        near -- Coordinate of the near clipping plane
        far -- Coordinate of the far clipping plane

        """
        vrange = near*tan(fov/2.)
        left = -vrange*aspect
        right = vrange*aspect
        bottom = -vrange
        top = vrange
        return cls.perspective_projection(left, right, bottom, top, near, far)

    @staticmethod
    def chain(*matrices):
        """
        Compose a transformation matrix from <*matrices>.
        """
        transformation = Matrix44()
        for matrix in matrices:
            transformation *= matrix
        return transformation

    def __hash__(self):
        """
        Allows matrices to be used as keys in a dictionary.
        """
        return self.matrix.__hash__()

    def __setitem__(self, coord, value):
        """
        Set element in the Matrix44.

        <coord> is a tuple of (row, column)

        """
        row, col = coord
        self.matrix[row * 4 + col] = float(value)

    def __getitem__(self, coord):
        """
        Get element in the Matrix44.

        <coord> is a tuple of (row, column)

        """
        row, col = coord
        return self.matrix[row * 4 + col]

    def __iter__(self):
        """
        Iterates over all 16 values in the Matrix44.
        """
        return iter(self.matrix)

    def __mul__(self, other):
        """
        Returns the result of multiplying this Matrix44 by another, called by the * (multiply) operator.
        """
        res_matrix = self.copy()
        res_matrix.__imul__(other)
        return res_matrix

    def __imul__(self, other):
        """
        Multiplies this Matrix44 by another, called by the *= operator.
        """
        m1 = self.matrix
        m2 = other.matrix
        self.matrix = array('d', [
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
        ])
        return self

    def fast_mul(self, other):
        """
        Multiplies this matrix by <other>.

        Assumes that both matrices have a right column of (0, 0, 0, 1). This is true for matrices composed of rotations,
        translations and scales. fast_mul is approximately 25% quicker than the *= operator.

        """
        m1 = self.matrix
        m2 = other.matrix
        self.matrix = array('d', [
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
        ])
        return self

    def rows(self):
        """
        Returns an iterator for the rows in the Matrix44.
        """
        return (self.get_row(index) for index in (0, 1, 2, 3))

    def columns(self):
        """
        Returns an iterator for the columns in the Matrix44.
        """
        return (self.get_col(index) for index in (0, 1, 2, 3))

    def transform(self, vector):
        """
        Transforms a Vector3 and returns the result as a tuple.
        """
        m = self.matrix
        x, y, z = vector
        return (x * m[0] + y * m[4] + z * m[8] + m[12],
                x * m[1] + y * m[5] + z * m[9] + m[13],
                x * m[2] + y * m[6] + z * m[10] + m[14])

    def transform_vectors(self, vectors):
        """
        Transform multiple vectors.
        """
        result = []
        m0, m1, m2, m3, m4, m5, m6, m7, m8, m9, m10, m11, m12, m13, m14, m15 = self.matrix
        for vector in vectors:
            x, y, z = vector
            result.append((
                x * m0 + y * m4 + z * m8 + m12,
                x * m1 + y * m5 + z * m9 + m13,
                x * m2 + y * m6 + z * m10 + m14
            ))
        return result

    def transpose(self):
        """
        Swaps the rows for columns.
        """
        m00, m01, m02, m03, \
        m10, m11, m12, m13, \
        m20, m21, m22, m23, \
        m30, m31, m32, m33 = self.matrix

        self.matrix = array('d', [
            m00, m10, m20, m30,
            m01, m11, m21, m31,
            m02, m12, m22, m32,
            m03, m13, m23, m33
        ])

    def get_transpose(self):
        """
        Returns a Matrix44 that is a copy of this, but with rows and columns swapped.
        """
        matrix = self.copy()
        matrix.transpose()
        return matrix

    def determinant(self):
        e11, e12, e13, e14, \
        e21, e22, e23, e24, \
        e31, e32, e33, e34, \
        e41, e42, e43, e44 = self.matrix
        return e11 * e22 * e33 * e44 - e11 * e22 * e34 * e43 + e11 * e23 * e34 * e42 - e11 * e23 * e32 * e44 + \
               e11 * e24 * e32 * e43 - e11 * e24 * e33 * e42 - e12 * e23 * e34 * e41 + e12 * e23 * e31 * e44 - \
               e12 * e24 * e31 * e43 + e12 * e24 * e33 * e41 - e12 * e21 * e33 * e44 + e12 * e21 * e34 * e43 + \
               e13 * e24 * e31 * e42 - e13 * e24 * e32 * e41 + e13 * e21 * e32 * e44 - e13 * e21 * e34 * e42 + \
               e13 * e22 * e34 * e41 - e13 * e22 * e31 * e44 - e14 * e21 * e32 * e43 + e14 * e21 * e33 * e42 - \
               e14 * e22 * e33 * e41 + e14 * e22 * e31 * e43 - e14 * e23 * e31 * e42 + e14 * e23 * e32 * e41

    def inverse(self):
        """
        Calculates the inverse of the matrix.

        Raises ZeroDivisionError if matrix has no inverse.
        """
        det = self.determinant()
        f = 1./det  # catch ZeroDivisionError by caller
        m00, m01, m02, m03, \
        m10, m11, m12, m13, \
        m20, m21, m22, m23, \
        m30, m31, m32, m33 = self.matrix
        self.matrix = array('d', (
            (m12*m23*m31 - m13*m22*m31 + m13*m21*m32 - m11*m23*m32 - m12*m21*m33 + m11*m22*m33)*f,
            (m03*m22*m31 - m02*m23*m31 - m03*m21*m32 + m01*m23*m32 + m02*m21*m33 - m01*m22*m33)*f,
            (m02*m13*m31 - m03*m12*m31 + m03*m11*m32 - m01*m13*m32 - m02*m11*m33 + m01*m12*m33)*f,
            (m03*m12*m21 - m02*m13*m21 - m03*m11*m22 + m01*m13*m22 + m02*m11*m23 - m01*m12*m23)*f,
            (m13*m22*m30 - m12*m23*m30 - m13*m20*m32 + m10*m23*m32 + m12*m20*m33 - m10*m22*m33)*f,
            (m02*m23*m30 - m03*m22*m30 + m03*m20*m32 - m00*m23*m32 - m02*m20*m33 + m00*m22*m33)*f,
            (m03*m12*m30 - m02*m13*m30 - m03*m10*m32 + m00*m13*m32 + m02*m10*m33 - m00*m12*m33)*f,
            (m02*m13*m20 - m03*m12*m20 + m03*m10*m22 - m00*m13*m22 - m02*m10*m23 + m00*m12*m23)*f,
            (m11*m23*m30 - m13*m21*m30 + m13*m20*m31 - m10*m23*m31 - m11*m20*m33 + m10*m21*m33)*f,
            (m03*m21*m30 - m01*m23*m30 - m03*m20*m31 + m00*m23*m31 + m01*m20*m33 - m00*m21*m33)*f,
            (m01*m13*m30 - m03*m11*m30 + m03*m10*m31 - m00*m13*m31 - m01*m10*m33 + m00*m11*m33)*f,
            (m03*m11*m20 - m01*m13*m20 - m03*m10*m21 + m00*m13*m21 + m01*m10*m23 - m00*m11*m23)*f,
            (m12*m21*m30 - m11*m22*m30 - m12*m20*m31 + m10*m22*m31 + m11*m20*m32 - m10*m21*m32)*f,
            (m01*m22*m30 - m02*m21*m30 + m02*m20*m31 - m00*m22*m31 - m01*m20*m32 + m00*m21*m32)*f,
            (m02*m11*m30 - m01*m12*m30 - m02*m10*m31 + m00*m12*m31 + m01*m10*m32 - m00*m11*m32)*f,
            (m01*m12*m20 - m02*m11*m20 + m02*m10*m21 - m00*m12*m21 - m01*m10*m22 + m00*m11*m22)*f))
