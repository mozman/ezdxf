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
