#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
import math
from ezdxf.math import X_AXIS, Y_AXIS, Z_AXIS, Vec3, close_vectors
from ezdxf.math.construct3d import inscribe_circle_tangent_length, bending_angle
from ezdxf.path.tools import chamfer, chamfer2, fillet, polygonal_fillet


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

    @pytest.mark.parametrize(
        "points",
        [
            Vec3.list([(0, 0), (5, 0), (10, 0)]),
            Vec3.list([(0, 0), (5, 0), (0, 0)]),
        ],
        ids=["180deg", "360deg"],
    )
    def test_colinear_points_are_ignored(self, points):
        p = chamfer(points, 1.0)
        assert points == list(p.flattening(0))

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

    @pytest.mark.parametrize(
        "points",
        [
            Vec3.list([(0, 0), (5, 0), (10, 0)]),
            Vec3.list([(0, 0), (5, 0), (0, 0)]),
        ],
        ids=["180deg", "360deg"],
    )
    def test_colinear_points_are_ignored(self, points):
        p = chamfer2(points, 1.0, 1.0)
        assert points == list(p.flattening(0))

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

    @pytest.mark.parametrize(
        "points",
        [
            Vec3.list([(0, 0), (5, 0), (10, 0)]),
            Vec3.list([(0, 0), (5, 0), (0, 0)]),
        ],
        ids=["180deg", "360deg"],
    )
    def test_colinear_points_are_ignored(self, points):
        p = fillet(points, 1.0)
        assert points == list(p.flattening(0.1))

    def test_points_for_45_deg(self):
        p = fillet(Vec3.list([(-5, 0), (0, 0), (-5, -5)]), 1.0)
        # result is visually checked in CAD application
        assert (
            close_vectors(
                p.flattening(1, segments=16),
                [
                    Vec3(-5.0, 0.0, 0.0),
                    Vec3(-2.414213562373095, 0.0, 0.0),
                    Vec3(-2.338885112974325, -0.0028274449650404843, 0.0),
                    Vec3(-2.2647391508495334, -0.011198832627437505, 0.0),
                    Vec3(-2.192024742400491, -0.02494774213810442, 0.0),
                    Vec3(-2.1209909540289686, -0.04390775264795457, 0.0),
                    Vec3(-2.0518868521367364, -0.06791244330790133, 0.0),
                    Vec3(-1.9849615031255663, -0.09679539326885803, 0.0),
                    Vec3(-1.920463973397228, -0.13039018168173805, 0.0),
                    Vec3(-1.8586433293534927, -0.1685303876974547, 0.0),
                    Vec3(-1.7997486373961311, -0.2110495904669214, 0.0),
                    Vec3(-1.744028963926914, -0.25778136914105143, 0.0),
                    Vec3(-1.6917333753476123, -0.3085593028707582, 0.0),
                    Vec3(-1.6431109380599964, -0.36321697080695503, 0.0),
                    Vec3(-1.5984107184658374, -0.42158795210055533, 0.0),
                    Vec3(-1.5578817829669058, -0.4835058259024724, 0.0),
                    Vec3(-1.5217731979649725, -0.5488041713636196, 0.0),
                    Vec3(-1.4903340298618082, -0.6173165676349102, 0.0),
                    Vec3(-1.46411929882365, -0.687992996594291, 0.0),
                    Vec3(-1.4434790212617288, -0.7596985247840479, 0.0),
                    Vec3(-1.428354757945307, -0.832139358351603, 0.0),
                    Vec3(-1.418688069643647, -0.9050217034443786, 0.0),
                    Vec3(-1.4144205171260105, -0.9780517662097967, 0.0),
                    Vec3(-1.4154936611616598, -1.0509357527952796, 0.0),
                    Vec3(-1.421849062519857, -1.1233798693482493, 0.0),
                    Vec3(-1.4334282819698645, -1.1950903220161282, 0.0),
                    Vec3(-1.4501728802809442, -1.2657733169463383, 0.0),
                    Vec3(-1.4720244182223583, -1.3351350602863021, 0.0),
                    Vec3(-1.498924456563369, -1.4028817581834412, 0.0),
                    Vec3(-1.5308145560732387, -1.4687196167851782, 0.0),
                    Vec3(-1.5676362775212291, -1.5323548422389353, 0.0),
                    Vec3(-1.6093311816766027, -1.593493640692134, 0.0),
                    Vec3(-1.6558408293086213, -1.6518422182921977, 0.0),
                    Vec3(-1.7071067811865475, -1.7071067811865475, 0.0),
                    Vec3(-5.0, -5.0, 0.0),
                ],
            )
            is True
        )

    def test_points_for_135_deg(self):
        p = fillet(Vec3.list([(-5, 0), (0, 0), (-5, 5)]), 1.0)
        # result is visually checked in CAD application
        assert (
            close_vectors(
                p.flattening(1, segments=16),
                [
                    Vec3(-5.0, 0.0, 0.0),
                    Vec3(-2.414213562373095, 0.0, 0.0),
                    Vec3(-2.338885112974325, 0.0028274449650404843, 0.0),
                    Vec3(-2.2647391508495334, 0.011198832627437505, 0.0),
                    Vec3(-2.192024742400491, 0.02494774213810442, 0.0),
                    Vec3(-2.1209909540289686, 0.04390775264795457, 0.0),
                    Vec3(-2.0518868521367364, 0.06791244330790133, 0.0),
                    Vec3(-1.9849615031255663, 0.09679539326885803, 0.0),
                    Vec3(-1.920463973397228, 0.13039018168173805, 0.0),
                    Vec3(-1.8586433293534927, 0.1685303876974547, 0.0),
                    Vec3(-1.7997486373961311, 0.2110495904669214, 0.0),
                    Vec3(-1.744028963926914, 0.25778136914105143, 0.0),
                    Vec3(-1.6917333753476123, 0.3085593028707582, 0.0),
                    Vec3(-1.6431109380599964, 0.36321697080695503, 0.0),
                    Vec3(-1.5984107184658374, 0.42158795210055533, 0.0),
                    Vec3(-1.5578817829669058, 0.4835058259024724, 0.0),
                    Vec3(-1.5217731979649725, 0.5488041713636196, 0.0),
                    Vec3(-1.4903340298618082, 0.6173165676349102, 0.0),
                    Vec3(-1.46411929882365, 0.687992996594291, 0.0),
                    Vec3(-1.4434790212617288, 0.7596985247840479, 0.0),
                    Vec3(-1.428354757945307, 0.832139358351603, 0.0),
                    Vec3(-1.418688069643647, 0.9050217034443786, 0.0),
                    Vec3(-1.4144205171260105, 0.9780517662097967, 0.0),
                    Vec3(-1.4154936611616598, 1.0509357527952796, 0.0),
                    Vec3(-1.421849062519857, 1.1233798693482493, 0.0),
                    Vec3(-1.4334282819698645, 1.1950903220161282, 0.0),
                    Vec3(-1.4501728802809442, 1.2657733169463383, 0.0),
                    Vec3(-1.4720244182223583, 1.3351350602863021, 0.0),
                    Vec3(-1.498924456563369, 1.4028817581834412, 0.0),
                    Vec3(-1.5308145560732387, 1.4687196167851782, 0.0),
                    Vec3(-1.5676362775212291, 1.5323548422389353, 0.0),
                    Vec3(-1.6093311816766027, 1.593493640692134, 0.0),
                    Vec3(-1.6558408293086213, 1.6518422182921977, 0.0),
                    Vec3(-1.7071067811865475, 1.7071067811865475, 0.0),
                    Vec3(-5.0, 5.0, 0.0),
                ],
            )
            is True
        )


class TestPolygonalFillet:
    def test_requires_three_points(self):
        with pytest.raises(ValueError):
            polygonal_fillet([Vec3(), Vec3()], 1.0)

    @pytest.mark.parametrize(
        "points",
        [
            Vec3.list([(0, 0), (5, 0), (10, 0)]),
            Vec3.list([(0, 0), (5, 0), (0, 0)]),
        ],
        ids=["180deg", "360deg"],
    )
    def test_colinear_points_are_ignored(self, points):
        p = polygonal_fillet(points, 1.0)
        assert points == list(p.flattening(0))

    @pytest.mark.parametrize(
        "count, expected", [
            (0, 3), (1, 3), (4, 3),
            (16, 4 + 2), (32, 8 + 2)
        ]
    )
    def test_for_required_segment_count(self, count, expected):
        p = polygonal_fillet(Vec3.list([(0, 0), (5, 0), (5, 5)]), 1, count)
        # min line segment count is 3
        assert len(p) == expected


if __name__ == "__main__":
    pytest.main([__file__])
