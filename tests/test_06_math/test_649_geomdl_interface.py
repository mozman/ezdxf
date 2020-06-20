# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
from geomdl.fitting import interpolate_curve
from ezdxf.math import BSpline, global_bspline_interpolation


def test_from_geomdl_curve_to_ezdxf_bspline():
    curve = interpolate_curve([(0, 0), (0, 10), (10, 10), (10, 0)], degree=3)
    bspline = BSpline.from_geomdl_curve(curve)
    assert bspline.degree == 3
    assert len(bspline.control_points) == 4
    assert len(bspline.knots()) == 8  # count + order


def test_from_ezdxf_bspline_to_geomdl_curve():
    bspline = global_bspline_interpolation([(0, 0), (0, 10), (10, 10), (10, 0)], degree=3)
    curve = bspline.geomdl_curve()
    assert curve.degree == 3
    assert len(curve.ctrlpts) == 4
    assert len(curve.knotvector) == 8  # count + order


if __name__ == '__main__':
    pytest.main([__file__])
