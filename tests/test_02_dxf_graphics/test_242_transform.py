# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import Union
import pytest
import math
from ezdxf.entities import (
    DXFGraphic, Line, Point, Circle, Arc, Ellipse, XLine, Mesh, Spline, Solid, Face3d, LWPolyline, Polyline, Text,
    MText, Insert, Dimension,
)
from ezdxf.math import Matrix44, OCS, Vector
from ezdxf.math.transformtools import NonUniformScalingError


# Assuming Transformation by Matrix44() class is correct.
# Test for Matrix44() class are located in test_605_matrix44.py


def test_transform_interface():
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


def test_basic_transformation_interfaces():
    # test basic implementation = forward operation to transform interface
    class BasicGraphic(DXFGraphic):
        def transform(self, m: 'Matrix44') -> 'DXFGraphic':
            return self

    interface_mockup = BasicGraphic.new()
    assert interface_mockup.translate(1, 2, 3) is interface_mockup
    assert interface_mockup.scale(1, 2, 3) is interface_mockup
    assert interface_mockup.scale_uniform(1) is interface_mockup
    assert interface_mockup.rotate_axis((1, 2, 3), 1) is interface_mockup
    assert interface_mockup.rotate_x(1) is interface_mockup
    assert interface_mockup.rotate_y(1) is interface_mockup
    assert interface_mockup.rotate_z(1) is interface_mockup


def test_line_fast_translation():
    line = Line.new(dxfattribs={'start': (0, 0, 0), 'end': (1, 0, 0), 'extrusion': (0, 1, 0)})
    line.translate(1, 2, 3)
    assert line.dxf.start == (1, 2, 3)
    assert line.dxf.end == (2, 2, 3)


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


def test_point_fast_translation():
    point = Point.new(dxfattribs={'location': (2, 3, 4), 'extrusion': (0, 1, 0), 'thickness': 2})
    point.translate(1, 2, 3)
    assert point.dxf.location == (3, 5, 7)


def test_circle_default_ocs():
    circle = Circle.new(dxfattribs={'center': (2, 3, 4), 'thickness': 2})
    # 1. rotation - 2. scaling - 3. translation
    m = Matrix44.chain(Matrix44.scale(2, 2, 3), Matrix44.translate(1, 1, 1))
    # default extrusion is (0, 0, 1), therefore scale(2, 2, ..) is a uniform scaling in the xy-play of the OCS
    circle.transform(m)

    assert circle.dxf.center == (5, 7, 13)
    assert circle.dxf.extrusion == (0, 0, 1)
    assert circle.dxf.thickness == 6


def test_circle_fast_translation():
    circle = Circle.new(dxfattribs={'center': (2, 3, 4), 'thickness': 2})
    circle.translate(1, 2, 3)
    assert circle.dxf.center == (3, 5, 7)


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
    v = Vector(v.x * 2, v.y * 4, v.z * 2)
    v += (1, 1, 1)
    # and back to OCS, extrusion is unchanged
    result = ocs.from_wcs(v)

    m = Matrix44.chain(Matrix44.scale(2, 4, 2), Matrix44.translate(1, 1, 1))
    circle.transform(m)
    assert circle.dxf.center == result
    assert circle.dxf.extrusion == (0, 1, 0)
    assert circle.dxf.thickness == 8  # in WCS y-axis


def test_arc_default_ocs():
    arc = Arc.new(dxfattribs={'center': (2, 3, 4), 'thickness': 2, 'start_angle': 30, 'end_angle': 60})
    # 1. rotation - 2. scaling - 3. translation
    m = Matrix44.chain(Matrix44.scale(2, 2, 3), Matrix44.translate(1, 1, 1))
    # default extrusion is (0, 0, 1), therefore scale(2, 2, ..) is a uniform scaling in the xy-play of the OCS
    arc.transform(m)

    assert arc.dxf.center == (5, 7, 13)
    assert arc.dxf.extrusion == (0, 0, 1)
    assert arc.dxf.thickness == 6
    assert math.isclose(arc.dxf.start_angle, 30, abs_tol=1e-9)
    assert math.isclose(arc.dxf.end_angle, 60, abs_tol=1e-9)

    arc.transform(Matrix44.z_rotate(math.radians(30)))
    assert math.isclose(arc.dxf.start_angle, 60, abs_tol=1e-9)
    assert math.isclose(arc.dxf.end_angle, 90, abs_tol=1e-9)


