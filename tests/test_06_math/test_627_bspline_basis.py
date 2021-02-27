#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
import math
from ezdxf.math.bspline import bspline_basis_vector, open_uniform_knot_vector
from ezdxf.math._bspline import Basis
from ezdxf.acc import USE_C_EXT

basis_functions = [Basis]

if USE_C_EXT:
    pass


@pytest.fixture(params=basis_functions)
def basis_cls(request):
    return request.param


def make_knots(count, degree):
    return list(open_uniform_knot_vector(count, order=degree + 1))


def make_basic_func(count, degree, cls):
    knots = make_knots(count, degree)
    return cls(knots=knots, order=degree + 1, count=count)


def test_property_exists(basis_cls):
    degree = 3
    count = 10
    knots = make_knots(count, degree)
    basis_func = basis_cls(knots=knots, order=degree + 1, count=count)
    assert basis_func.degree == degree
    assert basis_func.order == degree + 1
    assert basis_func.max_t == max(knots)
    assert basis_func.knots == knots
    assert basis_func.weights == []
    assert basis_func.is_rational is False


def test_bspline_basis_vector(basis_cls):
    degree = 3
    count = 10
    knots = make_knots(count, degree)
    max_t = max(knots)
    basis_func = basis_cls(knots=knots, order=degree + 1, count=count)
    for u in (0, 2, 2.5, 3.5, 4, max_t):
        basis = bspline_basis_vector(u, count=count, degree=degree, knots=knots)
        basis2 = basis_func.basis_vector(u)
        assert len(basis) == len(basis2)
        for v1, v2 in zip(basis, basis2):
            assert v1 == pytest.approx(v2)


def test_find_span(basis_cls):
    degree = 3
    basis_func = make_basic_func(10, degree, basis_cls)
    for u in [0, 2, 2.5, 3.5, 4]:
        result = basis_func.find_span(u)
        span = math.floor(u) + degree
        assert result == span
    assert basis_func.find_span(basis_func.max_t) == 9


if __name__ == '__main__':
    pytest.main([__file__])
