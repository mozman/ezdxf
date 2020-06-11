# Copyright (c) 2018-2020 Manfred Moitzi
# License: MIT License
from typing import Iterable, Tuple, List, Sequence, Union, Any
from itertools import repeat
import math

__all__ = [
    'Matrix', 'gauss_vector_solver', 'gauss_matrix_solver', 'gauss_jordan_solver', 'gauss_jordan_inverse',
    'LUDecomposition',
]


def zip_to_list(*args) -> Iterable[List]:
    for e in zip(*args):  # returns immutable tuples
        yield list(e)  # need mutable list


MatrixData = List[List[float]]
Shape = Tuple[int, int]


def copy_float_matrix(A) -> MatrixData:
    if isinstance(A, Matrix):
        A = A.matrix
    return [[float(v) for v in row] for row in A]


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
                return
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

    def __str__(self) -> str:
        return '[{}]'.format(', '.join([str(row) for row in self.rows()]))

    def __repr__(self) -> str:
        return f'Matrix(matrix={self.__str__()})'

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

    def inverse(self) -> 'Matrix':
        return gauss_jordan_inverse(self)

    def gauss_vector_solver(self, vector: Iterable[float]) -> List[float]:
        return gauss_vector_solver(self.matrix, vector)

    def gauss_matrix_solver(self, matrix: Iterable[Iterable[float]]) -> 'Matrix':
        return gauss_matrix_solver(self.matrix, matrix)

    def gauss_jordan_solver(self, matrix: Iterable[Iterable[float]]) -> Tuple['Matrix', 'Matrix']:
        return gauss_jordan_solver(self.matrix, matrix)


def gauss_vector_solver(A: Iterable[Iterable[float]], B: Iterable[float]) -> List[float]:
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
    # copy input data
    A = copy_float_matrix(A)
    B = list(B)
    num = len(A)
    if len(A[0]) != num:
        raise ValueError('Matrix has to have same row and column count.')
    if len(B) != num:
        raise ValueError('Item count of vector has to be equal to row count of matrix.')

    # inplace modification of A & B
    _build_upper_triangle(A, B)
    return _backsubstitution(A, B)


def gauss_matrix_solver(A: Iterable[Iterable[float]], B: Iterable[Iterable[float]]) -> Matrix:
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
    # copy input data
    A = copy_float_matrix(A)
    B = copy_float_matrix(B)

    num = len(A)
    if len(A[0]) != num:
        raise ValueError('Matrix has to have same row and column count.')
    if len(B) != num:
        raise ValueError('Row count of matrices has to match.')

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


def _backsubstitution(A: MatrixData, B: List[float]) -> List[float]:
    """ Solve equation A . x = B for an upper triangular matrix A by backsubstitution.

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


def gauss_jordan_solver(A: Iterable[Iterable[float]], B: Iterable[Iterable[float]]) -> Tuple[Matrix, Matrix]:
    # copy input data
    A = copy_float_matrix(A)
    B = copy_float_matrix(B)

    n = len(A)
    m = len(B[0])
    icol = 0
    irow = 0
    col_indices = [0] * n
    row_indices = [0] * n
    ipiv = [0] * n

    for i in range(n):
        big = 0.0
        for j in range(n):
            if ipiv[j] != 1:
                for k in range(n):
                    if ipiv[k] == 0:
                        if abs(A[j][k]) >= big:
                            big = abs(A[j][k])
                            irow = j
                            icol = k

        ipiv[icol] += 1
        if irow != icol:
            A[irow], A[icol] = A[icol], A[irow]
            B[irow], B[icol] = B[icol], B[irow]

        row_indices[i] = irow
        col_indices[i] = icol

        if math.isclose(A[icol][icol], 0.0):
            raise ZeroDivisionError('Singular Matrix')

        pivinv = 1.0 / A[icol][icol]
        A[icol][icol] = 1.0
        A[icol] = [v * pivinv for v in A[icol]]
        B[icol] = [v * pivinv for v in B[icol]]
        for row in range(n):
            if row == icol:
                continue
            dum = A[row][icol]
            A[row][icol] = 0.0
            for col in range(n):
                A[row][col] -= A[icol][col] * dum
            for col in range(m):
                B[row][col] -= B[icol][col] * dum

    for i in range(n - 1, -1, -1):
        irow = row_indices[i]
        icol = col_indices[i]
        if irow != icol:
            for row in A:
                row[irow], row[icol] = row[icol], row[irow]
    return Matrix(matrix=A), Matrix(matrix=B)


def gauss_jordan_inverse(A: Iterable[Iterable[float]]) -> Matrix:
    if isinstance(A, Matrix):
        A = A.matrix
    else:
        A = list(A)
    nrows = len(A)
    return gauss_jordan_solver(A, repeat([0.0], nrows))[0]


TINY = 1e-12


class LUDecomposition:
    def __init__(self, A: Iterable[Iterable[float]]):
        lu = copy_float_matrix(A)
        n = len(lu)
        det = 1.0
        index = []

        # find max value for each row, raises ZeroDivisionError for singular matrix!
        scaling = [1.0 / max(abs(v) for v in row) for row in lu]

        for k in range(n):
            big = 0.0
            imax = k
            for i in range(n):
                temp = scaling[i] * abs(lu[i][k])
                if temp > big:
                    big = temp
                    imax = i

            if k != imax:
                for col in range(n):
                    temp = lu[imax][col]
                    lu[imax][col] = lu[k][col]
                    lu[k][col] = temp

                det = -det
                scaling[imax] = scaling[k]

            index.append(imax)
            if lu[k][k] == 0.0:
                lu[k][k] = TINY
            for row in range(k + 1, n):
                temp = lu[row][k] / lu[k][k]
                lu[row][k] = temp
                for col in range(k + 1, n):
                    lu[row][col] -= temp * lu[k][col]

        self.index: List[int] = index
        self.matrix: MatrixData = lu
        self._det = det

    @property
    def nrows(self) -> int:
        return len(self.matrix)

    def solve_vector(self, B: Iterable[float]) -> List[float]:
        X = [float(v) for v in B]
        lu = self.matrix
        index = self.index
        n = self.nrows
        ii = 0

        if len(X) != n:
            raise ValueError('Item count of vector has to be equal to row count of matrix.')

        for i in range(n):
            ip = index[i]
            sum_ = X[ip]
            X[ip] = X[i]
            if ii != 0:
                for j in range(ii - 1, i):
                    sum_ -= lu[i][j] * X[j]
            elif sum_ != 0.0:
                ii = i + 1
            X[i] = sum_

        for row in range(n - 1, -1, -1):
            sum_ = X[row]
            for col in range(row + 1, n):
                sum_ -= lu[row][col] * X[col]
            X[row] = sum_ / lu[row][row]
        return X

    def solve_matrix(self, B: Iterable[Iterable[float]]) -> Matrix:
        if not isinstance(B, Matrix):
            B = Matrix(matrix=[list(row) for row in B])
        if B.nrows != self.nrows:
            raise ValueError('Item count of vector has to be equal to row count of matrix.')

        return Matrix(matrix=[self.solve_vector(col) for col in B.cols()]).transpose()

    def inverse(self) -> Matrix:
        return self.solve_matrix(Matrix.identity(shape=(self.nrows, self.nrows)))

    def determinant(self) -> float:
        det = self._det
        lu = self.matrix
        for i in range(self.nrows):
            det *= lu[i][i]
        return det
