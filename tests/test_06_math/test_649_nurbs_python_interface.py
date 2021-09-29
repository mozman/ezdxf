# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.math import (
    BSpline,
    global_bspline_interpolation,
    rational_bspline_from_arc,
    Vec3,
)


def test_from_nurbs_python_curve_to_ezdxf_bspline():
    from geomdl.fitting import interpolate_curve

    curve = interpolate_curve([(0, 0), (0, 10), (10, 10), (10, 0)], degree=3)
    bspline = BSpline.from_nurbs_python_curve(curve)
    assert bspline.degree == 3
    assert len(bspline.control_points) == 4
    assert len(bspline.knots()) == 8  # count + order


def test_from_ezdxf_bspline_to_nurbs_python_curve_non_rational():
    bspline = global_bspline_interpolation(
        [(0, 0), (0, 10), (10, 10), (10, 0)], degree=3
    )

    # to NURBS-Python
    curve = bspline.to_nurbs_python_curve()
    assert curve.degree == 3
    assert len(curve.ctrlpts) == 4
    assert len(curve.knotvector) == 8  # count + order
    assert curve.rational is False

    # and back to ezdxf
    spline = BSpline.from_nurbs_python_curve(curve)
    assert spline.degree == 3
    assert len(spline.control_points) == 4
    assert len(spline.knots()) == 8  # count + order


def test_from_ezdxf_bspline_to_nurbs_python_curve_rational():
    bspline = rational_bspline_from_arc(
        center=Vec3(0, 0), radius=2, start_angle=0, end_angle=90
    )

    # to NURBS-Python
    curve = bspline.to_nurbs_python_curve()
    assert curve.degree == 2
    assert len(curve.ctrlpts) == 3
    assert len(curve.knotvector) == 6  # count + order
    assert curve.rational is True
    assert curve.weights == [1.0, 0.7071067811865476, 1.0]

    # and back to ezdxf
    spline = BSpline.from_nurbs_python_curve(curve)
    assert spline.degree == 2
    assert len(spline.control_points) == 3
    assert len(spline.knots()) == 6  # count + order
    assert spline.weights() == (1.0, 0.7071067811865476, 1.0)


if __name__ == "__main__":
    pytest.main([__file__])
