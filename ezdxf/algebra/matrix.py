# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from typing import Iterable, Tuple, List, Sequence, Union, Any
from itertools import repeat


def zip_to_list(*args) -> Iterable[List]:
    for e in zip(*args):  # returns immutable tuples
        yield list(e)  # need mutable list


class Matrix:
    """
    Simple unoptimized Matrix math.

    Initialization:

        - Matrix(shape=(rows, cols)) -> Matrix filled with zeros
        - Matrix(matrix[, shape=(rows, cols)]) -> Matrix by copy a Matrix and optional reshape
        - Matrix([[row_0], [row_1], ..., [row_n]]) -> Matrix from List[List[float]]
        - Matrix([a1, a2, ..., an], shape=(rows, cols)) -> Matrix from List[float] and shape

    """

    def __init__(self, items: Any = None,
                 shape: Tuple[int, int] = None,
                 matrix: List[List[float]] = None):
        self.matrix = matrix  # type: List[List[float]]
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
            for item in row:
                yield item

    @staticmethod
    def reshape(items: Iterable[float], shape: Tuple[int, int]) -> 'Matrix':
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
    def shape(self) -> Tuple[int, int]:
        return self.nrows, self.ncols

    def row(self, index) -> List[float]:
        return self.matrix[index]

    def col(self, index) -> List[float]:
        return [row[index] for row in self.matrix]

    def rows(self) -> List[List[float]]:
        return self.matrix

    def cols(self) -> List[List[float]]:
        return [self.col(i) for i in range(self.ncols)]

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
            if list(row1) != list(row2):
                return False
        return True

    def __mul__(self, other: Union['Matrix', float]) -> 'Matrix':
        if isinstance(other, Matrix):
            matrix = Matrix(
                matrix=[[sum(a * b for a, b in zip(X_row, Y_col)) for Y_col in zip(*other.matrix)] for X_row in
                        self.matrix])
        else:
            factor = float(other)
            matrix = Matrix.reshape([item * factor for item in self], shape=self.shape)
        return matrix

    __imul__ = __mul__

    def __add__(self, other: Union['Matrix', float]) -> 'Matrix':
        if isinstance(other, Matrix):
            matrix = Matrix.reshape([a + b for a, b in zip(self, other)], shape=self.shape)
        else:
            other = float(other)
            matrix = Matrix.reshape([item + other for item in self], shape=self.shape)
        return matrix

    __iadd__ = __add__

    def __sub__(self, other: Union['Matrix', float]) -> 'Matrix':
        if isinstance(other, Matrix):
            matrix = Matrix.reshape([a - b for a, b in zip(self, other)], shape=self.shape)
        else:
            other = float(other)
            matrix = Matrix.reshape([item - other for item in self], shape=self.shape)
        return matrix

    __isub__ = __sub__

    def transpose(self) -> 'Matrix':
        return Matrix(matrix=list(zip_to_list(*self.matrix)))

    def gauss(self, col):
        m = Matrix(self)
        m.append_col(col)
        return gauss(m.matrix)

    def gauss_matrix(self, matrix) -> 'Matrix':
        B = Matrix(matrix)
        if self.nrows != B.nrows:
            raise ValueError('Row count of matrices do not match.')
        result = [self.gauss(col) for col in B.cols()]
        return Matrix(items=zip(*result))


def gauss(matrix: List[List[float]]) -> List[float]:
    """
    Solves a nxn Matrix A x = b, Matrix has 1 column more than rows.

    Args:
        matrix: matrix [[a11, a12, ..., a1n, b1],
                   [a21, a22, ..., a2n, b2],
                   [a21, a22, ..., a2n, b3],
                   ...
                   [an1, an2, ..., ann, bn],]

    Returns: x vector as list

    """
    n = len(matrix)

    for i in range(0, n):
        # Search for maximum in this column
        max_element = abs(matrix[i][i])
        max_row = i
        for k in range(i + 1, n):
            if abs(matrix[k][i]) > max_element:
                max_element = abs(matrix[k][i])
                max_row = k

        # Swap maximum row with current row (column by column)
        for k in range(i, n + 1):
            tmp = matrix[max_row][k]
            matrix[max_row][k] = matrix[i][k]
            matrix[i][k] = tmp

        # Make all rows below this one 0 in current column
        for k in range(i + 1, n):
            c = -matrix[k][i] / matrix[i][i]
            for j in range(i, n + 1):
                if i == j:
                    matrix[k][j] = 0
                else:
                    matrix[k][j] += c * matrix[i][j]

    # Solve equation Ax=b for an upper triangular matrix A
    x = [0.] * n
    for i in range(n - 1, -1, -1):
        x[i] = matrix[i][n] / matrix[i][i]
        for k in range(i - 1, -1, -1):
            matrix[k][n] -= matrix[k][i] * x[i]
    return x
