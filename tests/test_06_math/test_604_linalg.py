# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from typing import Iterable
import pytest
import math
from ezdxf.math.linalg import Matrix, gauss_vector_solver, gauss_matrix_solver, gauss_jordan_solver


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


def test_set_row(X):
    X.set_row(0, [1, 1])
    X.set_row(2, [2, 2])
    assert X.row(0) == [1, 1]
    assert X.row(2) == [2, 2]
    assert list(X.rows()) == [[1, 1], [4, 5], [2, 2]]

    X.set_row(-1, [7, 7])
    assert X.row(2) == [7, 7]


def test_set_row_error(X):
    with pytest.raises(IndexError):
        X.set_row(5, [1, 1])


def test_col(X):
    assert X.col(0) == [12, 4, 3]
    assert X.col(1) == [7, 5, 8]
    assert list(X.cols()) == [[12, 4, 3], [7, 5, 8]]


def test_set_col(X):
    X.set_col(0, [1, 1, 1])
    X.set_col(1, [2, 2, 2])
    assert X.col(0) == [1, 1, 1]
    assert X.col(1) == [2, 2, 2]
    assert list(X.cols()) == [[1, 1, 1], [2, 2, 2]]

    X.set_col(-1, [3, 3, 3])
    assert X.col(1) == [3, 3, 3]


def test_set_col_error(X):
    with pytest.raises(IndexError):
        X.set_col(2, [1, 1, 1])


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


def test_swap_rows(X):
    # X = [[12, 7], [4, 5], [3, 8]]
    X.swap_rows(0, 2)
    assert X.row(0) == [3, 8]
    assert X.row(2) == [12, 7]


def test_swap_cols(X):
    # X = [[12, 7], [4, 5], [3, 8]]
    X.swap_cols(0, 1)
    assert X.col(0) == [7, 5, 8]
    assert X.col(1) == [12, 4, 3]


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


def test_identity():
    m = Matrix.identity((3, 4))
    for i in range(3):
        assert m[i, i] == 1.0


A = [
    [2, 3, 2, 5, 6],
    [5, 1, 4, 5, 3],
    [1, 12, 3, 1, 12],
    [7, 3, 2, 2, 6],
    [9, 4, 2, 13, 6],
]
B1 = [6, 9, 5, 4, 8]
B2 = [5, 10, 6, 3, 2]
B3 = [1, 7, 3, 9, 12]

EXPECTED = [-0.14854771784232382, -0.3128630705394192, 1.7966804979253113, 0.41908713692946065, 0.2578146611341633]


def test_gauss_vector_solver():
    result = gauss_vector_solver(A, B1)
    assert result == EXPECTED


def test_gauss_matrix_solver():
    B = Matrix()
    B.append_col(B1)
    B.append_col(B2)
    B.append_col(B3)
    result = gauss_matrix_solver(A, B.matrix)
    assert result.col(0) == gauss_vector_solver(A, B1)
    assert result.col(1) == gauss_vector_solver(A, B2)
    assert result.col(2) == gauss_vector_solver(A, B3)


def are_close_vectors(v1: Iterable[float], v2: Iterable[float], abs_tol: float = 1e-12):
    for i, j in zip(v1, v2):
        assert math.isclose(i, j, abs_tol=abs_tol)


def test_gauss_jordan_vector_solver():
    B = Matrix(items=B1, shape=(5, 1))
    result_A, result_B = gauss_jordan_solver(A, B)
    are_close_vectors(result_B.col(0), EXPECTED)


def test_gauss_jordan_matrix_solver():
    B = Matrix()
    B.append_col(B1)
    B.append_col(B2)
    B.append_col(B3)

    result_A, result_B = gauss_jordan_solver(A, B)
    are_close_vectors(result_B.col(0), gauss_vector_solver(A, B1))
    are_close_vectors(result_B.col(1), gauss_vector_solver(A, B2))
    are_close_vectors(result_B.col(2), gauss_vector_solver(A, B3))
