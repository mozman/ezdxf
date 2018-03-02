import pytest
from ezdxf.algebra.bspline import bspline_control_frame
from ezdxf.algebra.bspline import uniform_t_vector, chord_length_t_vector, centripetal_t_vector
from ezdxf.algebra.bspline import control_frame_knots

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


def test_control_frame():
    spline = bspline_control_frame(POINTS1, degree=3)
    assert len(spline.control_points) == len(POINTS1)
