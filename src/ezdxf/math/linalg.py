# Copyright (c) 2018-2020 Manfred Moitzi
# License: MIT License
from typing import Iterable, Tuple, List, Sequence, Union, Any
from itertools import repeat
import math

__all__ = ['Matrix', 'gauss_vector_solver', 'gauss_matrix_solver']


def zip_to_list(*args) -> Iterable[List]:
    for e in zip(*args):  # returns immutable tuples
        yield list(e)  # need mutable list


MatrixData = List[List[float]]
Shape = Tuple[int, int]


class Matrix:
    """
    Simple unoptimized Matrix implementation.

    Initialization:

        - Matrix(shape=(rows, cols)) -> Matrix filled with zeros
        - Matrix(matrix[, shape=(rows, cols)]) -> Matrix by copy a Matrix and optional reshape
        - Matrix([[row_0], [row_1], ..., [row_n]]) -> Matrix from List[List[float]]
        - Matrix([a1, a2, ..., an], shape=(rows, cols)) -> Matrix from List[float] and shape

    """

    def __init__(self, items: Any = None, shape: Shape = None, matrix: MatrixData = None):
        self.matrix: MatrixData = matrix
        self.abs_tol: float = 1e-12
        if items is None:
            if shape is not None:
                self.matrix = Matrix.reshape(repeat(0.), shape).matrix
            else:  # items is None, shape is None
                pass
        elif isinstance(items, Matrix):
            if shape is None:
                shape = items.shape
            self.matrix = Matrix.reshape(items, shape=shape).matrix
        else:
            items = list(items)
            try:
                self.matrix = [list(row) for row in items]
            except TypeError:
                self.matrix = Matrix.reshape(items, shape).matrix

    def __iter__(self) -> Iterable[float]:
        for row in self.matrix:
            yield from row

    def __copy__(self) -> 'Matrix':
        m = Matrix()
        m.abs_tol = self.abs_tol
        m.matrix = [list(row) for row in self.rows()]
        return m

    @staticmethod
    def reshape(items: Iterable[float], shape: Shape) -> 'Matrix':
        items = iter(items)
        rows, cols = shape
        return Matrix(matrix=[[next(items) for _ in range(cols)] for _ in range(rows)])

    @property
    def nrows(self) -> int:
        return len(self.matrix)

    @property
    def ncols(self) -> int:
        return len(self.matrix[0])

    @property
    def shape(self) -> Shape:
        return self.nrows, self.ncols

    def row(self, index) -> List[float]:
        return self.matrix[index]

    def col(self, index) -> List[float]:
        return [row[index] for row in self.matrix]

    def rows(self) -> MatrixData:
        return self.matrix

    def cols(self) -> MatrixData:
        return [self.col(i) for i in range(self.ncols)]

    def set_row(self, index: int, items: List[float]) -> None:
        if len(items) != self.ncols:
            raise ValueError('Invalid item count')
        self.matrix[index] = items

    def set_col(self, index: int, items: List[float]) -> None:
        for row, item in zip(self.rows(), items):
            row[index] = item

    def set_diag(self, value: float = 1.0, row_offset: int = 0, col_offset: int = 0):
        for index in range(max(self.nrows, self.ncols)):
            try:
                self.matrix[index + row_offset][index + col_offset] = value
            except IndexError:
                return

    @classmethod
    def identity(cls, shape: Shape) -> 'Matrix':
        m = Matrix(shape=shape)
        m.set_diag(1.0)
        return m

    def append_row(self, items: Sequence[float]) -> None:
        if self.matrix is None:
            self.matrix = [list(items)]
        elif len(items) == self.ncols:
            self.matrix.append(items)
        else:
            raise ValueError('Invalid item count.')

    def append_col(self, items: Sequence[float]) -> None:
        if self.matrix is None:
            self.matrix = [[item] for item in items]
        elif len(items) == self.nrows:
            for row, item in zip(self.matrix, items):
                row.append(item)
        else:
            raise ValueError('Invalid item count.')

    def swap_rows(self, a: int, b: int) -> None:
        """ Swap rows `a` and `b` inplace. """
        m = self.matrix
        m[a], m[b] = m[b], m[a]

    def swap_cols(self, a: int, b: int) -> None:
        """ Swap columns `a` and `b` inplace. """
        for row in self.rows():
            row[a], row[b] = row[b], row[a]

    def __getitem__(self, item: Tuple[int, int]) -> float:
        row, col = item
        return self.matrix[row][col]

    def __setitem__(self, key: Tuple[int, int], value: float):
        row, col = key
        self.matrix[row][col] = value

    def __eq__(self, other: 'Matrix') -> bool:
        if not isinstance(other, Matrix):
            raise TypeError('Only comparable to class Matrix.')
        if self.shape != other.shape:
            raise TypeError('Matrices has to have the same shape.')
        for row1, row2 in zip(self.matrix, other.matrix):
            for item1, item2 in zip(row1, row2):
                if not math.isclose(item1, item2, abs_tol=self.abs_tol):
                    return False
        return True

    def __mul__(self, other: Union['Matrix', float]) -> 'Matrix':
        if isinstance(other, Matrix):
            matrix = Matrix(
                matrix=[[sum(a * b for a, b in zip(X_row, Y_col)) for Y_col in zip(*other.matrix)] for X_row in
                        self.matrix])
        else:
            factor = float(other)
            matrix = Matrix(matrix=[[item * factor for item in row] for row in self.matrix])
        return matrix

    __imul__ = __mul__

    def __add__(self, other: Union['Matrix', float]) -> 'Matrix':
        if isinstance(other, Matrix):
            matrix = Matrix.reshape([a + b for a, b in zip(self, other)], shape=self.shape)
        else:
            value = float(other)
            matrix = Matrix(matrix=[[item + value for item in row] for row in self.matrix])
        return matrix

    __iadd__ = __add__

    def __sub__(self, other: Union['Matrix', float]) -> 'Matrix':
        if isinstance(other, Matrix):
            matrix = Matrix.reshape([a - b for a, b in zip(self, other)], shape=self.shape)
        else:
            value = float(other)
            matrix = Matrix(matrix=[[item - value for item in row] for row in self.matrix])
        return matrix

    __isub__ = __sub__

    def transpose(self) -> 'Matrix':
        return Matrix(matrix=list(zip_to_list(*self.matrix)))

    def gauss_vector_solver(self, col: Sequence[float]) -> List[float]:
        return gauss_vector_solver(self.matrix, col)

    def gauss_matrix_solver(self, matrix: Sequence) -> 'Matrix':
        if self.nrows != len(matrix):
            raise ValueError('Row count of matrices do not match.')
        return gauss_matrix_solver(self.matrix, matrix)


