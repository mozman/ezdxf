#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
import math
from ezdxf.math import X_AXIS, Y_AXIS, Z_AXIS, Vec3
from ezdxf.math.construct3d import inscribe_circle_tangent_length, bending_angle


class TestInscribeCircle:
    @pytest.mark.parametrize(
        "d1,d2,r",
        [
            (X_AXIS, Y_AXIS, 0.0),
            (X_AXIS, X_AXIS, 1.0),
            (X_AXIS, -X_AXIS, 1.0),
        ],
        ids=[
            "Radius = 0",
            "colinear directions",
            "opposite colinear directions",
        ],
    )
    def test_returns_zero_for_invalid_input(self, d1, d2, r):
        assert inscribe_circle_tangent_length(d1, d2, r) == 0.0

    @pytest.mark.parametrize(
        "ax1,ax2",
        [
            (X_AXIS, Y_AXIS),
            (X_AXIS, Z_AXIS),
            (Y_AXIS, X_AXIS),
            (Y_AXIS, Z_AXIS),
        ],
    )
    @pytest.mark.parametrize("r", [1.0, -1.0, 2.0, -2.0])
    def test_90_deg_directions(self, r, ax1, ax2):
        assert inscribe_circle_tangent_length(ax1, ax2, r) == pytest.approx(
            abs(r)
        )

    def test_45_deg_direction(self):
        assert inscribe_circle_tangent_length(
            X_AXIS, Vec3(1, 1, 0), 1.0
        ) == pytest.approx(2.41421356237309515)


def test_bending_angle():
    pi2 = math.pi / 2.0
    a = X_AXIS
    assert bending_angle(a, Y_AXIS, normal=Z_AXIS) == pytest.approx(pi2)
    assert bending_angle(a, Y_AXIS, normal=-Z_AXIS) == pytest.approx(-pi2)
    assert bending_angle(a, Z_AXIS, normal=Y_AXIS) == pytest.approx(-pi2)
    assert bending_angle(a, Z_AXIS, normal=-Y_AXIS) == pytest.approx(pi2)
    b = Vec3(0, 1, 1)
    normal = a.cross(b)
    assert bending_angle(a, b, normal=normal) == pytest.approx(pi2)
    assert bending_angle(a, b, normal=-normal) == pytest.approx(-pi2)


if __name__ == "__main__":
    pytest.main([__file__])
