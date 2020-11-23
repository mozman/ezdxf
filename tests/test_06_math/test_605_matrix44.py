# Author:  mozman
# Created: 19.04.2010
# License: MIT License
import pytest
from math import radians, sin, cos, pi, isclose
# Import from 'ezdxf.math.matrix44' to test Python implementation
from ezdxf.math.matrix44 import Matrix44


def diag(values):
    m = Matrix44()
    for i, value in enumerate(values):
        m[i, i] = value
    return m


def equal_matrix(m1, m2, abs_tol=1e-9):
    for row in range(4):
        for col in range(4):
            if not isclose(m1[row, col], m2[row, col], abs_tol=abs_tol):
                return False
    return True


def equal_vector(v1, v2, abs_tol=1e-9):
    if len(v1) != len(v2):
        return False
    for index in range(len(v1)):
        if not isclose(v1[index], v2[index], abs_tol=abs_tol):
            return False
    return True


def equal_vectors(p1, p2):
    for v1, v2 in zip(p1, p2):
        if not equal_vector(v1, v2):
            return False
    return True


class TestMatrix44:
    def test_init_0(self):
        matrix = Matrix44()
        isclose(matrix[0, 0], 1.)
        isclose(matrix[1, 1], 1.)
        isclose(matrix[2, 2], 1.)
        isclose(matrix[3, 3], 1.)

    def test_init_1(self):
        matrix = Matrix44([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        assert matrix.get_row(0) == (0.0, 1.0, 2.0, 3.0)
        assert matrix.get_row(1) == (4.0, 5.0, 6.0, 7.0)
        assert matrix.get_row(2) == (8.0, 9.0, 10.0, 11.0)
        assert matrix.get_row(3) == (12.0, 13.0, 14.0, 15.0)

    def test_init_4(self):
        matrix = Matrix44((0, 1, 2, 3),
                          (4, 5, 6, 7),
                          (8, 9, 10, 11),
                          (12, 13, 14, 15))
        assert matrix.get_row(0) == (0.0, 1.0, 2.0, 3.0)
        assert matrix.get_row(1) == (4.0, 5.0, 6.0, 7.0)
        assert matrix.get_row(2) == (8.0, 9.0, 10.0, 11.0)
        assert matrix.get_row(3) == (12.0, 13.0, 14.0, 15.0)

    def test_invalid_init(self):
        with pytest.raises(ValueError):
            Matrix44((0, 1, 2, 3), (4, 5, 6, 7), (8, 9, 10, 11), (12, 13, 14, 15, 16))
        with pytest.raises(ValueError):
            Matrix44((0, 1, 2, 3), (4, 5, 6, 7), (8, 9, 10, 11), )
        with pytest.raises(ValueError):
            Matrix44([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])
        with pytest.raises(ValueError):
            Matrix44([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])

    def test_iter(self):
        values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        matrix = Matrix44(values)
        for v1, m1 in zip(values, matrix):
            assert isclose(v1, m1)

    def test_copy(self):
        values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        m1 = Matrix44(values)
        matrix = m1.copy()
        for v1, m1 in zip(values, matrix):
            assert isclose(v1, m1)

    def test_get_row(self):
        matrix = Matrix44()
        assert matrix.get_row(0) == (1.0, 0.0, 0.0, 0.0)
        assert matrix.get_row(1) == (0.0, 1.0, 0.0, 0.0)
        assert matrix.get_row(2) == (0.0, 0.0, 1.0, 0.0)
        assert matrix.get_row(3) == (0.0, 0.0, 0.0, 1.0)

    def test_set_row(self):
        matrix = Matrix44()
        matrix.set_row(0, (2., 3., 4., 5.))
        assert matrix.get_row(0) == (2.0, 3.0, 4.0, 5.0)
        matrix.set_row(1, (6., 7., 8., 9.))
        assert matrix.get_row(1) == (6.0, 7.0, 8.0, 9.0)
        matrix.set_row(2, (10., 11., 12., 13.))
        assert matrix.get_row(2) == (10.0, 11.0, 12.0, 13.0)
        matrix.set_row(3, (14., 15., 16., 17.))
        assert matrix.get_row(3) == (14.0, 15.0, 16.0, 17.0)

    def test_get_col(self):
        matrix = Matrix44()
        assert matrix.get_col(0) == (1.0, 0.0, 0.0, 0.0)
        assert matrix.get_col(1) == (0.0, 1.0, 0.0, 0.0)
        assert matrix.get_col(2) == (0.0, 0.0, 1.0, 0.0)
        assert matrix.get_col(3) == (0.0, 0.0, 0.0, 1.0)

    def test_set_col(self):
        matrix = Matrix44()
        matrix.set_col(0, (2., 3., 4., 5.))
        assert matrix.get_col(0) == (2.0, 3.0, 4.0, 5.0)
        matrix.set_col(1, (6., 7., 8., 9.))
        assert matrix.get_col(1) == (6.0, 7.0, 8.0, 9.0)
        matrix.set_col(2, (10., 11., 12., 13.))
        assert matrix.get_col(2) == (10.0, 11.0, 12.0, 13.0)
        matrix.set_col(3, (14., 15., 16., 17.))
        assert matrix.get_col(3) == (14.0, 15.0, 16.0, 17.0)

    def test_set(self):
        matrix = Matrix44()
        matrix.set((2., 3., 4., 5.),
                   (6., 7., 8., 9.),
                   (10., 11., 12., 13.),
                   (14., 15., 16., 17.)
                   )
        assert matrix.get_row(0) == (2.0, 3.0, 4.0, 5.0)
        assert matrix.get_row(1) == (6.0, 7.0, 8.0, 9.0)
        assert matrix.get_row(2) == (10.0, 11.0, 12.0, 13.0)
        assert matrix.get_row(3) == (14.0, 15.0, 16.0, 17.0)

    def test_translate(self):
        t = Matrix44.translate(10, 20, 30)
        x = diag((1., 1., 1., 1.))
        x[3, 0] = 10.
        x[3, 1] = 20.
        x[3, 2] = 30.
        assert equal_matrix(t, x) is True

    def test_scale(self):
        t = Matrix44.scale(10, 20, 30)
        x = diag((10., 20., 30., 1.))
        assert equal_matrix(t, x) is True

    def test_x_rotate(self):
        alpha = radians(25)
        t = Matrix44.x_rotate(alpha)
        x = diag((1., 1., 1., 1.))
        x[1, 1] = cos(alpha)
        x[2, 1] = -sin(alpha)
        x[1, 2] = sin(alpha)
        x[2, 2] = cos(alpha)
        assert equal_matrix(t, x) is True

    def test_y_rotate(self):
        alpha = radians(25)
        t = Matrix44.y_rotate(alpha)
        x = diag((1., 1., 1., 1.))
        x[0, 0] = cos(alpha)
        x[2, 0] = sin(alpha)
        x[0, 2] = -sin(alpha)
        x[2, 2] = cos(alpha)
        assert equal_matrix(t, x) is True

    def test_z_rotate(self):
        alpha = radians(25)
        t = Matrix44.z_rotate(alpha)
        x = diag((1., 1., 1., 1.))
        x[0, 0] = cos(alpha)
        x[1, 0] = -sin(alpha)
        x[0, 1] = sin(alpha)
        x[1, 1] = cos(alpha)
        assert equal_matrix(t, x) is True

    def test_chain(self):
        s = Matrix44.scale(10, 20, 30)
        t = Matrix44.translate(10, 20, 30)

        c = Matrix44.chain(s, t)
        x = diag((10., 20., 30., 1.))
        x[3, 0] = 10.
        x[3, 1] = 20.
        x[3, 2] = 30.
        assert equal_matrix(c, x) is True

    def test_chain2(self):
        s = Matrix44.scale(10, 20, 30)
        t = Matrix44.translate(10, 20, 30)
        r = Matrix44.axis_rotate(angle=pi / 2, axis=(0., 0., 1.))
        points = ((23., 97., .5), (2., 7., 13.))

        p1 = s.transform_vertices(points)
        p1 = t.transform_vertices(p1)
        p1 = r.transform_vertices(p1)

        c = Matrix44.chain(s, t, r)
        p2 = c.transform_vertices(points)
        assert equal_vectors(p1, p2) is True

    def test_transform(self):
        t = Matrix44.scale(2., .5, 1.)
        r = t.transform((10., 20., 30.))
        assert r == (20., 10., 30.)

    def test_transpose(self):
        matrix = Matrix44((0, 1, 2, 3),
                          (4, 5, 6, 7),
                          (8, 9, 10, 11),
                          (12, 13, 14, 15))
        matrix.transpose()
        assert matrix.get_row(0) == (0.0, 4.0, 8.0, 12.0)
        assert matrix.get_row(1) == (1.0, 5.0, 9.0, 13.0)
        assert matrix.get_row(2) == (2.0, 6.0, 10.0, 14.0)
        assert matrix.get_row(3) == (3.0, 7.0, 11.0, 15.0)

    def test_inverse_error(self):
        m = Matrix44([1] * 16)
        pytest.raises(ZeroDivisionError, m.inverse)

