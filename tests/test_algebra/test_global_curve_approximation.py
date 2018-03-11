# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from ezdxf.algebra import Vector, is_close
from ezdxf.algebra.bspline import bspline_basis_vector, Basis, uniform_t_vector, control_frame_knots
from ezdxf.algebra.bspline import bspline_control_frame_approx

POINTS2 = [(1, 1), (2, 4), (4, 1), (7, 6), (5, 8), (3, 3), (1, 7)]


def test_basis_vector_N_ip():
    degree = 3
    fit_points = Vector.list(POINTS2)  # data points D
    n = len(fit_points) - 1
    t_vector = list(uniform_t_vector(fit_points))
    knots = list(control_frame_knots(n, degree, t_vector))
    should_count = len(fit_points) - 2  # target control point count
    h = should_count - 1
    spline = Basis(knots, order=degree+1, count=len(fit_points))
    matrix_N = [spline.basis(t) for t in t_vector]

    for k in range(1, n):
        basis_vector = bspline_basis_vector(u=t_vector[k], count=len(fit_points), degree=degree, knots=knots)
        for i in range(1, h):
            assert is_close(matrix_N[k][i], basis_vector[i])


def test_control_frame_approx():
    points = [(1, 1), (2, 4), (4, 1), (7, 6), (5, 8), (3, 3), (1, 7), (2, 10), (5, 12), (7, 8)]
    spline = bspline_control_frame_approx(points, 7, degree=3)
    assert len(spline.control_points) == 7
    assert spline.control_points[0] == points[0]
    assert spline.control_points[-1] == points[-1]
