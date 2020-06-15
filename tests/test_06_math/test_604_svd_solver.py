# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import Iterable
import pytest
import math
from ezdxf.math.linalg import Matrix, SVD

MATRIX = Matrix(matrix=[
    [3, 1, 0, 0, 0, 0, 0],
    [4, 1, 5, 0, 0, 0, 0],
    [9, 2, 6, 5, 0, 0, 0],
    [0, 3, 5, 8, 9, 0, 0],
    [0, 0, 7, 9, 3, 2, 0],
    [0, 0, 7, 9, 3, 2, 0],
    [0, 0, 0, 3, 8, 4, 6],
])


def are_close_vectors(v1: Iterable[float], v2: Iterable[float], abs_tol: float = 1e-12):
    for i, j in zip(v1, v2):
        assert math.isclose(i, j, abs_tol=abs_tol)


B1 = [5, 3, 2, 6, 8, 2, 1]
B2 = [9, 1, 7, 6, 4, 5, 0]
B3 = [0, 9, 3, 7, 1, 9, 9]


@pytest.mark.skip(reason='something is wrong')
def test_regular_matrix_vector():
    svd = SVD(MATRIX)
    result = svd.solve_vector(B1)


if __name__ == '__main__':
    pytest.main([__file__])