def _get_transformed_curve(scale_factors: Vector, rotation: float, is_arc: bool) -> Union[Ellipse, Arc]:
    if is_arc:
        entity = Arc.new(dxfattribs={'center': (0, 0), 'radius': 1, 'start_angle': 0, 'end_angle': 90})
    else:
        entity = Ellipse.new(
            dxfattribs={'center': (0, 0), 'major_axis': (1, 0), 'ratio': 1, 'start_param': 0, 'end_param': math.pi / 2})

    assert entity.start_point.isclose(Vector(1, 0, 0))
    assert entity.end_point.isclose(Vector(0, 1, 0))

    m = Matrix44.chain(
        Matrix44.scale(scale_factors.x, scale_factors.y, scale_factors.z),
        Matrix44.z_rotate(rotation),
    )
    has_uniform_scaling = True
    try:
        entity.transform(m)
    except NonUniformScalingError:
        entity = Ellipse.from_arc(entity)
        entity.transform(m)
        has_uniform_scaling = False

    if is_arc and has_uniform_scaling:
        assert entity.dxftype() == 'ARC'
    else:
        assert entity.dxftype() == 'ELLIPSE'

    start_point = m.transform((1, 0, 0))
    end_point = m.transform((0, 1, 0))

    # reference points should have the same transformation as the ellipse
    assert start_point.isclose(entity.start_point)
    assert end_point.isclose(entity.end_point)
    return entity


def _check_curve(ellipse: Ellipse, expected_start: Vector, expected_end: Vector, expected_extrusion: Vector):
    assert ellipse.start_point.isclose(expected_start)
    assert ellipse.end_point.isclose(expected_end)
    # todo: given extrusions do not match the reconstructed extrusion vectors: x-axis cross y-axis
    # assert ellipse.dxf.extrusion.isclose(expected_extrusion.normalize())


