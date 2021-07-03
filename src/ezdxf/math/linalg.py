# Copyright (c) 2018-2021 Manfred Moitzi
# License: MIT License
from typing import Iterable, Tuple, List, Sequence, Union, Any, Iterator, cast
from functools import lru_cache
from itertools import repeat
import math
import reprlib

__all__ = [
    "Matrix",
    "gauss_vector_solver",
    "gauss_matrix_solver",
    "gauss_jordan_solver",
    "gauss_jordan_inverse",
    "LUDecomposition",
    "freeze_matrix",
    "tridiagonal_vector_solver",
    "tridiagonal_matrix_solver",
    "detect_banded_matrix",
    "compact_banded_matrix",
    "BandedMatrixLU",
    "banded_matrix",
    "quadratic_equation",
    "binomial_coefficient",
]


def zip_to_list(*args) -> Iterable[List]:
    for e in zip(*args):  # returns immutable tuples
        yield list(e)  # need mutable list


MatrixData = List[List[float]]
IterableMatrixData = Iterable[Iterable[float]]
FrozenMatrixData = Tuple[Tuple[float, ...]]
Shape = Tuple[int, int]


def copy_float_matrix(A) -> MatrixData:
    if isinstance(A, Matrix):
        A = A.matrix
    return [[float(v) for v in row] for row in A]


def freeze_matrix(A: Union[IterableMatrixData, "Matrix"]) -> "Matrix":
    """Returns a frozen matrix, all data is stored in immutable tuples."""
    if isinstance(A, Matrix):
        A = A.matrix
    m = Matrix()
    m.matrix = tuple(tuple(float(v) for v in row) for row in A)  # type: ignore
    return m


@lru_cache(maxsize=128)
def binomial_coefficient(k: int, i: int) -> float:
    # (c) Onur Rauf Bingol <orbingol@gmail.com>, NURBS-Python, MIT-License
    """Computes the binomial coefficient (denoted by `k choose i`).

    Please see the following website for details:
    http://mathworld.wolfram.com/BinomialCoefficient.html

    Args:
        k: size of the set of distinct elements
        i: size of the subsets

    """
    # Special case
    if i > k:
        return float(0)
    # Compute binomial coefficient
    k_fact: int = math.factorial(k)
    i_fact: int = math.factorial(i)
    k_i_fact: int = math.factorial(k - i)
    return float(k_fact / (k_i_fact * i_fact))


