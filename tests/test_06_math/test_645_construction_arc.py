# (c) 2018, Manfred Moitzi
# License: MIT License

import ezdxf
import math
from ezdxf.math import ConstructionArc, Vector, UCS, Vec2
from math import isclose


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

    assert arc.center.isclose(arc_result.center, abs_tol=1e-5)
    assert isclose(arc.radius, arc_result.radius, abs_tol=1e-5)
    assert isclose(arc.start_angle, arc_result.start_angle, abs_tol=1e-4)
    assert isclose(arc.end_angle, arc_result.end_angle, abs_tol=1e-4)


def test_arc_from_2p_angle_simple():
    p1 = (2, 1)
    p2 = (0, 3)
    angle = 90

    arc = ConstructionArc.from_2p_angle(start_point=p1, end_point=p2, angle=angle)
    assert arc.center == (0, 1)
    assert isclose(arc.radius, 2)
    assert isclose(arc.start_angle, 0, abs_tol=1e-12)
    assert isclose(arc.end_angle, 90)

    arc = ConstructionArc.from_2p_angle(start_point=p2, end_point=p1, angle=angle)
    assert arc.center == (2, 3)
    assert isclose(arc.radius, 2)
    assert isclose(arc.start_angle, 180)
    assert isclose(arc.end_angle, -90)


def test_arc_from_2p_radius():
    p1 = (2, 1)
    p2 = (0, 3)
    radius = 2

    arc = ConstructionArc.from_2p_radius(start_point=p1, end_point=p2, radius=radius)
    assert arc.center == (0, 1)
    assert isclose(arc.radius, radius)
    assert isclose(arc.start_angle, 0)
    assert isclose(arc.end_angle, 90)

    arc = ConstructionArc.from_2p_radius(start_point=p2, end_point=p1, radius=radius)
    assert arc.center == Vector(2, 3)
    assert isclose(arc.radius, radius)
    assert isclose(arc.start_angle, 180)
    assert isclose(arc.end_angle, -90)


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

    assert arc.center.isclose(arc_result.center, abs_tol=1e-5)
    assert isclose(arc.radius, arc_result.radius, abs_tol=1e-5)
    assert isclose(arc.start_angle, arc_result.start_angle, abs_tol=1e-4)
    assert isclose(arc.end_angle, arc_result.end_angle, abs_tol=1e-4)


def test_spatial_arc_from_3p():
    start_point_wcs = Vector(0, 1, 0)
    end_point_wcs = Vector(1, 0, 0)
    def_point_wcs = Vector(0, 0, 1)

    ucs = UCS.from_x_axis_and_point_in_xy(origin=def_point_wcs, axis=end_point_wcs - def_point_wcs,
                                          point=start_point_wcs)
    start_point_ucs = ucs.from_wcs(start_point_wcs)
    end_point_ucs = ucs.from_wcs(end_point_wcs)
    def_point_ucs = Vector(0, 0)

    arc = ConstructionArc.from_3p(start_point_ucs, end_point_ucs, def_point_ucs)
    dwg = ezdxf.new('R12')
    msp = dwg.modelspace()

    dxf_arc = arc.add_to_layout(msp, ucs)
    assert dxf_arc.dxftype() == 'ARC'
    assert isclose(dxf_arc.dxf.radius, 0.81649658, abs_tol=1e-9)
    assert isclose(dxf_arc.dxf.start_angle, 330)
    assert isclose(dxf_arc.dxf.end_angle, 210)
    assert dxf_arc.dxf.extrusion.isclose((0.57735027, 0.57735027, 0.57735027), abs_tol=1e-9)


def test_bounding_box():
    bbox = ConstructionArc(center=(0, 0), radius=1, start_angle=0, end_angle=90).bounding_box
    assert bbox.extmin == (0, 0)
    assert bbox.extmax == (1, 1)

    bbox = ConstructionArc(center=(0, 0), radius=1, start_angle=0, end_angle=180).bounding_box
    assert bbox.extmin == (-1, 0)
    assert bbox.extmax == (1, 1)

    bbox = ConstructionArc(center=(0, 0), radius=1, start_angle=270, end_angle=90).bounding_box
    assert bbox.extmin == (0, -1)
    assert bbox.extmax == (1, 1)


def test_angles():
    arc = ConstructionArc(radius=1, start_angle=30, end_angle=60)
    assert tuple(arc.angles(2)) == (30, 60)
    assert tuple(arc.angles(3)) == (30, 45, 60)

    arc.start_angle = 180
    arc.end_angle = 0
    assert tuple(arc.angles(2)) == (180, 0)
    assert tuple(arc.angles(3)) == (180, 270, 0)

    arc.start_angle = -90
    arc.end_angle = -180
    assert tuple(arc.angles(2)) == (270, 180)
    assert tuple(arc.angles(4)) == (270, 0, 90, 180)


def test_vertices():
    angles = [0, 45, 90, 135, -45, -90, -135, 180]
    arc = ConstructionArc(center=(1, 1))
    vertices = list(arc.vertices(angles))
    for v, a in zip(vertices, angles):
        a = math.radians(a)
        assert v.isclose(Vec2((1 + math.cos(a), 1 + math.sin(a))))


def test_tangents():
    angles = [0, 45, 90, 135, -45, -90, -135, 180]
    sin45 = math.sin(math.pi / 4)
    result = [(0, 1), (-sin45, sin45), (-1, 0), (-sin45, -sin45), (sin45, sin45), (1, 0), (sin45, -sin45), (0, -1)]
    arc = ConstructionArc(center=(1, 1))
    vertices = list(arc.tangents(angles))
    for v, r in zip(vertices, result):
        assert v.isclose(Vec2(r))


def test_angle_span():
    assert ConstructionArc(start_angle=30, end_angle=270).angle_span == 240
    # crossing 0-degree:
    assert ConstructionArc(start_angle=30, end_angle=270, is_counter_clockwise=False).angle_span == 120
    # crossing 0-degree:
    assert ConstructionArc(start_angle=300, end_angle=60).angle_span == 120
    assert ConstructionArc(start_angle=300, end_angle=60, is_counter_clockwise=False).angle_span == 240
