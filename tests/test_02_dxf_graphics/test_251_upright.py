#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
import math
from ezdxf.upright import upright, _flip_deg_angle
from ezdxf import path
from ezdxf.entities import (
    Circle,
    Arc,
    DXFEntity,
    Text,
    Solid,
    Trace,
    Ellipse,
    LWPolyline,
    Hatch,
)
from ezdxf.math import Z_AXIS, Matrix44, OCS, OCSTransform, Vec3


@pytest.mark.parametrize(
    "angle",
    [
        0.0,
        30.0,
        60.0,
        90.0,
        180.0,
        270.0,
        -30.0,
        -60.0,
        -90.0,
        -180.0,
        -270.0,
    ],
)
def test_flip_deg_angle(angle):
    t = OCSTransform.from_ocs(
        OCS(-Z_AXIS),
        OCS(Z_AXIS),
        Matrix44(),
    )
    control_value = t.transform_deg_angle(angle)
    assert _flip_deg_angle(angle) == pytest.approx(control_value)


@pytest.fixture
def circle():
    return Circle.new(
        dxfattribs={"center": (3, 4), "radius": 2.0, "extrusion": (0, 0, -1)}
    )


def test_safety_checks(circle):
    # invalid entities should be ignored silently
    upright(None)  # ignore None values
    upright(DXFEntity())  # ignore invalid DXF entity types
    upright(Text())  # ignore unsupported DXF entity types
    circle.destroy()
    upright(circle)  # ignore destroyed entities
    assert True is True


def test_upright_circle_dxf_attributes(circle):
    upright(circle)
    assert circle.dxf.extrusion.isclose(Z_AXIS)
    assert circle.dxf.center.isclose((-3, 4))
    assert circle.dxf.radius == 2.0


def test_upright_circle_geometry(circle):
    circle.dxf.center = (0, 0)  # required for rotation!
    p0 = path.make_path(circle)
    upright(circle)
    # IMPORTANT: Circle has a different WCS representation as Path object
    # Rotated around the z-axis by 180 degrees AND reversed order, because
    # the start point is always at 0 degrees, determined by the OCS x-axis!
    p1 = path.make_path(circle).transform(Matrix44.z_rotate(math.pi))
    assert path.have_close_control_vertices(p0, p1.reversed())


@pytest.fixture
def arc():
    return Arc.new(
        dxfattribs={
            "center": (3, 4, 5),
            "radius": 2.0,
            "start_angle": 15,
            "end_angle": 75,
            "extrusion": (0, 0, -1),
        }
    )


def test_upright_arc_dxf_attributes(arc):
    upright(arc)
    assert arc.dxf.extrusion.isclose(Z_AXIS)
    assert arc.dxf.center.isclose((-3, 4, -5))
    assert arc.dxf.radius == 2.0
    assert arc.dxf.start_angle == pytest.approx(105.0)
    assert arc.dxf.end_angle == pytest.approx(165.0)


def test_upright_arc_geometry(arc):
    p0 = path.make_path(arc)
    upright(arc)
    # ARC angles are always in counter-clockwise orientation around the
    # extrusion vector, therefore a reversed path vertex order:
    p1 = path.make_path(arc).reversed()
    assert path.have_close_control_vertices(p0, p1)


@pytest.mark.parametrize("cls", [Solid, Trace])
def test_upright_quadrilaterals(cls):
    solid = cls.new(
        dxfattribs={
            "vtx0": (1, 1),
            "vtx1": (2, 1),
            "vtx2": (2, 2),
            "vtx3": (1, 2),
            "extrusion": (0, 0, -1),
        }
    )
    p0 = path.make_path(solid)
    assert len(p0) == 4

    upright(solid)
    assert solid.dxf.extrusion.isclose(Z_AXIS)
    p1 = path.make_path(solid)
    # same vertex order as source entity
    assert path.have_close_control_vertices(p0, p1)


def test_upright_ellipse():
    ellipse = Ellipse.new(
        dxfattribs={
            "center": (5, 5, 5),
            "major_axis": (5, 0, 0),
            "ratio": 0.5,
            "start_param": 0.5,
            "end_param": 1.5,
            "extrusion": (0, 0, -1),
        }
    )
    p0 = path.make_path(ellipse)
    assert p0.has_curves is True

    upright(ellipse)
    assert ellipse.dxf.extrusion.isclose(Z_AXIS)
    p1 = path.make_path(ellipse)
    # has reversed vertex order of source entity:
    assert path.have_close_control_vertices(p0, p1.reversed())


POLYLINE_POINTS = [
    # x, y, s, e, b
    (0, 0, 0, 0, 0),
    (2, 2, 1, 2, -1),
    (4, 0, 2, 1, 1),
    (6, 0, 0, 0, 0),
]


def lwpolyline():
    pline = LWPolyline.new(
        dxfattribs={
            "elevation": 4,
            "extrusion": (0, 0, -1),
        }
    )
    pline.set_points(POLYLINE_POINTS)
    return pline


def polyline2d():
    from ezdxf.layouts import VirtualLayout

    layout = VirtualLayout()
    return layout.add_polyline2d(
        POLYLINE_POINTS,
        format="xyseb",
        dxfattribs={
            "elevation": (0, 0, 4),
            "extrusion": (0, 0, -1),
        },
    )


@pytest.mark.parametrize("factory", [lwpolyline, polyline2d])
def test_upright_polyline(factory):
    polyline = factory()
    p0 = path.make_path(polyline)
    assert p0.has_curves is True

    upright(polyline)
    assert polyline.dxf.extrusion.isclose(Z_AXIS)
    p1 = path.make_path(polyline)
    # vertex order do not change:
    assert path.have_close_control_vertices(p0, p1)


def test_upright_hatch_with_polyline_path():
    hatch = Hatch.new(
        dxfattribs={
            "elevation": (0, 0, 4),
            "extrusion": (0, 0, -1),
        }
    )
    hatch.paths.add_polyline_path(
        [(x, y, b) for x, y, s, e, b in POLYLINE_POINTS]
    )
    p0 = path.make_path(hatch)
    assert p0.has_curves is True

    upright(hatch)
    assert hatch.dxf.extrusion.isclose(Z_AXIS)
    p1 = path.make_path(hatch)
    assert path.have_close_control_vertices(p0, p1)


def test_upright_hatch_with_edge_path(all_edge_types_hatch):
    hatch = all_edge_types_hatch
    hatch.dxf.elevation = Vec3(0, 0, 4)
    hatch.dxf.extrusion = Vec3(0, 0, -1)
    assert hatch.dxf.extrusion.isclose(-Z_AXIS)

    p0 = path.make_path(hatch)
    assert p0.has_curves is True

    upright(hatch)
    assert hatch.dxf.extrusion.isclose(Z_AXIS)
    p1 = path.make_path(hatch)
    assert path.have_close_control_vertices(p0, p1)


if __name__ == "__main__":
    pytest.main([__file__])