class Matrix:
    """Basic matrix implementation without any optimization for speed of
    memory usage. Matrix data is stored in row major order, this means in a
    list of rows, where each row is a list of floats. Direct access to the
    data is accessible by the attribute :attr:`Matrix.matrix`.

    The matrix can be frozen by function :func:`freeze_matrix` or method
    :meth:`Matrix.freeze`, than the data is stored in immutable tuples.

    Initialization:

        - Matrix(shape=(rows, cols)) ... new matrix filled with zeros
        - Matrix(matrix[, shape=(rows, cols)]) ... from copy of matrix and optional reshape
        - Matrix([[row_0], [row_1], ..., [row_n]]) ... from Iterable[Iterable[float]]
        - Matrix([a1, a2, ..., an], shape=(rows, cols)) ... from Iterable[float] and shape

    """

    __slots__ = ("matrix", "abs_tol")

    def __init__(
        self, items: Any = None, shape: Shape = None, matrix: MatrixData = None
    ):
        self.matrix: MatrixData = matrix  # type: ignore
        self.abs_tol: float = 1e-12
        if items is None:
            if shape is not None:
                self.matrix = Matrix.reshape(repeat(0.0), shape).matrix
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
                self.matrix = Matrix.reshape(items,
                    shape).matrix  # type: ignore

    def __iter__(self) -> Iterator[float]:
        for row in self.matrix:
            yield from row

    def __copy__(self) -> "Matrix":
        m = Matrix()
        m.abs_tol = self.abs_tol
        m.matrix = [list(row) for row in self.rows()]
        return m

    def __str__(self) -> str:
        return str(self.matrix)

    def __repr__(self) -> str:
        return f"Matrix({reprlib.repr(self.matrix)})"

    @staticmethod
    def reshape(items: Iterable[float], shape: Shape) -> "Matrix":
        """Returns a new matrix for iterable `items` in the configuration of
        `shape`.
        """
        items = iter(items)
        rows, cols = shape
        return Matrix(
            matrix=[[next(items) for _ in range(cols)] for _ in range(rows)]
        )

    @property
    def nrows(self) -> int:
        """Count of matrix rows."""
        return len(self.matrix)

    @property
    def ncols(self) -> int:
        """Count of matrix columns."""
        return len(self.matrix[0])

    @property
    def shape(self) -> Shape:
        """Shape of matrix as (n, m) tuple for n rows and m columns."""
        return self.nrows, self.ncols

    def row(self, index: int) -> List[float]:
        """Returns row `index` as list of floats."""
        return self.matrix[index]

    def iter_row(self, index: int) -> Iterator[float]:
        """Yield values of row `index`."""
        return iter(self.matrix[index])

    def col(self, index: int) -> List[float]:
        """Return column `index` as list of floats."""
        return [row[index] for row in self.matrix]

    def iter_col(self, index: int) -> Iterator[float]:
        """Yield values of column `index`."""
        return (row[index] for row in self.matrix)

    def diag(self, index: int) -> List[float]:
        """Returns diagonal `index` as list of floats.

        An `index` of 0 specifies the main diagonal, negative values
        specifies diagonals below the main diagonal and positive values
        specifies diagonals above the main diagonal.

        e.g. given a 4x4 matrix:

        - index 0 is [00, 11, 22, 33],
        - index -1 is [10, 21, 32] and
        - index +1 is [01, 12, 23]

        """
        return list(self.iter_diag(index))

    def iter_diag(self, index: int) -> Iterator[float]:
        """Yield values of diagonal `index`, see also :meth:`diag`."""
        get = self.__getitem__
        col_offset = max(index, 0)
        row_offset = abs(min(index, 0))
        for i in range(max(self.nrows, self.ncols)):
            try:
                yield get((i + row_offset, i + col_offset))
            except IndexError:
                break

    def rows(self) -> MatrixData:
        """Return a list of all rows."""
        return self.matrix

    def cols(self) -> MatrixData:
        """Return a list of all columns."""
        return [self.col(i) for i in range(self.ncols)]

    def set_row(
        self, index: int, items: Union[float, Sequence[float]] = 1.0
    ) -> None:
        """Set row values to a fixed value or from an iterable of floats."""
        if isinstance(items, (float, int)):
            items = [float(items)] * self.ncols

        if len(items) != self.ncols:
            raise ValueError("Invalid item count")
        self.matrix[index] = list(items)

    def set_col(
        self, index: int, items: Union[float, Iterable[float]] = 1.0
    ) -> None:
        """Set column values to a fixed value or from an iterable of floats."""
        if isinstance(items, (float, int)):
            items = [float(items)] * self.nrows

        for row, item in zip(self.rows(), items):
            row[index] = item

    def set_diag(
        self, index: int = 0, items: Union[float, Iterable[float]] = 1.0
    ) -> None:
        """Set diagonal values to a fixed value or from an iterable of floats.

        An `index` of ``0`` specifies the main diagonal, negative values
        specifies diagonals below the main diagonal and positive values
        specifies diagonals above the main diagonal.

        e.g. given a 4x4 matrix:
        index ``0`` is [00, 11, 22, 33],
        index ``-1`` is [10, 21, 32] and
        index ``+1`` is [01, 12, 23]

        """
        if isinstance(items, (float, int)):
            items = repeat(float(items))

        col_offset: int = max(index, 0)
        row_offset: int = abs(min(index, 0))

        for index, value in zip(range(max(self.nrows, self.ncols)), items):
            try:
                self.matrix[index + row_offset][index + col_offset] = value
            except IndexError:
                return

    @classmethod
    def identity(cls, shape: Shape) -> "Matrix":
        """Returns the identity matrix for configuration `shape`."""
        m = Matrix(shape=shape)
        m.set_diag(0, 1.0)
        return m

    def append_row(self, items: Sequence[float]) -> None:
        """Append a row to the matrix."""
        if self.matrix is None:
            self.matrix = [list(items)]
        elif len(items) == self.ncols:
            self.matrix.append(list(items))
        else:
            raise ValueError("Invalid item count.")

    def append_col(self, items: Sequence[float]) -> None:
        """Append a column to the matrix."""
        if self.matrix is None:
            self.matrix = [[item] for item in items]
        elif len(items) == self.nrows:
            for row, item in zip(self.matrix, items):
                row.append(item)
        else:
            raise ValueError("Invalid item count.")

    def swap_rows(self, a: int, b: int) -> None:
        """Swap rows `a` and `b` inplace."""
        m = self.matrix
        m[a], m[b] = m[b], m[a]

    def swap_cols(self, a: int, b: int) -> None:
        """Swap columns `a` and `b` inplace."""
        for row in self.rows():
            row[a], row[b] = row[b], row[a]

    def freeze(self) -> "Matrix":
        """Returns a frozen matrix, all data is stored in immutable tuples."""
        return freeze_matrix(self.matrix)

    def lu_decomp(self) -> "LUDecomposition":
        """Returns the `LU decomposition`_ as :class:`LUDecomposition` object,
        a faster linear equation solver.

        """
        return LUDecomposition(self.matrix)

    def __getitem__(self, item: Tuple[int, int]) -> float:
        """Get value by (row, col) index tuple, fancy slicing as known from
        numpy is not supported.

        """
        row, col = item
        return self.matrix[row][col]

    def __setitem__(self, item: Tuple[int, int], value: float):
        """Set value by (row, col) index tuple, fancy slicing as known from
        numpy is not supported.

        """
        row, col = item
        self.matrix[row][col] = value

    def __eq__(self, other: object) -> bool:
        """Returns ``True`` if matrices are equal, tolerance value for
        comparison is adjustable by the attribute :attr:`Matrix.abs_tol`.

        """
        if not isinstance(other, Matrix):
            raise TypeError("Matrix class required.")
        if self.shape != other.shape:
            raise TypeError("Matrices have different shapes.")
        for row1, row2 in zip(self.matrix, other.matrix):
            for item1, item2 in zip(row1, row2):
                if not math.isclose(item1, item2, abs_tol=self.abs_tol):
                    return False
        return True

    def __mul__(self, other: Union["Matrix", float]) -> "Matrix":
        """Matrix multiplication by another matrix or a float, returns a new
        matrix.

        """
        if isinstance(other, Matrix):
            matrix = Matrix(
                matrix=[
                    [
                        sum(a * b for a, b in zip(X_row, Y_col))
                        for Y_col in zip(*other.matrix)
                    ]
                    for X_row in self.matrix
                ]
            )
        else:
            factor = float(other)
            matrix = Matrix(
                matrix=[[item * factor for item in row] for row in self.matrix]
            )
        return matrix

    __imul__ = __mul__

    def __add__(self, other: Union["Matrix", float]) -> "Matrix":
        """Matrix addition by another matrix or a float, returns a new matrix."""
        if isinstance(other, Matrix):
            matrix = Matrix.reshape(
                [a + b for a, b in zip(self, other)], shape=self.shape
            )
        else:
            value = float(other)
            matrix = Matrix(
                matrix=[[item + value for item in row] for row in self.matrix]
            )
        return matrix

    __iadd__ = __add__

    def __sub__(self, other: Union["Matrix", float]) -> "Matrix":
        """Matrix subtraction by another matrix or a float, returns a new
        matrix.

        """
        if isinstance(other, Matrix):
            matrix = Matrix.reshape(
                [a - b for a, b in zip(self, other)], shape=self.shape
            )
        else:
            value = float(other)
            matrix = Matrix(
                matrix=[[item - value for item in row] for row in self.matrix]
            )
        return matrix

    __isub__ = __sub__

    def transpose(self) -> "Matrix":
        """Returns a new transposed matrix."""
        return Matrix(matrix=list(zip_to_list(*self.matrix)))

    def inverse(self) -> "Matrix":
        """Returns inverse of matrix as new object."""
        if self.nrows != self.ncols:
            raise TypeError("Inverse of non-square matrix not supported.")

        if self.nrows > 10:
            return LUDecomposition(self.matrix).inverse()
        else:  # faster for small matrices
            return gauss_jordan_inverse(self.matrix)

    def determinant(self) -> float:
        """Returns determinant of matrix, raises :class:`ZeroDivisionError`
        if matrix is singular.

        """
        return LUDecomposition(self.matrix).determinant()


