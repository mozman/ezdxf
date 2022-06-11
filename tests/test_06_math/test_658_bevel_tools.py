#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
import math
from ezdxf.math import X_AXIS, Y_AXIS, Z_AXIS, Vec3
from ezdxf.math.construct3d import inscribe_circle_tangent_length, bending_angle
from ezdxf.path.tools import chamfer, chamfer2, fillet


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


class TestChamfer:
    def test_requires_three_points(self):
        with pytest.raises(ValueError):
            chamfer([Vec3(), Vec3()], 1.0)

    def test_one_chamfer(self):
        p = chamfer(Vec3.list([(0, 0), (5, 0), (5, 5)]), 1.0)
        points = list(p.flattening(0))
        assert points[0].isclose((0, 0))
        assert points[1].isclose((4.292893218813452, 0))
        assert points[2].isclose((5, 0.7071067811865475))
        assert points[3].isclose((5, 5))
        assert len(points) == 4

    def test_two_chamfers(self):
        p = chamfer(Vec3.list([(0, 0), (5, 0), (5, 5), (10, 5)]), 1.0)
        points = list(p.flattening(0))
        assert points[3].isclose((5, 4.292893218813452))
        assert points[4].isclose((5.7071067811865475, 5))
        assert points[5].isclose((10, 5))
        assert len(points) == 6


class TestChamfer2:
    def test_requires_three_points(self):
        with pytest.raises(ValueError):
            chamfer2([Vec3(), Vec3()], 1.0, 1.0)

    def test_one_chamfer(self):
        p = chamfer2(Vec3.list([(0, 0), (5, 0), (5, 5)]), 1.0, 1.0)
        points = list(p.flattening(0))
        assert points[0].isclose((0, 0))
        assert points[1].isclose((4, 0))
        assert points[2].isclose((5, 1))
        assert points[3].isclose((5, 5))
        assert len(points) == 4

    def test_two_chamfers(self):
        p = chamfer2(Vec3.list([(0, 0), (5, 0), (5, 5), (10, 5)]), 0.5, 0.5)
        points = list(p.flattening(0))
        assert points[0].isclose((0, 0))
        assert points[1].isclose((4.5, 0))
        assert points[2].isclose((5, 0.5))
        assert points[3].isclose((5, 4.5))
        assert points[4].isclose((5.5, 5))
        assert points[5].isclose((10, 5))
        assert len(points) == 6


class TestFillet:
    def test_requires_three_points(self):
        with pytest.raises(ValueError):
            fillet([Vec3(), Vec3()], 1.0)


if __name__ == "__main__":
    pytest.main([__file__])