@pytest.mark.parametrize('zscale,is_arc', [
    (1, False), (0.5, False),
    # (1, True), (0.5, True),  # todo: does not work for ARC
    (-1, False),
    # (-1, True),  # todo: does not work for ARC
])
def test_07_rotated_and_reflected_curves(zscale, is_arc):
    scale = Vector(1, 1, zscale)

    ellipse = _get_transformed_curve(scale, 0.0, is_arc)
    _check_curve(ellipse, Vector(1, 0, 0), Vector(0, 1, 0), Vector(0, 0, zscale))

    ellipse = _get_transformed_curve(scale, math.pi / 2, is_arc)
    _check_curve(ellipse, Vector(0, 1, 0), Vector(-1, 0, 0), Vector(0, 0, zscale))

    ellipse = _get_transformed_curve(scale, math.pi, is_arc)
    _check_curve(ellipse, Vector(-1, 0, 0), Vector(0, -1, 0), Vector(0, 0, zscale))

    ellipse = _get_transformed_curve(scale, 3 * math.pi / 2, is_arc)
    _check_curve(ellipse, Vector(0, -1, 0), Vector(1, 0, 0), Vector(0, 0, zscale))

    scale = Vector(1, -1, zscale)

    ellipse = _get_transformed_curve(scale, 0.0, is_arc)
    _check_curve(ellipse, Vector(1, 0, 0), Vector(0, -1, 0), Vector(0, 0, zscale))

    ellipse = _get_transformed_curve(scale, math.pi / 2, is_arc)
    _check_curve(ellipse, Vector(0, 1, 0), Vector(1, 0, 0), Vector(0, 0, zscale))

    ellipse = _get_transformed_curve(scale, math.pi, is_arc)
    _check_curve(ellipse, Vector(-1, 0, 0), Vector(0, 1, 0), Vector(0, 0, zscale))

    ellipse = _get_transformed_curve(scale, 3 * math.pi / 2, is_arc)
    _check_curve(ellipse, Vector(0, -1, 0), Vector(-1, 0, 0), Vector(0, 0, zscale))

    scale = Vector(-1, 1, zscale)

    ellipse = _get_transformed_curve(scale, 0.0, is_arc)
    _check_curve(ellipse, Vector(-1, 0, 0), Vector(0, 1, 0), Vector(0, 0, zscale))

    ellipse = _get_transformed_curve(scale, math.pi / 2, is_arc)
    _check_curve(ellipse, Vector(0, -1, 0), Vector(-1, 0, 0), Vector(0, 0, zscale))

    ellipse = _get_transformed_curve(scale, math.pi, is_arc)
    _check_curve(ellipse, Vector(1, 0, 0), Vector(0, -1, 0), Vector(0, 0, zscale))

    ellipse = _get_transformed_curve(scale, 3 * math.pi / 2, is_arc)
    _check_curve(ellipse, Vector(0, 1, 0), Vector(1, 0, 0), Vector(0, 0, zscale))

    scale = Vector(-1, -1, zscale)

    ellipse = _get_transformed_curve(scale, 0.0, is_arc)
    _check_curve(ellipse, Vector(-1, 0, 0), Vector(0, -1, 0), Vector(0, 0, zscale))

    ellipse = _get_transformed_curve(scale, math.pi / 2, is_arc)
    _check_curve(ellipse, Vector(0, -1, 0), Vector(1, 0, 0), Vector(0, 0, zscale))

    ellipse = _get_transformed_curve(scale, math.pi, is_arc)
    _check_curve(ellipse, Vector(1, 0, 0), Vector(0, 1, 0), Vector(0, 0, zscale))

    ellipse = _get_transformed_curve(scale, 3 * math.pi / 2, is_arc)
    _check_curve(ellipse, Vector(0, 1, 0), Vector(-1, 0, 0), Vector(0, 0, zscale))