def quadratic_equation(a: float, b: float, c: float) -> Tuple[float, float]:
    discriminant = math.sqrt(b ** 2 - 4 * a * c)
    return ((-b + discriminant) / (2.0 * a)), ((-b - discriminant) / (2.0 * a))


def gauss_vector_solver(
    A: Iterable[Iterable[float]], B: Iterable[float]
) -> List[float]:
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


def gauss_matrix_solver(
    A: IterableMatrixData, B: IterableMatrixData
) -> Matrix:
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


def _build_upper_triangle(A: MatrixData, B: List) -> None:
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


def _backsubstitution(A: MatrixData, B: List[float]) -> List[float]:
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


def gauss_jordan_solver(
    A: IterableMatrixData, B: IterableMatrixData
) -> Tuple[Matrix, Matrix]:
    """Solves the linear equation system given by a nxn Matrix A . x = B,
    right-hand side quantities as nxm Matrix B by the `Gauss-Jordan`_ algorithm,
    which is the slowest of all, but it is very reliable. Returns a copy of the
    modified input matrix `A` and the result matrix `x`.

    Internally used for matrix inverse calculation.

    Args:
        A: matrix [[a11, a12, ..., a1n], [a21, a22, ..., a2n], [a21, a22, ..., a2n],
            ... [an1, an2, ..., ann]]
        B: matrix [[b11, b12, ..., b1m], [b21, b22, ..., b2m], ... [bn1, bn2, ..., bnm]]

    Returns:
        2-tuple of :class:`Matrix` objects

    Raises:
        ZeroDivisionError: singular matrix

    """
    # copy input data
    matrix_a = copy_float_matrix(A)
    matrix_b = copy_float_matrix(B)

    n = len(matrix_a)
    m = len(matrix_b[0])

    if len(matrix_a[0]) != n:
        raise ValueError("A square nxn matrix A is required.")
    if len(matrix_b) != n:
        raise ValueError("Row count of matrices A and B has to match.")

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
                        if abs(matrix_a[j][k]) >= big:
                            big = abs(matrix_a[j][k])
                            irow = j
                            icol = k

        ipiv[icol] += 1
        if irow != icol:
            matrix_a[irow], matrix_a[icol] = matrix_a[icol], matrix_a[irow]
            matrix_b[irow], matrix_b[icol] = matrix_b[icol], matrix_b[irow]

        row_indices[i] = irow
        col_indices[i] = icol

        pivinv = 1.0 / matrix_a[icol][icol]
        matrix_a[icol][icol] = 1.0
        matrix_a[icol] = [v * pivinv for v in matrix_a[icol]]
        matrix_b[icol] = [v * pivinv for v in matrix_b[icol]]
        for row in range(n):
            if row == icol:
                continue
            dum = matrix_a[row][icol]
            matrix_a[row][icol] = 0.0
            for col in range(n):
                matrix_a[row][col] -= matrix_a[icol][col] * dum
            for col in range(m):
                matrix_b[row][col] -= matrix_b[icol][col] * dum

    for i in range(n - 1, -1, -1):
        irow = row_indices[i]
        icol = col_indices[i]
        if irow != icol:
            for _row in matrix_a:
                _row[irow], _row[icol] = _row[icol], _row[irow]
    return Matrix(matrix=matrix_a), Matrix(matrix=matrix_b)


