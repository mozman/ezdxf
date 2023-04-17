# Copyright (c) 2010-2023, Manfred Moitzi
# License: MIT License
import pytest
import pickle
from math import radians, sin, cos, pi, isclose

# Import from 'ezdxf.math._matrix44' to test Python implementation
from ezdxf.math import (
    close_vectors,
    has_matrix_2d_stretching,
    has_matrix_3d_stretching,
)
from ezdxf.math._matrix44 import Matrix44
from ezdxf.acc import USE_C_EXT

m44_classes = [Matrix44]

if USE_C_EXT:
    from ezdxf.acc.matrix44 import Matrix44 as CMatrix44

    m44_classes.append(CMatrix44)


@pytest.fixture(params=m44_classes)
def m44(request):
    return request.param


def diag(values, m44_cls):
    m = m44_cls()
    for i, value in enumerate(values):
        m[i, i] = value
    return m


def equal_matrix(m1, m2, abs_tol=1e-9):
    for row in range(4):
        for col in range(4):
            if not isclose(m1[row, col], m2[row, col], abs_tol=abs_tol):
                return False
    return True


class TestMatrix44:
    @pytest.mark.parametrize("index", [0, 1, 2, 3])
    def test_default_constructor(self, index, m44):
        matrix = m44()
        assert matrix[index, index] == 1.0

    def test_numbers_constructor(self, m44):
        matrix = m44([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        assert matrix.get_row(0) == (0.0, 1.0, 2.0, 3.0)
        assert matrix.get_row(1) == (4.0, 5.0, 6.0, 7.0)
        assert matrix.get_row(2) == (8.0, 9.0, 10.0, 11.0)
        assert matrix.get_row(3) == (12.0, 13.0, 14.0, 15.0)

    def test_row_constructor(self, m44):
        matrix = m44(
            (0, 1, 2, 3), (4, 5, 6, 7), (8, 9, 10, 11), (12, 13, 14, 15)
        )
        assert matrix.get_row(0) == (0.0, 1.0, 2.0, 3.0)
        assert matrix.get_row(1) == (4.0, 5.0, 6.0, 7.0)
        assert matrix.get_row(2) == (8.0, 9.0, 10.0, 11.0)
        assert matrix.get_row(3) == (12.0, 13.0, 14.0, 15.0)

    def test_invalid_row_constructor(self, m44):
        with pytest.raises(ValueError):
            m44(
                (0, 1, 2, 3), (4, 5, 6, 7), (8, 9, 10, 11), (12, 13, 14, 15, 16)
            )
        with pytest.raises(ValueError):
            m44(
                (0, 1, 2, 3),
                (4, 5, 6, 7),
                (8, 9, 10, 11),
                (
                    12,
                    13,
                    14,
                ),
            )

    def test_invalid_number_constructor(self, m44):
        pytest.raises(ValueError, m44, range(17))
        pytest.raises(ValueError, m44, range(15))

    def test_get_item_does_not_support_slicing(self, m44):
        with pytest.raises(TypeError):
            _ = m44()[:]

    def test_get_item_index_error(self, m44):
        with pytest.raises(IndexError):
            _ = m44()[(-1, -1)]
        with pytest.raises(IndexError):
            _ = m44()[(0, 4)]
        with pytest.raises(IndexError):
            _ = m44()[(1, -1)]
        with pytest.raises(IndexError):
            _ = m44()[4, 4]

    def test_set_item_does_not_support_slicing(self, m44):
        with pytest.raises(TypeError):
            m44()[:] = (1, 2)

    def test_set_item_index_error(self, m44):
        with pytest.raises(IndexError):
            m44()[-1, -1] = 0
        with pytest.raises(IndexError):
            m44()[4, 4] = 0

    def test_iter(self, m44):
        values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        matrix = m44(values)
        for v1, m1 in zip(values, matrix):
            assert v1 == m1

    def test_copy(self, m44):
        values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        m1 = m44(values)
        matrix = m1.copy()
        for v1, m1 in zip(values, matrix):
            assert v1 == m1

    def test_get_row_index_error(self, m44):
        with pytest.raises(IndexError):
            m44().get_row(-1)
        with pytest.raises(IndexError):
            m44().get_row(4)

    def test_set_row(self, m44):
        matrix = m44()
        matrix.set_row(0, (2.0, 3.0, 4.0, 5.0))
        assert matrix.get_row(0) == (2.0, 3.0, 4.0, 5.0)
        matrix.set_row(1, (6.0, 7.0, 8.0, 9.0))
        assert matrix.get_row(1) == (6.0, 7.0, 8.0, 9.0)
        matrix.set_row(2, (10.0, 11.0, 12.0, 13.0))
        assert matrix.get_row(2) == (10.0, 11.0, 12.0, 13.0)
        matrix.set_row(3, (14.0, 15.0, 16.0, 17.0))
        assert matrix.get_row(3) == (14.0, 15.0, 16.0, 17.0)

    def test_set_row_index_error(self, m44):
        with pytest.raises(IndexError):
            m44().set_row(-1, (0,))
        with pytest.raises(IndexError):
            m44().set_row(4, (0,))

    def test_get_col(self, m44):
        matrix = m44()
        assert matrix.get_col(0) == (1.0, 0.0, 0.0, 0.0)
        assert matrix.get_col(1) == (0.0, 1.0, 0.0, 0.0)
        assert matrix.get_col(2) == (0.0, 0.0, 1.0, 0.0)
        assert matrix.get_col(3) == (0.0, 0.0, 0.0, 1.0)

    def test_get_col_index_error(self, m44):
        with pytest.raises(IndexError):
            m44().get_col(-1)
        with pytest.raises(IndexError):
            m44().get_col(4)

    def test_set_col(self, m44):
        matrix = m44()
        matrix.set_col(0, (2.0, 3.0, 4.0, 5.0))
        assert matrix.get_col(0) == (2.0, 3.0, 4.0, 5.0)
        matrix.set_col(1, (6.0, 7.0, 8.0, 9.0))
        assert matrix.get_col(1) == (6.0, 7.0, 8.0, 9.0)
        matrix.set_col(2, (10.0, 11.0, 12.0, 13.0))
        assert matrix.get_col(2) == (10.0, 11.0, 12.0, 13.0)
        matrix.set_col(3, (14.0, 15.0, 16.0, 17.0))
        assert matrix.get_col(3) == (14.0, 15.0, 16.0, 17.0)

    def test_set_col_index_error(self, m44):
        with pytest.raises(IndexError):
            m44().set_col(-1, (0,))
        with pytest.raises(IndexError):
            m44().set_col(4, (0,))

    def test_is_orthogonal(self, m44):
        assert m44().is_orthogonal is True

    def test_is_cartesian(self, m44):
        assert m44().is_cartesian is True

    def test_translate(self, m44):
        t = m44.translate(10, 20, 30)
        x = diag((1.0, 1.0, 1.0, 1.0), m44)
        x[3, 0] = 10.0
        x[3, 1] = 20.0
        x[3, 2] = 30.0
        assert equal_matrix(t, x) is True

    def test_scale(self, m44):
        t = m44.scale(10, 20, 30)
        x = diag((10.0, 20.0, 30.0, 1.0), m44)
        assert equal_matrix(t, x) is True

    def test_x_rotate(self, m44):
        alpha = radians(25)
        t = m44.x_rotate(alpha)
        x = diag((1.0, 1.0, 1.0, 1.0), m44)
        x[1, 1] = cos(alpha)
        x[2, 1] = -sin(alpha)
        x[1, 2] = sin(alpha)
        x[2, 2] = cos(alpha)
        assert equal_matrix(t, x) is True

    def test_y_rotate(self, m44):
        alpha = radians(25)
        t = m44.y_rotate(alpha)
        x = diag((1.0, 1.0, 1.0, 1.0), m44)
        x[0, 0] = cos(alpha)
        x[2, 0] = sin(alpha)
        x[0, 2] = -sin(alpha)
        x[2, 2] = cos(alpha)
        assert equal_matrix(t, x) is True

    def test_z_rotate(self, m44):
        alpha = radians(25)
        t = m44.z_rotate(alpha)
        x = diag((1.0, 1.0, 1.0, 1.0), m44)
        x[0, 0] = cos(alpha)
        x[1, 0] = -sin(alpha)
        x[0, 1] = sin(alpha)
        x[1, 1] = cos(alpha)
        assert equal_matrix(t, x) is True

    def test_chain(self, m44):
        s = m44.scale(10, 20, 30)
        t = m44.translate(10, 20, 30)

        c = m44.chain(s, t)
        x = diag((10.0, 20.0, 30.0, 1.0), m44)
        x[3, 0] = 10.0
        x[3, 1] = 20.0
        x[3, 2] = 30.0
        assert equal_matrix(c, x) is True

    def test_chain2(self, m44):
        s = m44.scale(10, 20, 30)
        t = m44.translate(10, 20, 30)
        r = m44.axis_rotate(angle=pi / 2, axis=(0.0, 0.0, 1.0))
        points = ((23.0, 97.0, 0.5), (2.0, 7.0, 13.0))

        p1 = s.transform_vertices(points)
        p1 = t.transform_vertices(p1)
        p1 = r.transform_vertices(p1)

        c = m44.chain(s, t, r)
        p2 = c.transform_vertices(points)
        assert close_vectors(p1, p2) is True

    def test_transform(self, m44):
        t = m44.scale(2.0, 0.5, 1.0)
        r = t.transform((10.0, 20.0, 30.0))
        assert r == (20.0, 10.0, 30.0)

    def test_multiply(self, m44):
        m1 = m44(range(16))
        m2 = m44(range(16))
        res = m1 * m2
        expected = m44(
            (56.0, 62.0, 68.0, 74.0),
            (152.0, 174.0, 196.0, 218.0),
            (248.0, 286.0, 324.0, 362.0),
            (344.0, 398.0, 452.0, 506.0),
        )
        assert equal_matrix(res, expected)
        # __matmul__()
        res = m1 @ m2
        assert equal_matrix(res, expected)

    def test_transpose(self, m44):
        matrix = m44(
            (0, 1, 2, 3), (4, 5, 6, 7), (8, 9, 10, 11), (12, 13, 14, 15)
        )
        matrix.transpose()
        assert matrix.get_row(0) == (0.0, 4.0, 8.0, 12.0)
        assert matrix.get_row(1) == (1.0, 5.0, 9.0, 13.0)
        assert matrix.get_row(2) == (2.0, 6.0, 10.0, 14.0)
        assert matrix.get_row(3) == (3.0, 7.0, 11.0, 15.0)

    def test_inverse_error(self, m44):
        m = m44([1] * 16)
        pytest.raises(ZeroDivisionError, m.inverse)

    def test_axis_rotate_for_axis_normalization(self, m44):
        m1 = m44.axis_rotate((0, 0, 1), 1.23)
        m2 = m44.axis_rotate((0, 0, 0.5), 1.23)
        for a, b in zip(m1, m2):
            assert isclose(a, b)

    def test_assign_after_initialised(self, m44):
        matrix = m44()
        matrix[0, 0] = 12
        matrix2 = m44()
        assert matrix2[0, 0] == 1

        values = list(range(16))
        matrix = m44(values)
        matrix[0, 0] = 12
        assert values[0] == 0
        assert matrix[0, 0] == 12

    def test_picklable(self, m44):
        matrix = m44(
            (0.1, 1, 2, 3), (4, 5, 6, 7), (8, 9, 10, 11), (12, 13, 14, 15)
        )
        pickled_matrix = pickle.loads(pickle.dumps(matrix))
        assert equal_matrix(matrix, pickled_matrix)
        assert type(matrix) is type(pickled_matrix)
        matrix[0, 0] = 12
        assert not equal_matrix(matrix, pickled_matrix)

    def test_shear_xy(self, m44):
        angle = pi / 4
        matrix = m44.shear_xy(angle_x=angle, angle_y=-angle)
        assert matrix[0, 1] == pytest.approx(-1.0)
        assert matrix[1, 0] == pytest.approx(1.0)


def test_has_matrix_2d_stretching():
    """Note: Uniform scaling is not stretching in this context."""
    assert has_matrix_2d_stretching(Matrix44.scale(1, 1, 1)) is False
    assert has_matrix_2d_stretching(Matrix44.scale(2, 2, 2)) is False
    assert (
        has_matrix_2d_stretching(Matrix44.scale(1, 1, 2)) is False
    ), "ignore z-axis"
    assert has_matrix_2d_stretching(Matrix44.scale(2, 1, 1)) is True
    assert has_matrix_2d_stretching(Matrix44.scale(1, 2, 1)) is True


def test_has_matrix_3d_stretching():
    """Note: Uniform scaling is not stretching in this context."""
    assert has_matrix_3d_stretching(Matrix44.scale(1, 1, 1)) is False
    assert has_matrix_3d_stretching(Matrix44.scale(2, 2, 2)) is False
    assert has_matrix_3d_stretching(Matrix44.scale(2, 1, 1)) is True
    assert has_matrix_3d_stretching(Matrix44.scale(1, 2, 1)) is True
    assert has_matrix_3d_stretching(Matrix44.scale(1, 1, 2)) is True