def gauss_vector_solver(A: Sequence[Sequence[float]], B: Sequence[float]) -> List[float]:
    """
    Solves a nxn Matrix A . x = B, for vector B with n elements. A, B stay unmodified.

    Args:
        A: matrix [[a11, a12, ..., a1n],
                   [a21, a22, ..., a2n],
                   [a21, a22, ..., a2n],
                   ...
                   [an1, an2, ..., ann],]
        B: [b1, b2, ..., bn]

    Returns: result vector x

    """
    if isinstance(A, Matrix):
        A = A.matrix
    n = len(A)
    if len(A[0]) != n:
        raise ValueError('Matrix A has to have same row and column count.')
    if len(B) != n:
        raise ValueError('Item count of vector B has to be equal to row count of matrix A.')
    # copy input data
    A = [list(row) for row in A]
    B = list(B)
    # inplace modification of A & B
    _build_upper_triangle(A, B)
    return _backsubstitution(A, B)


def gauss_matrix_solver(A: Sequence[Sequence[float]], B: Sequence[Sequence[float]]) -> Matrix:
    """
    Solves a nxn Matrix A . x = B, for nxm Matrix B. A, B stay unmodified.

    Args:
        A: matrix [[a11, a12, ..., a1n],
                   [a21, a22, ..., a2n],
                   [a21, a22, ..., a2n],
                   ...
                   [an1, an2, ..., ann]]
        B: matrix [[b11, b12, ..., b1m],
                   [b21, b22, ..., b2m],
                   ...
                   [bn1, bn2, ..., bnm]]

    Returns: result matrix x

    """
    if isinstance(A, Matrix):
        A = A.matrix

    n = len(A)
    if len(A[0]) != n:
        raise ValueError('Matrix A has to have same row and column count.')
    if len(B) != n:
        raise ValueError('Row count of matrix B has to be equal to row count of matrix A.')

    # copy input data
    A = [list(row) for row in A]
    B = [list(row) for row in B]
    # inplace modification of A & B
    _build_upper_triangle(A, B)

    columns = Matrix(matrix=B).cols()
    result = Matrix()
    for col in columns:
        result.append_col(_backsubstitution(A, col))
    return result


def _build_upper_triangle(A: MatrixData, B: List) -> None:
    """ Build upper triangle for backsubstitution. Modifies A and B inplace!

    Args:
         A: row major matrix
         B: vector of floats or row major matrix

    """
    n = len(A)
    try:
        bcols = len(B[0])
    except TypeError:
        bcols = 1

    for i in range(0, n):
        # Search for maximum in this column
        max_element = abs(A[i][i])
        max_row = i
        for k in range(i + 1, n):
            value = abs(A[k][i])
            if value > max_element:
                max_element = value
                max_row = k

        # Swap maximum row with current row
        A[max_row], A[i] = A[i], A[max_row]
        B[max_row], B[i] = B[i], B[max_row]

        # Make all rows below this one 0 in current column
        for k in range(i + 1, n):
            c = -A[k][i] / A[i][i]
            for j in range(i, n):
                if i == j:
                    A[k][j] = 0
                else:
                    A[k][j] += c * A[i][j]
            if bcols == 1:
                B[k] += c * B[i]
            else:
                for col in range(bcols):
                    B[k][col] += c * B[i][col]


def _backsubstitution(A: MatrixData, B: List[float]) -> List[float]:
    """ Solve equation A . x = B for an upper triangular matrix A by backsubstitution.

    Args:
        A: row major matrix
        B: vector of floats

    """
    n = len(A)
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = B[i] / A[i][i]
        for k in range(i - 1, -1, -1):
            B[k] -= A[k][i] * x[i]
    return x