def gauss_jordan_inverse(A: IterableMatrixData) -> Matrix:
    """Returns the inverse of matrix `A` as :class:`Matrix` object.

    .. hint::

        For small matrices (n<10) is this function faster than
        LUDecomposition(m).inverse() and as fast even if the decomposition is
        already done.

    Raises:
        ZeroDivisionError: singular matrix

    """
    if isinstance(A, Matrix):
        matrix_a = A.matrix
    else:
        matrix_a = list(A)
    nrows = len(matrix_a)
    return gauss_jordan_solver(matrix_a, repeat([0.0], nrows))[0]


class LUDecomposition:
    """Represents a `LU decomposition`_ matrix of A, raise :class:`ZeroDivisionError`
    for a singular matrix.

    This algorithm is a little bit faster than the `Gauss-Elimination`_
    algorithm using CPython and much faster when using pypy.

    The :attr:`LUDecomposition.matrix` attribute gives access to the matrix data
    as list of rows like in the :class:`Matrix` class, and the :attr:`LUDecomposition.index`
    attribute gives access to the swapped row indices.

    Args:
        A: matrix [[a11, a12, ..., a1n], [a21, a22, ..., a2n], [a21, a22, ..., a2n],
            ... [an1, an2, ..., ann]]

    raises:
        ZeroDivisionError: singular matrix

    """

    __slots__ = ("matrix", "index", "_det")

    def __init__(self, A: IterableMatrixData):
        lu: MatrixData = copy_float_matrix(A)
        n: int = len(lu)
        det: float = 1.0
        index: List[int] = []

        # find max value for each row, raises ZeroDivisionError for singular matrix!
        scaling: List[float] = [1.0 / max(abs(v) for v in row) for row in lu]

        for k in range(n):
            big: float = 0.0
            imax: int = k
            for i in range(k, n):
                temp: float = scaling[i] * abs(lu[i][k])
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
            for i in range(k + 1, n):
                temp = lu[i][k] / lu[k][k]
                lu[i][k] = temp
                for j in range(k + 1, n):
                    lu[i][j] -= temp * lu[k][j]

        self.index: List[int] = index
        self.matrix: MatrixData = lu
        self._det: float = det

    def __str__(self) -> str:
        return str(self.matrix)

    def __repr__(self) -> str:
        return f"{self.__class__} {reprlib.repr(self.matrix)}"

    @property
    def nrows(self) -> int:
        """Count of matrix rows (and cols)."""
        return len(self.matrix)

    def solve_vector(self, B: Iterable[float]) -> List[float]:
        """Solves the linear equation system given by the nxn Matrix A . x = B,
        right-hand side quantities as vector B with n elements.

        Args:
            B: vector [b1, b2, ..., bn]

        Returns:
            vector as list of floats

        """
        X: List[float] = [float(v) for v in B]
        lu: MatrixData = self.matrix
        index: List[int] = self.index
        n: int = self.nrows
        ii: int = 0

        if len(X) != n:
            raise ValueError(
                "Item count of vector B has to be equal to matrix row count."
            )

        for i in range(n):
            ip: int = index[i]
            sum_: float = X[ip]
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

    def solve_matrix(self, B: IterableMatrixData) -> Matrix:
        """Solves the linear equation system given by the nxn Matrix A . x = B,
        right-hand side quantities as nxm Matrix B.

        Args:
            B: matrix [[b11, b12, ..., b1m], [b21, b22, ..., b2m],
                ... [bn1, bn2, ..., bnm]]

        Returns:
            matrix as :class:`Matrix` object

        """
        if not isinstance(B, Matrix):
            matrix_b = Matrix(matrix=[list(row) for row in B])
        else:
            matrix_b = cast(Matrix, B)

        if matrix_b.nrows != self.nrows:
            raise ValueError("Row count of self and matrix B has to match.")

        return Matrix(
            matrix=[self.solve_vector(col) for col in matrix_b.cols()]
        ).transpose()

    def inverse(self) -> Matrix:
        """Returns the inverse of matrix as :class:`Matrix` object,
        raise :class:`ZeroDivisionError` for a singular matrix.

        """
        return self.solve_matrix(
            Matrix.identity(shape=(self.nrows, self.nrows)).matrix
        )

    def determinant(self) -> float:
        """Returns the determinant of matrix, raises :class:`ZeroDivisionError`
        if matrix is singular.

        """
        det: float = self._det
        lu: MatrixData = self.matrix
        for i in range(self.nrows):
            det *= lu[i][i]
        return det


