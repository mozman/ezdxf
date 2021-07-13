#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
import math
from ezdxf.upright import upright, _flip_deg_angle
from ezdxf import path
from ezdxf.entities import Circle, Arc, DXFEntity, Text
from ezdxf.math import Z_AXIS, Matrix44, OCS, OCSTransform


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


def test_upright_circle_params(circle):
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
            "center": (3, 4),
            "radius": 2.0,
            "start_angle": 15,
            "end_angle": 75,
            "extrusion": (0, 0, -1),
        }
    )


def test_upright_arc(arc):
    upright(arc)
    assert arc.dxf.extrusion.isclose(Z_AXIS)
    assert arc.dxf.center.isclose((-3, 4))
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


if __name__ == "__main__":
    pytest.main([__file__])
