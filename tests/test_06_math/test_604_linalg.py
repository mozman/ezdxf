# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from typing import Iterable
import pytest
import math
from ezdxf.math.linalg import (
    Matrix, gauss_vector_solver, gauss_matrix_solver, gauss_jordan_solver, gauss_jordan_inverse, LUDecomposition,
)


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


def test_set_diag_float():
    m = Matrix(shape=(4, 4))
    m.set_diag(2)
    for i in range(4):
        assert m[i, i] == 2.0


def test_set_diag_col_offset():
    m = Matrix(shape=(4, 4))
    m.set_diag(2, col_offset=1)
    for i in range(3):
        assert m[i, i + 1] == 2.0


def test_set_diag_row_offset():
    m = Matrix(shape=(4, 4))
    m.set_diag(2, row_offset=1)
    for i in range(3):
        assert m[i + 1, i] == 2.0


def test_set_diag_iterable():
    m = Matrix(shape=(4, 4))
    m.set_diag(range(5))
    for i in range(4):
        assert m[i, i] == i


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

SOLUTION_B1 = [-0.14854771784232382, -0.3128630705394192, 1.7966804979253113, 0.41908713692946065, 0.2578146611341633]


def test_gauss_vector_solver():
    result = gauss_vector_solver(A, B1)
    assert result == SOLUTION_B1


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
    are_close_vectors(result_B.col(0), SOLUTION_B1)


def test_gauss_jordan_matrix_solver():
    B = Matrix()
    B.append_col(B1)
    B.append_col(B2)
    B.append_col(B3)

    result_A, result_B = gauss_jordan_solver(A, B)
    are_close_vectors(result_B.col(0), gauss_vector_solver(A, B1))
    are_close_vectors(result_B.col(1), gauss_vector_solver(A, B2))
    are_close_vectors(result_B.col(2), gauss_vector_solver(A, B3))


EXPECTED_INVERSE = [
    [-0.16390041493775933617, -0.002489626556016597522, -0.007468879668049792526, 0.13651452282157676342,
     0.043568464730290456478],
    [-0.33402489626556016593, 0.05062240663900414948, 0.15186721991701244817, -0.10912863070539419082,
     0.11410788381742738587],
    [-0.05394190871369294633, 0.34854771784232365142, 0.04564315352697095431, -0.11203319502074688787,
     -0.099585062240663900493],
    [0.06016597510373443986, -0.00414937759336099577, -0.012448132780082987519, -0.10580912863070539416,
     0.072614107883817427371],
    [0.35615491009681881048, -0.13720608575380359624, -0.078284923928077455093, 0.13457814661134163205,
     -0.098893499308437067754],
]


def test_gauss_jordan_inverse():
    result = gauss_jordan_inverse(A)
    assert result.nrows == len(A)
    assert result.ncols == len(A[0])
    m = Matrix(matrix=EXPECTED_INVERSE)
    assert result == m


def test_LU_decomposition_solve_vector():
    R = LUDecomposition(A).solve_vector(B1)
    are_close_vectors(R, SOLUTION_B1)


def test_LU_decomposition_solve_matrix():
    lu = LUDecomposition(A)

    B = Matrix()
    B.append_col(B1)
    B.append_col(B2)
    B.append_col(B3)

    result = lu.solve_matrix(B)
    are_close_vectors(result.col(0), gauss_vector_solver(A, B1))
    are_close_vectors(result.col(1), gauss_vector_solver(A, B2))
    are_close_vectors(result.col(2), gauss_vector_solver(A, B3))


def test_LU_decomposition_inverse():
    m = Matrix(matrix=EXPECTED_INVERSE)
    assert LUDecomposition(A).inverse() == m


def test_determinant():
    from ezdxf.math import Matrix44
    A = [
        [2, 3, 2, 5],
        [5, 1, 4, 5],
        [1, 12, 3, 1],
        [7, 3, 2, 2],
    ]
    det = LUDecomposition(A).determinant()
    chk = Matrix44(*A)
    assert chk.determinant() == det