def tridiagonal_vector_solver(
    A: IterableMatrixData, B: Iterable[float]
) -> List[float]:
    """Solves the linear equation system given by a tri-diagonal nxn Matrix
    A . x = B, right-hand side quantities as vector B. Matrix A is diagonal
    matrix defined by 3 diagonals [-1 (a), 0 (b), +1 (c)].

    Note: a0 is not used but has to be present, cn-1 is also not used and must
    not be present.

    If an :class:`ZeroDivisionError` exception occurs, the equation system can
    possibly be solved by :code:`BandedMatrixLU(A, 1, 1).solve_vector(B)`

    Args:
        A: diagonal matrix [[a0..an-1], [b0..bn-1], [c0..cn-1]] ::

            [[b0, c0, 0, 0, ...],
            [a1, b1, c1, 0, ...],
            [0, a2, b2, c2, ...],
            ... ]

        B: iterable of floats [[b1, b1, ..., bn]

    Returns:
        list of floats

    Raises:
        ZeroDivisionError: singular matrix

    """
    a, b, c = [list(v) for v in A]
    return _solve_tridiagonal_matrix(a, b, c, list(B))


def tridiagonal_matrix_solver(
    A: IterableMatrixData, B: IterableMatrixData
) -> Matrix:
    """Solves the linear equation system given by a tri-diagonal nxn Matrix
    A . x = B, right-hand side quantities as nxm Matrix B. Matrix A is diagonal
    matrix defined by 3 diagonals [-1 (a), 0 (b), +1 (c)].

    Note: a0 is not used but has to be present, cn-1 is also not used and must
    not be present.

    If an :class:`ZeroDivisionError` exception occurs, the equation system
    can possibly be solved by :code:`BandedMatrixLU(A, 1, 1).solve_vector(B)`

    Args:
        A: diagonal matrix [[a0..an-1], [b0..bn-1], [c0..cn-1]] ::

            [[b0, c0, 0, 0, ...],
            [a1, b1, c1, 0, ...],
            [0, a2, b2, c2, ...],
            ... ]

        B: matrix [[b11, b12, ..., b1m],
                   [b21, b22, ..., b2m],
                   ...
                   [bn1, bn2, ..., bnm]]

    Returns:
        matrix as :class:`Matrix` object

    Raises:
        ZeroDivisionError: singular matrix

    """
    a, b, c = [list(v) for v in A]
    if not isinstance(B, Matrix):
        matrix_b = Matrix(matrix=[list(row) for row in B])
    else:
        matrix_b = cast(Matrix, B)
    if matrix_b.nrows != len(b):
        raise ValueError("Row count of matrices A and B has to match.")

    return Matrix(
        matrix=[
            _solve_tridiagonal_matrix(a, b, c, col) for col in matrix_b.cols()
        ]
    ).transpose()


