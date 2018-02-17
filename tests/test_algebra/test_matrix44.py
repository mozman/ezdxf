# Author:  mozman
# Created: 19.04.2010
# License: MIT License

import unittest
from math import radians, sin, cos, pi
from ezdxf.algebra.base import equals_almost
from ezdxf.algebra.matrix44 import Matrix44


def diag(values):
    m = Matrix44()
    for i, value in enumerate(values):
        m[i, i] = value
    return m


def equal_matrix(m1, m2, precision=4):
    for row in range(4):
        for col in range(4):
            if not equals_almost(m1[row, col], m2[row, col], precision):
                return False
    return True


def equal_vector(v1, v2, precision=4):
    if len(v1) != len(v2):
        return False
    for index in range(len(v1)):
        if not equals_almost(v1[index], v2[index], precision):
            return False
    return True


def equal_vectors(p1, p2):
    for v1, v2 in zip(p1, p2):
        if not equal_vector(v1, v2):
            return False
    return True


class TestMatrix44(unittest.TestCase):
    def test_init_0(self):
        matrix = Matrix44()
        self.assertAlmostEqual(matrix[0, 0], 1.)
        self.assertAlmostEqual(matrix[1, 1], 1.)
        self.assertAlmostEqual(matrix[2, 2], 1.)
        self.assertAlmostEqual(matrix[3, 3], 1.)

    def test_init_1(self):
        matrix = Matrix44([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        self.assertEqual(matrix.get_row(0), (0.0, 1.0, 2.0, 3.0))
        self.assertEqual(matrix.get_row(1), (4.0, 5.0, 6.0, 7.0))
        self.assertEqual(matrix.get_row(2), (8.0, 9.0, 10.0, 11.0))
        self.assertEqual(matrix.get_row(3), (12.0, 13.0, 14.0, 15.0))

    def test_init_4(self):
        matrix = Matrix44((0, 1, 2, 3),
                          (4, 5, 6, 7),
                          (8, 9, 10, 11),
                          (12, 13, 14, 15))
        self.assertEqual(matrix.get_row(0), (0.0, 1.0, 2.0, 3.0))
        self.assertEqual(matrix.get_row(1), (4.0, 5.0, 6.0, 7.0))
        self.assertEqual(matrix.get_row(2), (8.0, 9.0, 10.0, 11.0))
        self.assertEqual(matrix.get_row(3), (12.0, 13.0, 14.0, 15.0))

    def test_from_iter(self):
        values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        matrix = Matrix44.from_iter(values)
        for v1, m1 in zip(values, matrix):
            self.assertAlmostEqual(v1, m1)

    def test_iter(self):
        values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        matrix = Matrix44(values)
        for v1, m1 in zip(values, matrix):
            self.assertAlmostEqual(v1, m1)

    def test_copy(self):
        values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        m1 = Matrix44(values)
        matrix = m1.copy()
        for v1, m1 in zip(values, matrix):
            self.assertAlmostEqual(v1, m1)

    def test_get_row(self):
        matrix = Matrix44()
        self.assertEqual(matrix.get_row(0), (1.0, 0.0, 0.0, 0.0))
        self.assertEqual(matrix.get_row(1), (0.0, 1.0, 0.0, 0.0))
        self.assertEqual(matrix.get_row(2), (0.0, 0.0, 1.0, 0.0))
        self.assertEqual(matrix.get_row(3), (0.0, 0.0, 0.0, 1.0))

    def test_set_row(self):
        matrix = Matrix44()
        matrix.set_row(0, (2., 3., 4., 5.))
        self.assertEqual(matrix.get_row(0), (2.0, 3.0, 4.0, 5.0))
        matrix.set_row(1, (6., 7., 8., 9.))
        self.assertEqual(matrix.get_row(1), (6.0, 7.0, 8.0, 9.0))
        matrix.set_row(2, (10., 11., 12., 13.))
        self.assertEqual(matrix.get_row(2), (10.0, 11.0, 12.0, 13.0))
        matrix.set_row(3, (14., 15., 16., 17.))
        self.assertEqual(matrix.get_row(3), (14.0, 15.0, 16.0, 17.0))

    def test_get_col(self):
        matrix = Matrix44()
        self.assertEqual(matrix.get_col(0), (1.0, 0.0, 0.0, 0.0))
        self.assertEqual(matrix.get_col(1), (0.0, 1.0, 0.0, 0.0))
        self.assertEqual(matrix.get_col(2), (0.0, 0.0, 1.0, 0.0))
        self.assertEqual(matrix.get_col(3), (0.0, 0.0, 0.0, 1.0))

    def test_set_col(self):
        matrix = Matrix44()
        matrix.set_col(0, (2., 3., 4., 5.))
        self.assertEqual(matrix.get_col(0), (2.0, 3.0, 4.0, 5.0))
        matrix.set_col(1, (6., 7., 8., 9.))
        self.assertEqual(matrix.get_col(1), (6.0, 7.0, 8.0, 9.0))
        matrix.set_col(2, (10., 11., 12., 13.))
        self.assertEqual(matrix.get_col(2), (10.0, 11.0, 12.0, 13.0))
        matrix.set_col(3, (14., 15., 16., 17.))
        self.assertEqual(matrix.get_col(3), (14.0, 15.0, 16.0, 17.0))

    def test_set(self):
        matrix = Matrix44()
        matrix.set((2., 3., 4., 5.),
                   (6., 7., 8., 9.),
                   (10., 11., 12., 13.),
                   (14., 15., 16., 17.)
                   )
        self.assertEqual(matrix.get_row(0), (2.0, 3.0, 4.0, 5.0))
        self.assertEqual(matrix.get_row(1), (6.0, 7.0, 8.0, 9.0))
        self.assertEqual(matrix.get_row(2), (10.0, 11.0, 12.0, 13.0))
        self.assertEqual(matrix.get_row(3), (14.0, 15.0, 16.0, 17.0))

    def test_translate(self):
        t = Matrix44.translate(10, 20, 30)
        x = diag((1., 1., 1., 1.))
        x[3, 0] = 10.
        x[3, 1] = 20.
        x[3, 2] = 30.
        self.assertTrue(equal_matrix(t, x))

    def test_scale(self):
        t = Matrix44.scale(10, 20, 30)
        x = diag((10., 20., 30., 1.))
        self.assertTrue(equal_matrix(t, x))

    def test_x_rotate(self):
        alpha = radians(25)
        t = Matrix44.x_rotate(alpha)
        x = diag((1., 1., 1., 1.))
        x[1, 1] = cos(alpha)
        x[2, 1] = -sin(alpha)
        x[1, 2] = sin(alpha)
        x[2, 2] = cos(alpha)
        self.assertTrue(equal_matrix(t, x))

    def test_y_rotate(self):
        alpha = radians(25)
        t = Matrix44.y_rotate(alpha)
        x = diag((1., 1., 1., 1.))
        x[0, 0] = cos(alpha)
        x[2, 0] = sin(alpha)
        x[0, 2] = -sin(alpha)
        x[2, 2] = cos(alpha)
        self.assertTrue(equal_matrix(t, x))

    def test_z_rotate(self):
        alpha = radians(25)
        t = Matrix44.z_rotate(alpha)
        x = diag((1., 1., 1., 1.))
        x[0, 0] = cos(alpha)
        x[1, 0] = -sin(alpha)
        x[0, 1] = sin(alpha)
        x[1, 1] = cos(alpha)
        self.assertTrue(equal_matrix(t, x))

    def test_chain(self):
        s = Matrix44.scale(10, 20, 30)
        t = Matrix44.translate(10, 20, 30)

        c = Matrix44.chain(s, t)
        x = diag((10., 20., 30., 1.))
        x[3, 0] = 10.
        x[3, 1] = 20.
        x[3, 2] = 30.
        self.assertTrue(equal_matrix(c, x))

    def test_chain2(self):
        s = Matrix44.scale(10, 20, 30)
        t = Matrix44.translate(10, 20, 30)
        r = Matrix44.axis_rotate(angle=pi / 2, axis=(0., 0., 1.))
        points = ((23., 97., .5), (2., 7., 13.))

        p1 = s.transform_vectors(points)
        p1 = t.transform_vectors(p1)
        p1 = r.transform_vectors(p1)

        c = Matrix44.chain(s, t, r)
        p2 = c.transform_vectors(points)
        self.assertTrue(equal_vectors(p1, p2))

    def test_transform(self):
        t = Matrix44.scale(2., .5, 1.)
        r = t.transform((10., 20., 30.))
        self.assertEqual(r, (20., 10., 30.))

    def test_transpose(self):
        matrix = Matrix44((0, 1, 2, 3),
                          (4, 5, 6, 7),
                          (8, 9, 10, 11),
                          (12, 13, 14, 15))
        matrix.transpose()
        self.assertEqual(matrix.get_row(0), (0.0, 4.0, 8.0, 12.0))
        self.assertEqual(matrix.get_row(1), (1.0, 5.0, 9.0, 13.0))
        self.assertEqual(matrix.get_row(2), (2.0, 6.0, 10.0, 14.0))
        self.assertEqual(matrix.get_row(3), (3.0, 7.0, 11.0, 15.0))

    def test_inverse_error(self):
        m = Matrix44([1] * 16)
        self.assertRaises(ZeroDivisionError, m.inverse)
