# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.math.linalg import Matrix


@pytest.fixture
def X():
    return Matrix([[12, 7], [4, 5], [3, 8]])


def matrix_init(X):
    Y = Matrix([12, 7, 4, 5, 3, 8], shape=(3, 2))
    assert X.shape == X.nrows, X.ncols
    assert Y.shape == (3, 2)
    assert X == Y

    Y = Matrix(shape=(3, 3))
    assert Y == Matrix([[0, 0, 0], [0, 0, 0], [0, 0, 0]])

    Y = Matrix(X)
    assert Y == X
    Y[0, 0] = -1
    assert Y != X, 'should not share the same list objects'

    Y = Matrix(X, shape=(2, 3))
    assert Y.rows() == [[12, 7, 4], [5, 3, 8]]


def test_matrix_getter(X):
    assert X[0, 0] == 12
    assert X[2, 1] == 8


def test_matrix_setter(X):
    X[0, 0] = -7
    X[2, 1] = 1.5
    assert X[0, 0] == -7
    assert X[2, 1] == 1.5


def test_row(X):
    assert X.row(0) == [12, 7]
    assert X.row(1) == [4, 5]
    assert X.row(2) == [3, 8]
    assert list(X.rows()) == [[12, 7], [4, 5], [3, 8]]


def test_col(X):
    assert X.col(0) == [12, 4, 3]
    assert X.col(1) == [7, 5, 8]
    assert list(X.cols()) == [[12, 4, 3], [7, 5, 8]]


def test_mul():
    X = Matrix([
        [12, 7, 3],
        [4, 5, 6],
        [7, 8, 9],
    ])

    Y = Matrix([
        [5, 8, 1, 2],
        [6, 7, 3, 0],
        [4, 5, 9, 1],
    ])

    R = Matrix([
        [114, 160, 60, 27],
        [74, 97, 73, 14],
        [119, 157, 112, 23],
    ])

    assert X * Y == R


def test_imul():
    X = Matrix([
        [12, 7, 3],
        [4, 5, 6],
        [7, 8, 9],
    ])
    Y = X
    Y *= 10

    assert Y == Matrix([
        [120, 70, 30],
        [40, 50, 60],
        [70, 80, 90],
    ])
    assert X[0, 0] != Y[0, 0]


def test_transpose(X):
    R = Matrix([
        (12, 4, 3),
        (7, 5, 8),
    ])
    T = X.transpose()
    assert T == R
    # is T mutable?
    T[0, 0] = 99
    assert T[0, 0] == 99


def test_add(X):
    R = X + X
    assert R == Matrix([[24, 14], [8, 10], [6, 16]])

    R = R + 10
    assert R == Matrix([[34, 24], [18, 20], [16, 26]])


def test_iadd(X):
    Y = X
    Y += Y
    assert Y == Matrix([[24, 14], [8, 10], [6, 16]])
    assert Y[0, 0] != X[0, 0]
    Z = Y
    Z += 10
    assert Z == Matrix([[34, 24], [18, 20], [16, 26]])
    assert Y[0, 0] != Z[0, 0]


def test_sub(X):
    R = X - X
    assert R == Matrix([[0, 0], [0, 0], [0, 0]])

    R = X - 10
    assert R == Matrix([[2, -3], [-6, -5], [-7, -2]])


def test_build_matrix_by_rows():
    m = Matrix()
    m.append_row([1, 2, 3])
    assert m.nrows == 1
    assert m.ncols == 3


def test_build_matrix_by_cols():
    m = Matrix()
    m.append_col([1, 2, 3])
    assert m.nrows == 3
    assert m.ncols == 1