def _solve_tridiagonal_matrix(
    a: List[float], b: List[float], c: List[float], r: List[float]
) -> List[float]:
    """Solves the linear equation system given by a tri-diagonal
    Matrix(a, b, c) . x = r.

    Matrix configuration::

        [[b0, c0, 0, 0, ...],
        [a1, b1, c1, 0, ...],
        [0, a2, b2, c2, ...],
        ... ]

    Args:
        a: lower diagonal [a0 .. an-1], a0 is not used but has to be present
        b: central diagonal [b0 .. bn-1]
        c: upper diagonal [c0 .. cn-1], cn-1 is not used and must not be present
        r: right-hand side quantities

    Returns:
        vector x as list of floats

    Raises:
        ZeroDivisionError: singular matrix

    """
    n: int = len(a)
    u: List[float] = [0.0] * n
    gam: List[float] = [0.0] * n
    bet: float = b[0]
    u[0] = r[0] / bet
    for j in range(1, n):
        gam[j] = c[j - 1] / bet
        bet = b[j] - a[j] * gam[j]
        u[j] = (r[j] - a[j] * u[j - 1]) / bet

    for j in range((n - 2), -1, -1):
        u[j] -= gam[j + 1] * u[j + 1]
    return u


def banded_matrix(A: Matrix, check_all=True) -> Tuple[Matrix, int, int]:
    """Transform matrix A into a compact banded matrix representation.
    Returns compact representation as :class:`Matrix` object and
    lower- and upper band count m1 and m2.

    Args:
        A: input :class:`Matrix`
        check_all: check all diagonals if ``True`` or abort testing
            after first all zero diagonal if ``False``.

    """
    m1, m2 = detect_banded_matrix(A, check_all)
    m = compact_banded_matrix(A, m1, m2)
    return m, m1, m2


def detect_banded_matrix(A: Matrix, check_all=True) -> Tuple[int, int]:
    """Returns lower- and upper band count m1 and m2.

    Args:
        A: input :class:`Matrix`
        check_all: check all diagonals if ``True`` or abort testing
            after first all zero diagonal if ``False``.

    """

    def detect_m2() -> int:
        m2: int = 0
        for d in range(1, A.ncols):
            if any(A.iter_diag(d)):
                m2 = d
            elif not check_all:
                break
        return m2

    def detect_m1() -> int:
        m1: int = 0
        for d in range(1, A.nrows):
            if any(A.iter_diag(-d)):
                m1 = d
            elif not check_all:
                break
        return m1

    return detect_m1(), detect_m2()


