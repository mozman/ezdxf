# (c) 2018, Manfred Moitzi
# License: MIT License

from ezdxf.algebra.base import equals_almost, almost_equal_points
from ezdxf.algebra.arc import Arc


def test_arc_from_2p_angle():
    p1 = (-15.73335, 10.98719)
    p2 = (-12.67722, 8.76554)
    angle = 55.247230
    arc = Arc.from_2p_angle(start_point=p1, end_point=p2, angle=angle)

    arc_result = Arc(
        center=(-12.08260, 12.79635),
        radius=4.07443,
        start_angle=-153.638906,
        end_angle=-98.391676,
    )

    assert almost_equal_points(arc.center, arc_result.center, places=5)
    assert equals_almost(arc.radius, arc_result.radius, places=5)
    assert equals_almost(arc.start_angle, arc_result.start_angle, places=3)
    assert equals_almost(arc.end_angle, arc_result.end_angle, places=3)


def test_arc_from_3p():
    p1 = (-15.73335, 10.98719)
    p2 = (-12.67722, 8.76554)
    p3 = (-8.00817, 12.79635)
    arc = Arc.from_3p(start_point=p1, end_point=p2, def_point=p3)

    arc_result = Arc(
        center=(-12.08260, 12.79635),
        radius=4.07443,
        start_angle=-153.638906,
        end_angle=-98.391676,
    )

    assert almost_equal_points(arc.center, arc_result.center, places=5)
    assert equals_almost(arc.radius, arc_result.radius, places=5)
    assert equals_almost(arc.start_angle, arc_result.start_angle, places=3)
    assert equals_almost(arc.end_angle, arc_result.end_angle, places=3)

