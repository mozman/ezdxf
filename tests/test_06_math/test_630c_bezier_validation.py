"""Invalid flattening inputs must fail before unbounded subdivision."""

import math


import pytest


from ezdxf.acc import USE_C_EXT


from ezdxf.math import Vec3


from ezdxf.math._bezier3p import Bezier3P


from ezdxf.math._bezier4p import Bezier4P

CURVES = [(Bezier3P, 3), (Bezier4P, 4)]


if USE_C_EXT:
    from ezdxf.acc.bezier3p import Bezier3P as CBezier3P
    from ezdxf.acc.bezier4p import Bezier4P as CBezier4P

    CURVES += [(CBezier3P, 3), (CBezier4P, 4)]


@pytest.fixture(params=CURVES)
def curve_class(request):
    return request.param


@pytest.fixture
def curve(curve_class):
    cls, count = curve_class
    return cls(Vec3.list([(0, 0), (0, 1), (1, 1), (1, 0)][:count]))


@pytest.mark.parametrize("distance", [0, -1, math.nan, math.inf, -math.inf])
def test_invalid_distance(curve, distance):
    with pytest.raises(ValueError, match="distance"):
        list(curve.flattening(distance))


@pytest.mark.parametrize("segments", [0, -1, -100])
def test_non_positive_segments(curve, segments):
    with pytest.raises(ValueError, match="segments"):
        list(curve.flattening(0.1, segments))


@pytest.mark.parametrize("segments", [0.5, 1.5, math.nan, math.inf, "4"])
def test_non_integer_segments(curve, segments):
    with pytest.raises(TypeError):
        list(curve.flattening(0.1, segments))


@pytest.mark.parametrize("points", [[], [Vec3()], [Vec3()] * 5])
def test_invalid_control_point_count(curve_class, points):
    cls, _ = curve_class
    with pytest.raises(ValueError, match="control points required"):
        cls(points)


def test_native_tuple_input_warns_and_converts(curve_class):
    cls, count = curve_class
    if not cls.__module__.startswith("ezdxf.acc."):
        pytest.skip("Python implementation requires vectors")
    points = [(0, 0), (0, 1), (1, 1), (1, 0)][:count]
    with pytest.warns(DeprecationWarning, match="Vec2 or Vec3"):
        curve = cls(points)
    assert curve.control_points == Vec3.tuple(points)
