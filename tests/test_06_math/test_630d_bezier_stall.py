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


def test_non_finite_curve_fails_without_recursion_explosion(curve_class):
    cls, count = curve_class
    curve = cls([Vec3(math.nan, 0)] * count)
    with pytest.raises(RecursionError):
        list(curve.flattening(0.1))


@pytest.mark.parametrize("cls,count", [(Bezier3P, 3), (Bezier4P, 4)])
def test_unresolvable_midpoint_terminates(cls, count):
    class UnresolvableCurve(cls):
        def _get_curve_point(self, t):
            return Vec3(0, 1 if t > 0.5 else 0)

    curve = UnresolvableCurve([Vec3()] * count)
    with pytest.raises(RecursionError, match="precision"):
        list(curve.flattening(0.1))
