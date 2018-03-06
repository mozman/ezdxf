# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from itertools import repeat


class Matrix(object):
    """
    Simple unoptimized Matrix math.

    Initialization:

    Matrix(shape=(rows, cols))

        matrix filled with zeros

    Matrix(matrix[, shape=(rows, cols)])

        copy constructor and reshape

    Matrix([[row_0], [row_1], ..., [row_n]])

    Matrix([a1, a2, ..., an], shape=(rows, cols))

    """
    def __init__(self, items=None, shape=None, matrix=None):
        self.matrix = matrix
        if items is None:
            if shape is not None:
                self.matrix = Matrix.reshape(repeat(0.), shape).matrix
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

    def __iter__(self):
        for row in self.matrix:
            for item in row:
                yield item

    @staticmethod
    def reshape(items, shape):
        items = iter(items)
        rows, cols = shape
        return Matrix(matrix=[[next(items) for _ in range(cols)] for _ in range(rows)])

    @property
    def nrows(self):
        return len(self.matrix)

    @property
    def ncols(self):
        return len(self.matrix[0])

    @property
    def shape(self):
        return self.nrows, self.ncols

    def row(self, index):
        return self.matrix[index]

    def col(self, index):
        return [row[index] for row in self.matrix]

    def rows(self):
        return self.matrix

    def cols(self):
        return [self.col(i) for i in range(self.ncols)]

    def append_row(self, items):
        if self.matrix is None:
            self.matrix = [list(items)]
        elif len(items) == self.ncols:
            self.matrix.append(items)
        else:
            raise ValueError('Invalid item count.')

    def append_col(self, items):
        if self.matrix is None:
            self.matrix = [[item] for item in items]
        elif len(items) == self.nrows:
            for row, item in zip(self.matrix, items):
                row.append(item)
        else:
            raise ValueError('Invalid item count.')

    def __getitem__(self, item):
        row, col = item
        return self.matrix[row][col]

    def __setitem__(self, key, value):
        row, col = key
        self.matrix[row][col] = value

    def __eq__(self, other):
        if not isinstance(other, Matrix):
            raise TypeError('Only comparable to class Matrix.')
        if self.shape != other.shape:
            raise TypeError('Matrices has to have the same shape.')
        for row1, row2 in zip(self.matrix, other.matrix):
            if list(row1) != list(row2):
                return False
        return True

    def __mul__(self, other):
        if isinstance(other, Matrix):
            matrix = Matrix(matrix=[[sum(a * b for a, b in zip(X_row, Y_col)) for Y_col in zip(*other.matrix)] for X_row in self.matrix])
        else:
            factor = float(other)
            matrix = Matrix.reshape([item*factor for item in self], shape=self.shape)
        return matrix
    __imul__ = __mul__

    def __add__(self, other):
        if isinstance(other, Matrix):
            matrix = Matrix.reshape([a+b for a, b in zip(self, other)], shape=self.shape)
        else:
            other = float(other)
            matrix = Matrix.reshape([item+other for item in self], shape=self.shape)
        return matrix
    __iadd__ = __add__

    def __sub__(self, other):
        if isinstance(other, Matrix):
            matrix = Matrix.reshape([a-b for a, b in zip(self, other)], shape=self.shape)
        else:
            other = float(other)
            matrix = Matrix.reshape([item-other for item in self], shape=self.shape)
        return matrix
    __isub__ = __sub__

    def transpose(self):
        return Matrix(matrix=list(zip(*self.matrix)))

    def gauss(self, col):
        m = Matrix(self)
        m.append_col(col)
        return gauss(m.matrix)

    def gauss_matrix(self, matrix):
        B = Matrix(matrix)
        if self.nrows != B.nrows:
            raise ValueError('Row count of matrices do not match.')
        result = [self.gauss(col) for col in B.cols()]
        return Matrix(zip(*result))


def gauss(A):
    """
    Solves a nxn Matrix A x = b, Matrix has 1 column more than rows.

    Args:
        A: matrix [[a11, a12, ..., a1n, b1],
                   [a21, a22, ..., a2n, b2],
                   [a21, a22, ..., a2n, b3],
                   ...
                   [an1, an2, ..., ann, bn],]

    Returns: x vector as list

    """
    n = len(A)

    for i in range(0, n):
        # Search for maximum in this column
        maxEl = abs(A[i][i])
        maxRow = i
        for k in range(i + 1, n):
            if abs(A[k][i]) > maxEl:
                maxEl = abs(A[k][i])
                maxRow = k

        # Swap maximum row with current row (column by column)
        for k in range(i, n + 1):
            tmp = A[maxRow][k]
            A[maxRow][k] = A[i][k]
            A[i][k] = tmp

        # Make all rows below this one 0 in current column
        for k in range(i + 1, n):
            c = -A[k][i] / A[i][i]
            for j in range(i, n + 1):
                if i == j:
                    A[k][j] = 0
                else:
                    A[k][j] += c * A[i][j]

    # Solve equation Ax=b for an upper triangular matrix A
    x = [0] * n
    for i in range(n - 1, -1, -1):
        x[i] = A[i][n] / A[i][i]
        for k in range(i - 1, -1, -1):
            A[k][n] -= A[k][i] * x[i]
    return x

