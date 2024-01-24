#  Copyright (c) 2021-2024, Manfred Moitzi
#  License: MIT License

import pytest
import math
import numpy as np

pytest.importorskip("ezdxf.acc.bspline")

from ezdxf.math._bspline import Basis as PyBasis, Evaluator as PyEvaluator
from ezdxf.acc.bspline import Basis as CyBasis, Evaluator as CyEvaluator
from ezdxf.math import Vec3, close_vectors

COUNT = 10
ORDER = 4
KNOTS = tuple(range(COUNT + ORDER))
WEIGHTS = [1.0, 0.7, 0.6, 0.5, 0.5, 0.5, 0.5, 0.6, 0.7, 1.0]
POINTS = [
    Vec3(0.181, 0.753, 0.15),
    Vec3(0.527, 0.944, 0.176),
    Vec3(1.326, 1.015, 0.184),
    Vec3(1.086, 0.607, 0.185),
    Vec3(1.286, 1.468, 0.255),
    Vec3(1.451, 0.596, 0.175),
    Vec3(1.282, 0.703, 0.17),
    Vec3(0.79, 0.77, 0.169),
    Vec3(1.622, 0.831, 0.172),
    Vec3(1.099, 0.922, 0.163),
]


@pytest.fixture
def t_vector():
    return list(np.linspace(0, max(KNOTS), 20))


@pytest.fixture
def py_basis():
    return PyBasis(KNOTS, ORDER, COUNT)


@pytest.fixture
def cy_basis():
    return CyBasis(KNOTS, ORDER, COUNT)


@pytest.fixture
def py_wbasis():
    return PyBasis(KNOTS, ORDER, COUNT, WEIGHTS)


@pytest.fixture
def cy_wbasis():
    return CyBasis(KNOTS, ORDER, COUNT, WEIGHTS)


def test_find_span(py_basis, cy_basis, t_vector):
    for u in t_vector:
        assert py_basis.find_span(u) == cy_basis.find_span(u)


def test_cython_knots(cy_basis):
    for _ in range(10):
        assert cy_basis.knots == KNOTS
        assert cy_basis.max_t == KNOTS[-1]


def test_basis_funcs(py_basis, cy_basis, t_vector):
    for u in t_vector:
        span1 = py_basis.find_span(u)
        p = py_basis.basis_funcs(span1, u)
        span2 = cy_basis.find_span(u)
        c = cy_basis.basis_funcs(span2, u)
        assert (
            all(math.isclose(a, b, abs_tol=1e-12) for a, b in zip(p, c)) is True
        )


def test_basis_vector(py_basis, cy_basis, t_vector):
    for u in t_vector:
        p = py_basis.basis_vector(u)
        c = list(cy_basis.basis_vector(u))
        assert (
            all(math.isclose(a, b, abs_tol=1e-12) for a, b in zip(p, c)) is True
        )


def test_weighted_basis_vector(py_wbasis, cy_wbasis, t_vector):
    for u in t_vector:
        p = py_wbasis.basis_vector(u)
        c = list(cy_wbasis.basis_vector(u))
        assert (
            all(math.isclose(a, b, abs_tol=1e-12) for a, b in zip(p, c)) is True
        )


def test_basis_funcs_derivatives(py_basis, cy_basis, t_vector):
    for u in t_vector:
        span = py_basis.find_span(u)
        pl = py_basis.basis_funcs_derivatives(span, u, 2)
        span = cy_basis.find_span(u)
        cl = cy_basis.basis_funcs_derivatives(span, u, 2)
        for p, c in zip(pl, cl):
            assert (
                all(math.isclose(a, b, abs_tol=1e-12) for a, b in
                    zip(p, c)) is True
            )


def test_weighted_basis_funcs_derivatives(py_wbasis, cy_wbasis, t_vector):
    for u in t_vector:
        span = py_wbasis.find_span(u)
        pl = py_wbasis.basis_funcs_derivatives(span, u, 2)
        span = cy_wbasis.find_span(u)
        cl = cy_wbasis.basis_funcs_derivatives(span, u, 2)
        for p, c in zip(pl, cl):
            assert (
                all(math.isclose(a, b, abs_tol=1e-12) for a, b in
                    zip(p, c)) is True
            )


@pytest.fixture
def py_eval(py_basis):
    return PyEvaluator(py_basis, POINTS)


@pytest.fixture
def cy_eval(cy_basis):
    return CyEvaluator(cy_basis, POINTS)


def test_point_evaluator(py_eval, cy_eval, t_vector):
    py_points = list(py_eval.points(t_vector))
    cy_points = list(cy_eval.points(t_vector))
    assert close_vectors(py_points, cy_points) is True


def test_derivative_evaluator(py_eval, cy_eval, t_vector):
    py_ders = list(py_eval.derivatives(t_vector, 2))
    cy_ders = list(cy_eval.derivatives(t_vector, 2))
    for d1, d2 in zip(py_ders, cy_ders):
        assert close_vectors(d1, d2) is True

@pytest.fixture
def py_weval(py_wbasis):
    return PyEvaluator(py_wbasis, POINTS)


@pytest.fixture
def cy_weval(cy_wbasis):
    return CyEvaluator(cy_wbasis, POINTS)


def test_weighted_point_evaluator(py_weval, cy_weval, t_vector):
    py_points = list(py_weval.points(t_vector))
    cy_points = list(cy_weval.points(t_vector))
    assert close_vectors(py_points, cy_points) is True


def test_weighted_derivative_evaluator(py_weval, cy_weval, t_vector):
    py_ders = list(py_weval.derivatives(t_vector, 2))
    cy_ders = list(cy_weval.derivatives(t_vector, 2))
    for d1, d2 in zip(py_ders, cy_ders):
        assert close_vectors(d1, d2) is True


if __name__ == "__main__":
    pytest.main([__file__])