@pytest.mark.parametrize('stretch,is_arc', [(0.5, False), (0.5, True)])
def test_08_rotated_and_reflected_and_stretched_curves(stretch, is_arc):
    scale = Vector(1, stretch, 1)

    ellipse = _get_transformed_curve(scale, 0.0, is_arc)
    _check_curve(ellipse, Vector(1, 0, 0), Vector(0, stretch, 0), Vector(0, 0, 1))

    ellipse = _get_transformed_curve(scale, math.pi / 2, is_arc)
    _check_curve(ellipse, Vector(0, 1, 0), Vector(-stretch, 0, 0), Vector(0, 0, 1))

    ellipse = _get_transformed_curve(scale, math.pi, is_arc)
    _check_curve(ellipse, Vector(-1, 0, 0), Vector(0, -stretch, 0), Vector(0, 0, 1))

    ellipse = _get_transformed_curve(scale, 3 * math.pi / 2, is_arc)
    _check_curve(ellipse, Vector(0, -1, 0), Vector(stretch, 0, 0), Vector(0, 0, 1))

    scale = Vector(1, -stretch, 1)

    ellipse = _get_transformed_curve(scale, 0.0, is_arc)
    _check_curve(ellipse, Vector(1, 0, 0), Vector(0, -stretch, 0), Vector(0, 0, 1))

    ellipse = _get_transformed_curve(scale, math.pi / 2, is_arc)
    _check_curve(ellipse, Vector(0, 1, 0), Vector(stretch, 0, 0), Vector(0, 0, 1))

    ellipse = _get_transformed_curve(scale, math.pi, is_arc)
    _check_curve(ellipse, Vector(-1, 0, 0), Vector(0, stretch, 0), Vector(0, 0, 1))

    ellipse = _get_transformed_curve(scale, 3 * math.pi / 2, is_arc)
    _check_curve(ellipse, Vector(0, -1, 0), Vector(-stretch, 0, 0), Vector(0, 0, 1))

    scale = Vector(-1, stretch, 1)

    ellipse = _get_transformed_curve(scale, 0.0, is_arc)
    _check_curve(ellipse, Vector(-1, 0, 0), Vector(0, stretch, 0), Vector(0, 0, 1))

    ellipse = _get_transformed_curve(scale, math.pi / 2, is_arc)
    _check_curve(ellipse, Vector(0, -1, 0), Vector(-stretch, 0, 0), Vector(0, 0, 1))

    ellipse = _get_transformed_curve(scale, math.pi, is_arc)
    _check_curve(ellipse, Vector(1, 0, 0), Vector(0, -stretch, 0), Vector(0, 0, 1))

    ellipse = _get_transformed_curve(scale, 3 * math.pi / 2, is_arc)
    _check_curve(ellipse, Vector(0, 1, 0), Vector(stretch, 0, 0), Vector(0, 0, 1))

    scale = Vector(-1, -stretch, 1)

    ellipse = _get_transformed_curve(scale, 0.0, is_arc)
    _check_curve(ellipse, Vector(-1, 0, 0), Vector(0, -stretch, 0), Vector(0, 0, 1))

    ellipse = _get_transformed_curve(scale, math.pi / 2, is_arc)
    _check_curve(ellipse, Vector(0, -1, 0), Vector(stretch, 0, 0), Vector(0, 0, 1))

    ellipse = _get_transformed_curve(scale, math.pi, is_arc)
    _check_curve(ellipse, Vector(1, 0, 0), Vector(0, stretch, 0), Vector(0, 0, 1))

    ellipse = _get_transformed_curve(scale, 3 * math.pi / 2, is_arc)
    _check_curve(ellipse, Vector(0, 1, 0), Vector(-stretch, 0, 0), Vector(0, 0, 1))


def test_xline():
    # same implementation for Ray()
    xline = XLine.new(dxfattribs={'start': (2, 3, 4), 'unit_vector': (1, 0, 0)})
    # 1. scaling - 2. rotation - 3. translation
    m = Matrix44.chain(Matrix44.scale(2, 2, 3), Matrix44.translate(1, 1, 1))
    xline.transform(m)

    assert xline.dxf.start == (5, 7, 13)
    assert xline.dxf.unit_vector == (1, 0, 0)


def test_xline_fast_translation():
    # same implementation for Ray()
    xline = XLine.new(dxfattribs={'start': (2, 3, 4), 'unit_vector': (1, 0, 0)})
    xline.translate(1, 2, 3)
    assert xline.dxf.start == (3, 5, 7)
    assert xline.dxf.unit_vector == (1, 0, 0)


def test_mesh_transform_interface():
    mesh = Mesh()
    mesh.vertices.append(Vector(1, 2, 3))
    mesh.transform(Matrix44.translate(1, 1, 1))
    assert mesh.vertices[0] == (2, 3, 4)


def test_spline_transform_interface():
    spline = Spline()
    spline.set_uniform([(1, 0, 0), (3, 3, 0), (6, 0, 1)])
    spline.dxf.start_tangent = Vector(1, 0, 0)
    spline.dxf.end_tangent = Vector(2, 0, 0)
    spline.dxf.extrusion = Vector(3, 0, 0)
    spline.transform(Matrix44.translate(1, 2, 3))
    assert spline.control_points[0] == (2, 2, 3)
    # direction vectors are not transformed by translation
    assert spline.dxf.start_tangent == (1, 0, 0)
    assert spline.dxf.end_tangent == (2, 0, 0)
    assert spline.dxf.extrusion == (3, 0, 0)


