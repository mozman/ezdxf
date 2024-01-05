# Copyright (c) 2018-2024, Manfred Moitzi
# License: MIT License
# legacy.py code is replaced by numpy - exists just for benchmarking, testing and nostalgia
from __future__ import annotations

from typing import (
    Iterable,
    Tuple,
    List,
    Sequence,
    Union,
    Any,
    cast,
    Optional,
)
from typing_extensions import TypeAlias
from itertools import repeat
import math
from .linalg import Matrix, MatrixData, NDArray

__all__ = [
    "gauss_vector_solver",
    "gauss_matrix_solver",
    "gauss_jordan_solver",
    "gauss_jordan_inverse",
    "LUDecomposition",
    "tridiagonal_vector_solver",
    "tridiagonal_matrix_solver",
    "detect_banded_matrix",
    "compact_banded_matrix",
    "BandedMatrixLU",
    "banded_matrix",
]


def copy_float_matrix(A) -> MatrixData:
    if isinstance(A, Matrix):
        A = A.matrix
    return [[float(v) for v in row] for row in A]


def gauss_vector_solver(A: MatrixData | NDArray, B: Iterable[float]) -> list[float]:
    """Solves the linear equation system given by a nxn Matrix A . x = B,
    right-hand side quantities as vector B with n elements by the
    `Gauss-Elimination`_ algorithm, which is faster than the `Gauss-Jordan`_
    algorithm. The speed improvement is more significant for solving multiple
    right-hand side quantities as matrix at once.

    Reference implementation for error checking.

    Args:
        A: matrix [[a11, a12, ..., a1n], [a21, a22, ..., a2n], [a21, a22, ..., a2n],
            ... [an1, an2, ..., ann]]
        B: vector [b1, b2, ..., bn]

    Returns:
        vector as list of floats

    Raises:
        ZeroDivisionError: singular matrix

    """
    # copy input data
    A = copy_float_matrix(A)
    B = list(B)
    num = len(A)
    if len(A[0]) != num:
        raise ValueError("A square nxn matrix A is required.")
    if len(B) != num:
        raise ValueError(
            "Item count of vector B has to be equal to matrix A row count."
        )

    # inplace modification of A & B
    _build_upper_triangle(A, B)
    return _backsubstitution(A, B)


def gauss_matrix_solver(A: MatrixData | NDArray, B: MatrixData | NDArray) -> Matrix:
    """Solves the linear equation system given by a nxn Matrix A . x = B,
    right-hand side quantities as nxm Matrix B by the `Gauss-Elimination`_
    algorithm, which is faster than the `Gauss-Jordan`_ algorithm.

    Reference implementation for error checking.

    Args:
        A: matrix [[a11, a12, ..., a1n], [a21, a22, ..., a2n], [a21, a22, ..., a2n],
            ... [an1, an2, ..., ann]]
        B: matrix [[b11, b12, ..., b1m], [b21, b22, ..., b2m], ... [bn1, bn2, ..., bnm]]

    Returns:
        matrix as :class:`Matrix` object

    Raises:
        ZeroDivisionError: singular matrix

    """
    # copy input data
    matrix_a = copy_float_matrix(A)
    matrix_b = copy_float_matrix(B)
    num = len(matrix_a)
    if len(matrix_a[0]) != num:
        raise ValueError("A square nxn matrix A is required.")
    if len(matrix_b) != num:
        raise ValueError("Row count of matrices A and B has to match.")

    # inplace modification of A & B
    _build_upper_triangle(matrix_a, matrix_b)

    columns = Matrix(matrix=matrix_b).cols()
    result = Matrix()
    for col in columns:
        result.append_col(_backsubstitution(matrix_a, col))

    return result


def _build_upper_triangle(A: MatrixData, B: list) -> None:
    """Build upper triangle for backsubstitution. Modifies A and B inplace!

    Args:
         A: row major matrix
         B: vector of floats or row major matrix

    """
    num = len(A)
    try:
        b_col_count = len(B[0])
    except TypeError:
        b_col_count = 1

    for i in range(0, num):
        # Search for maximum in this column
        max_element = abs(A[i][i])
        max_row = i
        for row in range(i + 1, num):
            value = abs(A[row][i])
            if value > max_element:
                max_element = value
                max_row = row

        # Swap maximum row with current row
        A[max_row], A[i] = A[i], A[max_row]
        B[max_row], B[i] = B[i], B[max_row]

        # Make all rows below this one 0 in current column
        for row in range(i + 1, num):
            c = -A[row][i] / A[i][i]
            for col in range(i, num):
                if i == col:
                    A[row][col] = 0
                else:
                    A[row][col] += c * A[i][col]
            if b_col_count == 1:
                B[row] += c * B[i]
            else:
                for col in range(b_col_count):
                    B[row][col] += c * B[i][col]


def _backsubstitution(A: MatrixData, B: list[float]) -> list[float]:
    """Solve equation A . x = B for an upper triangular matrix A by
    backsubstitution.

    Args:
        A: row major matrix
        B: vector of floats

    """
    num = len(A)
    x = [0.0] * num
    for i in range(num - 1, -1, -1):
        x[i] = B[i] / A[i][i]
        for row in range(i - 1, -1, -1):
            B[row] -= A[row][i] * x[i]
    return x
