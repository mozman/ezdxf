import pytest
from ezdxf.algebra.bspline import bspline_control_frame
from ezdxf.algebra.bspline import uniform_t_vector, chord_length_t_vector, centripetal_t_vector
from ezdxf.algebra.bspline import control_frame_knots
from ezdxf.algebra.bspline import bspline_basis, bspline_basis_vector, bspline_vertex
from ezdxf.algebra.bspline import BSpline
from ezdxf.algebra.base import is_close, is_close_points

POINTS1 = [(1, 1), (2, 4), (4, 1), (7, 6)]
POINTS2 = [(1, 1), (2, 4), (4, 1), (7, 6), (5, 8), (3, 3), (1, 7)]


@pytest.fixture(params=[POINTS1, POINTS2])
def fit_points(request):
    return request.param


def test_uniform_t_array(fit_points):
    t_vector = list(uniform_t_vector(fit_points))
    assert len(t_vector) == len(fit_points)
    assert t_vector[0] == 0.
    assert t_vector[-1] == 1.
    for t1, t2 in zip(t_vector, t_vector[1:]):
        assert t1 <= t2


def test_chord_length_t_array(fit_points):
    t_vector = list(chord_length_t_vector(fit_points))
    assert len(t_vector) == len(fit_points)
    assert t_vector[0] == 0.
    assert t_vector[-1] == 1.
    for t1, t2 in zip(t_vector, t_vector[1:]):
        assert t1 <= t2


def test_centripetal_length_t_array(fit_points):
    t_vector = list(centripetal_t_vector(fit_points))
    assert len(t_vector) == len(fit_points)
    assert t_vector[0] == 0.
    assert t_vector[-1] == 1.
    for t1, t2 in zip(t_vector, t_vector[1:]):
        assert t1 <= t2


def test_control_frame_knot_values(fit_points):
    n = len(fit_points)
    for p in (2, 3):  # degree
        order = p + 1
        t_vector = uniform_t_vector(fit_points)
        knots = list(control_frame_knots(n, p, t_vector))
        assert len(knots) == n + p + 2
        assert len(set(knots[:order])) == 1, 'first order elements have to be equal'
        assert len(set(knots[-order:])) == 1, 'last order elements have to be equal'
        for k1, k2 in zip(knots, knots[1:]):
            assert k1 <= k2


def test_bspline_basis():
    knots = [0, 1, 2, 3]
    assert bspline_basis(0, 0, 1, knots) == 0
    assert bspline_basis(1, 0, 1, knots) == 1
    assert bspline_basis(2, 0, 1, knots) == 0
    assert bspline_basis(1, 1, 1, knots) == 0
    assert bspline_basis(1.5, 1, 1, knots) == .5
    assert bspline_basis(2, 1, 1, knots) == 1
    assert bspline_basis(2.5, 1, 1, knots) == .5
    assert bspline_basis(3, 1, 1, knots) == 0


def test_compare_basis(fit_points):
    degree = 3
    spline = BSpline(fit_points, order=degree+1)
    n = len(fit_points)
    segments = 10
    du = spline.max_t / segments
    knots = list(spline.knots[1:])  # spline.knots is 1-based
    for index in range(segments+1):
        u = du * index
        basis_vector1 = spline.basis(u)
        basis_vector2 = list(bspline_basis_vector(u, n, degree=degree, knots=knots))
        assert len(basis_vector2) == n
        for b1, b2 in zip(basis_vector1[1:n+1], basis_vector2):
            assert is_close(b1, b2)

        p1 = spline.point(u)
        p2 = bspline_vertex(u, degree=degree, control_points=fit_points, knots=knots)
        assert is_close_points(p1, p2)


def test_control_frame():
    spline = bspline_control_frame(POINTS1, degree=3)
    assert len(spline.control_points) == len(POINTS1)
