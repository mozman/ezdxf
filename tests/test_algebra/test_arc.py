# (c) 2018, Manfred Moitzi
# License: MIT License

import ezdxf
from ezdxf.algebra.base import equals_almost, almost_equal_points
from ezdxf.algebra import ConstructionArc, Vector, UCS


def test_arc_from_2p_angle_complex():
    p1 = (-15.73335, 10.98719)
    p2 = (-12.67722, 8.76554)
    angle = 55.247230
    arc = ConstructionArc.from_2p_angle(start_point=p1, end_point=p2, angle=angle)

    arc_result = ConstructionArc(
        center=(-12.08260, 12.79635),
        radius=4.07443,
        start_angle=-153.638906,
        end_angle=-98.391676,
    )

    assert almost_equal_points(arc.center, arc_result.center, places=5)
    assert equals_almost(arc.radius, arc_result.radius, places=5)
    assert equals_almost(arc.start_angle, arc_result.start_angle, places=3)
    assert equals_almost(arc.end_angle, arc_result.end_angle, places=3)


def test_arc_from_2p_angle_simple():
    p1 = (2, 1)
    p2 = (0, 3)
    angle = 90

    arc = ConstructionArc.from_2p_angle(start_point=p1, end_point=p2, angle=angle)
    assert almost_equal_points(arc.center, Vector(0, 1))
    assert equals_almost(arc.radius, 2)
    assert equals_almost(arc.start_angle, 0)
    assert equals_almost(arc.end_angle, 90)

    arc = ConstructionArc.from_2p_angle(start_point=p2, end_point=p1, angle=angle)
    assert almost_equal_points(arc.center, Vector(2, 3))
    assert equals_almost(arc.radius, 2)
    assert equals_almost(arc.start_angle, 180)
    assert equals_almost(arc.end_angle, -90)


def test_arc_from_2p_radius():
    p1 = (2, 1)
    p2 = (0, 3)
    radius = 2

    arc = ConstructionArc.from_2p_radius(start_point=p1, end_point=p2, radius=radius)
    assert almost_equal_points(arc.center, Vector(0, 1))
    assert equals_almost(arc.radius, radius)
    assert equals_almost(arc.start_angle, 0)
    assert equals_almost(arc.end_angle, 90)

    arc = ConstructionArc.from_2p_radius(start_point=p2, end_point=p1, radius=radius)
    assert almost_equal_points(arc.center, Vector(2, 3))
    assert equals_almost(arc.radius, radius)
    assert equals_almost(arc.start_angle, 180)
    assert equals_almost(arc.end_angle, -90)


def test_arc_from_3p():
    p1 = (-15.73335, 10.98719)
    p2 = (-12.67722, 8.76554)
    p3 = (-8.00817, 12.79635)
    arc = ConstructionArc.from_3p(start_point=p1, end_point=p2, def_point=p3)

    arc_result = ConstructionArc(
        center=(-12.08260, 12.79635),
        radius=4.07443,
        start_angle=-153.638906,
        end_angle=-98.391676,
    )

    assert almost_equal_points(arc.center, arc_result.center, places=5)
    assert equals_almost(arc.radius, arc_result.radius, places=5)
    assert equals_almost(arc.start_angle, arc_result.start_angle, places=3)
    assert equals_almost(arc.end_angle, arc_result.end_angle, places=3)


def test_spatial_arc_from_3p():
    start_point_wcs = Vector(0, 1, 0)
    end_point_wcs = Vector(1, 0, 0)
    def_point_wcs = Vector(0, 0, 1)

    ucs = UCS.from_x_axis_and_point_in_xy(origin=def_point_wcs, axis=end_point_wcs-def_point_wcs, point=start_point_wcs)
    start_point_ucs = ucs.from_wcs(start_point_wcs)
    end_point_ucs = ucs.from_wcs(end_point_wcs)
    def_point_ucs = Vector(0, 0)

    arc = ConstructionArc.from_3p(start_point_ucs, end_point_ucs, def_point_ucs)
    dwg = ezdxf.new('R12')
    msp = dwg.modelspace()

    dxf_arc = arc.add_to_layout(msp, ucs)
    assert dxf_arc.dxftype() == 'ARC'
    assert equals_almost(dxf_arc.dxf.radius, 0.81649658)
    assert equals_almost(dxf_arc.dxf.start_angle, -30.)
    assert equals_almost(dxf_arc.dxf.end_angle, -150.)
    assert almost_equal_points(dxf_arc.dxf.extrusion, (0.57735027, 0.57735027, 0.57735027))