def test_solid_transform_interface():
    solid = Solid()
    solid.dxf.vtx1 = (3, 3, 0)
    solid.translate(1, 1, 0)
    assert solid.dxf.vtx1 == (4, 4, 0)


def test_trace_transform_interface():
    face = Face3d()
    face.dxf.vtx1 = (3, 3, 0)
    face.translate(1, 1, 0)
    assert face.dxf.vtx1 == (4, 4, 0)


def test_lwpolyline_transform_interface():
    pline = LWPolyline()
    pline.set_points([(0, 0), (2, 0), (1, 1)], format='xy')
    pline.translate(1, 1, 1)
    vertices = list(pline.vertices())
    assert vertices[0] == (1, 1)
    assert vertices[1] == (3, 1)
    assert vertices[2] == (2, 2)
    assert pline.dxf.elevation == 1
    assert Vector(0, 0, 1).isclose(pline.dxf.extrusion)


def test_polyline2d_transform_interface():
    pline = Polyline()
    pline.append_vertices([(0, 0, 0), (2, 0, 0), (1, 1, 0)])
    pline.translate(1, 1, 1)
    vertices = list(v.dxf.location for v in pline.vertices)
    assert pline.is_2d_polyline is True
    assert vertices[0] == (1, 1, 1)
    assert vertices[1] == (3, 1, 1)
    assert vertices[2] == (2, 2, 1)
    assert pline.dxf.elevation == (0, 0, 1)
    assert Vector(0, 0, 1).isclose(pline.dxf.extrusion)


def test_polyline3d_transform_interface():
    pline = Polyline.new(dxfattribs={'flags': 8})
    pline.append_vertices([(0, 0, 0), (2, 0, 0), (1, 1, 0)])
    pline.translate(1, 1, 1)
    vertices = list(v.dxf.location for v in pline.vertices)
    assert pline.is_3d_polyline is True
    assert vertices[0] == (1, 1, 1)
    assert vertices[1] == (3, 1, 1)
    assert vertices[2] == (2, 2, 1)


def test_text_transform_interface():
    text = Text()
    text.dxf.insert = (1, 0, 0)
    text.transform(Matrix44.translate(1, 2, 3))
    assert text.dxf.insert == (2, 2, 3)

    # optimized translate
    text.dxf.align_point = (3, 2, 1)
    text.translate(1, 2, 3)
    assert text.dxf.insert == (3, 4, 6)
    assert text.dxf.align_point == (4, 4, 4)


def test_mtext_transform_interface():
    mtext = MText()
    mtext.dxf.insert = (1, 0, 0)
    mtext.translate(1, 2, 3)
    assert mtext.dxf.insert == (2, 2, 3)


def test_insert_transform_interface():
    insert = Insert()
    insert.dxf.insert = (1, 0, 0)

    insert.transform(Matrix44.translate(1, 2, 3))
    assert insert.dxf.insert == (2, 2, 3)

    # optimized translate implementation
    insert.translate(-1, -2, -3)
    assert insert.dxf.insert == (1, 0, 0)

    insert.scale(2, 3, 4)
    assert insert.dxf.xscale == 2
    assert insert.dxf.yscale == 3
    assert insert.dxf.zscale == 4


def test_dimension_transform_interface():
    dim = Dimension()
    dim.dxf.insert = (1, 0, 0)  # OCS point
    dim.dxf.defpoint = (0, 1, 0)  # WCS point
    dim.dxf.angle = 45

    dim.transform(Matrix44.translate(1, 2, 3))
    assert dim.dxf.insert == (2, 2, 3)
    assert dim.dxf.defpoint == (1, 3, 3)
    assert dim.dxf.angle == 45

    dim.transform(Matrix44.z_rotate(math.radians(45)))
    assert dim.dxf.angle == 90


if __name__ == '__main__':
    pytest.main([__file__])
