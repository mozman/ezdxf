# Copyright (c) 2020-2024, Manfred Moitzi
# License: MIT License
from typing import Iterable
import pytest
import math
import numpy as np

from ezdxf.math.linalg import (
    Matrix,
    detect_banded_matrix,
    compact_banded_matrix,
    BandedMatrixLU,
    banded_matrix,
)
from ezdxf.math.legacy import gauss_vector_solver

BANDED_MATRIX = Matrix(
    matrix=[
        [3, 1, 0, 0, 0, 0, 0],
        [4, 1, 5, 0, 0, 0, 0],
        [9, 2, 6, 5, 0, 0, 0],
        [0, 3, 5, 8, 9, 0, 0],
        [0, 0, 7, 9, 3, 2, 0],
        [0, 0, 0, 3, 8, 4, 6],
        [0, 0, 0, 0, 2, 4, 4],
    ]
)
TRICKY = Matrix(
    matrix=[
        [3, 1, 0, 0, 0, 0, 1],
        [4, 1, 5, 0, 0, 0, 0],
        [9, 2, 6, 5, 0, 0, 0],
        [0, 3, 5, 8, 9, 0, 0],
        [0, 0, 7, 9, 3, 2, 0],
        [0, 0, 0, 3, 8, 4, 6],
        [0, 1, 0, 0, 2, 4, 4],
    ]
)


def are_close_vectors(
    v1: Iterable[float], v2: Iterable[float], abs_tol: float = 1e-12
):
    for i, j in zip(v1, v2):
        assert math.isclose(i, j, abs_tol=abs_tol)


def test_detect_banded_matrix():
    m1, m2 = detect_banded_matrix(BANDED_MATRIX)
    assert (m1, m2) == (2, 1)

    m1, m2 = detect_banded_matrix(TRICKY, check_all=False)
    assert (m1, m2) == (2, 1)

    m1, m2 = detect_banded_matrix(TRICKY, check_all=True)
    assert (m1, m2) == (5, 6)

    assert detect_banded_matrix(Matrix(shape=(10, 10))) == (0, 0)

    identity = Matrix.identity(shape=(10, 10))
    assert detect_banded_matrix(identity) == (0, 0)


def test_compact_banded_matrix():
    m1, m2 = detect_banded_matrix(BANDED_MATRIX)
    m = compact_banded_matrix(BANDED_MATRIX, m1, m2)
    assert m.ncols == 4
    assert m.nrows == 7
    assert m.col(0) == [0, 0, 9, 3, 7, 3, 2]
    assert m.col(1) == [0, 4, 2, 5, 9, 8, 4]
    assert m.col(2) == [3, 1, 6, 8, 3, 4, 4]
    assert m.col(3) == [1, 5, 5, 9, 2, 6, 0]


B1 = [5, 3, 2, 6, 8, 2, 1]
B2 = [9, 1, 7, 6, 4, 5, 0]
B3 = [0, 9, 3, 7, 1, 9, 9]

CHK1 = gauss_vector_solver(BANDED_MATRIX.matrix, B1)
CHK2 = gauss_vector_solver(BANDED_MATRIX.matrix, B2)
CHK3 = gauss_vector_solver(BANDED_MATRIX.matrix, B3)


def test_solve_banded_matrix_vector():
    m, m1, m2 = banded_matrix(BANDED_MATRIX)
    lu = BandedMatrixLU(m, m1, m2)
    are_close_vectors(lu.solve_vector(B1), CHK1)
    are_close_vectors(lu.solve_vector(B2), CHK2)
    are_close_vectors(lu.solve_vector(B3), CHK3)


def test_solve_banded_matrix_matrix():
    m, m1, m2 = banded_matrix(BANDED_MATRIX)
    lu = BandedMatrixLU(m, m1, m2)
    mat_B = np.array(list(zip(B1, B2, B3)))
    r = lu.solve_matrix(mat_B)
    are_close_vectors(r.col(0), CHK1)
    are_close_vectors(r.col(1), CHK2)
    are_close_vectors(r.col(2), CHK3)


if __name__ == "__main__":
    pytest.main([__file__])
