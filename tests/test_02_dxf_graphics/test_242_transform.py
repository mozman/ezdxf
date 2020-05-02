# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
import math
from ezdxf.entities import Line, Point, Circle
from ezdxf.math import Matrix44, OCS, Vector
from ezdxf.math.transformtools import NonUniformScalingError


# Assuming Transformation by Matrix44() class is correct.
# Test for Matrix44() class are located in test_605_matrix44.py


def test_transform_interface_by_line_entity():
    line = Line.new(dxfattribs={'start': (0, 0, 0), 'end': (1, 0, 0), 'extrusion': (0, 1, 0)})
    m = Matrix44.translate(1, 2, 3)
    line.transform(m)

    # simple 3D entity - no OCS transformation,
    assert line.dxf.start == (1, 2, 3)
    assert line.dxf.end == (2, 2, 3)
    # extrusion direction without translation - not an OCS extrusion vector!
    assert line.dxf.extrusion == (0, 1, 0)

    # Create new entity by transformation:
    new_line = line.copy()
    new_line.transform(m)

    assert new_line.dxf.start == (2, 4, 6)
    assert new_line.dxf.end == (3, 4, 6)
    assert new_line.dxf.extrusion == (0, 1, 0)


def test_line_rotation():
    line = Line.new(dxfattribs={'start': (0, 0, 0), 'end': (1, 0, 0), 'extrusion': (0, 1, 0)})
    angle = math.pi / 4
    m = Matrix44.z_rotate(angle)
    line.transform(m)
    assert line.dxf.start == (0, 0, 0)
    assert line.dxf.end.isclose((math.cos(angle), math.sin(angle), 0), abs_tol=1e-9)
    assert line.dxf.extrusion.isclose((-math.cos(angle), math.sin(angle), 0), abs_tol=1e-9)
    assert line.dxf.thickness == 0


def test_line_scaling():
    line = Line.new(dxfattribs={'start': (0, 0, 0), 'end': (1, 0, 0), 'extrusion': (0, 1, 0), 'thickness': 2})
    m = Matrix44.scale(2, 2, 0)
    line.transform(m)
    assert line.dxf.start == (0, 0, 0)
    assert line.dxf.end == (2, 0, 0)
    assert line.dxf.extrusion == (0, 1, 0)
    assert line.dxf.thickness == 4


def test_point():
    point = Point.new(dxfattribs={'location': (2, 3, 4), 'extrusion': (0, 1, 0), 'thickness': 2})
    # 1. rotation - 2. scaling - 3. translation
    m = Matrix44.chain(Matrix44.scale(2, 3, 1), Matrix44.translate(1, 1, 1))
    point.transform(m)
    assert point.dxf.location == (5, 10, 5)
    assert point.dxf.extrusion == (0, 1, 0)
    assert point.dxf.thickness == 6

    angle = math.pi / 4
    point.transform(Matrix44.z_rotate(math.pi / 4))
    assert point.dxf.extrusion.isclose((-math.cos(angle), math.sin(angle), 0))
    assert math.isclose(point.dxf.thickness, 6)


def test_circle_default_ocs():
    circle = Circle.new(dxfattribs={'center': (2, 3, 4), 'thickness': 2})
    # 1. rotation - 2. scaling - 3. translation
    m = Matrix44.chain(Matrix44.scale(2, 2, 3), Matrix44.translate(1, 1, 1))
    # default extrusion is (0, 0, 1), therefore scale(2, 2, ..) is a uniform scaling in the xy-play of the OCS
    circle.transform(m)

    assert circle.dxf.center == (5, 7, 13)
    assert circle.dxf.extrusion == (0, 0, 1)
    assert circle.dxf.thickness == 6


def test_circle_non_uniform_scaling():
    circle = Circle.new(dxfattribs={'center': (2, 3, 4), 'extrusion': (0, 1, 0), 'thickness': 2})
    # extrusion in WCS y-axis, therefore scale(2, ..., 3) is a non uniform scaling in the xy-play of the OCS
    # which is the xz-plane of the WCS
    with pytest.raises(NonUniformScalingError):
        circle.transform(Matrix44.scale(2, 2, 3))

    # source values unchanged after exception
    assert circle.dxf.center == (2, 3, 4)
    assert circle.dxf.extrusion == (0, 1, 0)
    assert circle.dxf.thickness == 2


def test_circle_user_ocs():
    center = (2, 3, 4)
    extrusion = (0, 1, 0)

    circle = Circle.new(dxfattribs={'center': center, 'extrusion': extrusion, 'thickness': 2})
    ocs = OCS(extrusion)
    v = ocs.to_wcs(center)  # (-2, 4, 3)
    v = Vector(v.x*2, v.y*4, v.z*2)
    v += (1, 1, 1)
    # and back to OCS, extrusion is unchanged
    result = ocs.from_wcs(v)

    m = Matrix44.chain(Matrix44.scale(2, 4, 2), Matrix44.translate(1, 1, 1))
    circle.transform(m)
    assert circle.dxf.center == result
    assert circle.dxf.extrusion == (0, 1, 0)
    assert circle.dxf.thickness == 8  # in WCS y-axis


if __name__ == '__main__':
    pytest.main([__file__])