def compact_banded_matrix(A: Matrix, m1: int, m2: int) -> Matrix:
    """Returns compact banded matrix representation as :class:`Matrix` object.

    Args:
        A: matrix to transform
        m1: lower band count, excluding main matrix diagonal
        m2: upper band count, excluding main matrix diagonal

    """
    if A.nrows != A.ncols:
        raise TypeError("Square matrix required.")

    m = Matrix()

    for d in range(m1, 0, -1):
        col = [0.0] * d
        col.extend(A.diag(-d))
        m.append_col(col)

    m.append_col(A.diag(0))

    for d in range(1, m2 + 1):
        col = A.diag(d)
        col.extend([0.0] * d)
        m.append_col(col)
    return m


class BandedMatrixLU:
    """Represents a LU decomposition of a compact banded matrix."""

    def __init__(self, A: Matrix, m1: int, m2: int):
        # upper triangle of LU decomposition
        self.upper: MatrixData = copy_float_matrix(A)
        self.m1: int = int(m1)
        self.m2: int = int(m2)

        # lower triangle of LU decomposition
        n: int = self.nrows
        self.lower: MatrixData = [[0.0] * m1 for _ in range(n)]
        self.index: List[int] = [0] * n
        self._det: float = 1.0

        m1 = self.m1
        m2 = self.m2
        upper: MatrixData = self.upper
        lower: MatrixData = self.lower

        mm: int = m1 + m2 + 1
        l: int = m1
        for i in range(m1):
            for j in range(m1 - i, mm):
                upper[i][j - l] = upper[i][j]
            l -= 1
            for j in range(mm - l - 1, mm):
                upper[i][j] = 0.0

        l = m1
        for k in range(n):
            dum = upper[k][0]
            i = k
            if l < n:
                l += 1
            for j in range(k + 1, l):
                if abs(upper[j][0]) > abs(dum):
                    dum = upper[j][0]
                    i = j
            self.index[k] = i + 1
            if i != k:
                self._det = -self._det
                for j in range(mm):
                    upper[k][j], upper[i][j] = upper[i][j], upper[k][j]

            for i in range(k + 1, l):
                dum = upper[i][0] / upper[k][0]
                lower[k][i - k - 1] = dum
                for j in range(1, mm):
                    upper[i][j - 1] = upper[i][j] - dum * upper[k][j]
                upper[i][mm - 1] = 0.0

    @property
    def nrows(self) -> int:
        """Count of matrix rows."""
        return len(self.upper)

    def solve_vector(self, B: Iterable[float]) -> List[float]:
        """Solves the linear equation system given by the banded nxn Matrix
        A . x = B, right-hand side quantities as vector B with n elements.

        Args:
            B: vector [b1, b2, ..., bn]

        Returns:
            vector as list of floats

        """
        x: List[float] = list(B)
        if len(x) != self.nrows:
            raise ValueError(
                "Item count of vector B has to be equal to matrix row count."
            )

        n: int = self.nrows
        m1: int = self.m1
        m2: int = self.m2
        index: List[int] = self.index
        al: MatrixData = self.lower
        au: MatrixData = self.upper

        mm: int = m1 + m2 + 1
        l: int = m1
        for k in range(n):
            j = index[k] - 1
            if j != k:
                x[k], x[j] = x[j], x[k]
            if l < n:
                l += 1
            for j in range(k + 1, l):
                x[j] -= al[k][j - k - 1] * x[k]

        l = 1
        for i in range(n - 1, -1, -1):
            dum = x[i]
            for k in range(1, l):
                dum -= au[i][k] * x[k + i]
            x[i] = dum / au[i][0]
            if l < mm:
                l += 1

        return x

    def solve_matrix(self, B: IterableMatrixData) -> Matrix:
        """
        Solves the linear equation system given by the banded nxn Matrix
        A . x = B, right-hand side quantities as nxm Matrix B.

        Args:
            B: matrix [[b11, b12, ..., b1m], [b21, b22, ..., b2m],
                ... [bn1, bn2, ..., bnm]]

        Returns:
            matrix as :class:`Matrix` object

        """
        if not isinstance(B, Matrix):
            matrix_b = Matrix(matrix=[list(row) for row in B])
        else:
            matrix_b = cast(Matrix, B)
        if matrix_b.nrows != self.nrows:
            raise ValueError("Row count of self and matrix B has to match.")

        return Matrix(
            matrix=[self.solve_vector(col) for col in matrix_b.cols()]
        ).transpose()

    def determinant(self) -> float:
        """Returns the determinant of matrix."""
        dd: float = self._det
        au: MatrixData = self.upper

        for i in range(0, len(au)):
            dd *= au[i][0]

        return dd
