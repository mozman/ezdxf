# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import Union
import pytest
import random
import math
from ezdxf.entities import (
    DXFGraphic, Line, Point, Circle, Arc, Ellipse, XLine, Mesh, Spline, Solid, Face3d, LWPolyline, Polyline, Text,
    MText, Insert, Dimension,
)
from ezdxf.math import Matrix44, OCS, Vector, linspace
from ezdxf.math.transformtools import NonUniformScalingError

UNIFORM_SCALING = [(-1, 1, 1), (1, -1, 1), (1, 1, -1), (-2, -2, 2), (2, -2, -2), (-2, 2, -2), (-3, -3, -3)]
NON_UNIFORM_SCALING = [(-1, 2, 3), (1, -2, 3), (1, 2, -3), (-3, -2, 1), (3, -2, -1), (-3, 2, -1), (-3, -2, -1)]


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
    circle = Circle.new(dxfattribs={'center': (2, 3, 4), 'extrusion': Vector.random()})
    ocs = circle.ocs()
    offset = Vector(1, 2, 3)
    center = ocs.to_wcs(circle.dxf.center) + offset
    circle.translate(*offset)
    assert ocs.to_wcs(circle.dxf.center).isclose(center, abs_tol=1e-9)


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


def synced_scaling(entity, chk, sx=1, sy=1, sz=1):
    entity = entity.copy()
    entity.scale(sx, sy, sz)
    chk = list(Matrix44.scale(sx, sy, sz).transform_vertices(chk))
    return entity, chk


def synced_rotation(entity, chk, axis, angle):
    entity = entity.copy()
    entity.rotate_axis(axis, angle)
    chk = list(Matrix44.axis_rotate(axis, angle).transform_vertices(chk))
    return entity, chk


def synced_translation(entity, chk, dx, dy, dz):
    entity = entity.copy()
    entity.translate(dx, dy, dz)
    chk = list(Matrix44.translate(dx, dy, dz).transform_vertices(chk))
    return entity, chk


@pytest.mark.parametrize('sx, sy, sz', UNIFORM_SCALING)
def test_random_circle_transformation(sx, sy, sz):
    # testing only uniform scaling, for non uniform scaling
    # the circle has to be converted to an ellipse
    vertex_count = 8

    def build():
        circle = Circle()
        vertices = list(circle.vertices(linspace(0, 360, vertex_count, endpoint=False)))
        circle, vertices = synced_rotation(circle, vertices, axis=Vector.random(), angle=random.uniform(0, math.tau))
        circle, vertices = synced_translation(
            circle, vertices, dx=random.uniform(-2, 2), dy=random.uniform(-2, 2), dz=random.uniform(-2, 2))
        return circle, vertices

    def check(circle, vertices):
        # Vertex(angle=0) of old_ocs is not the vertex(angle=0) of the new OCS
        # because of the arbitrary Axis algorithm.

        # Checking center point:
        ocs = circle.ocs()
        wcs_circle_center = ocs.to_wcs(circle.dxf.center)
        vertices_center = vertices[0].lerp(vertices[int(vertex_count / 2)])
        assert wcs_circle_center.isclose(vertices_center, abs_tol=1e-9)

        # Check distance of vertices from circle center point:
        radius = circle.dxf.radius
        for vtx in vertices:
            assert math.isclose((vtx - wcs_circle_center).magnitude, radius, abs_tol=1e-9)

        # Check for parallel plane orientation
        vertices_extrusion = (vertices[0] - vertices_center).cross((vertices[1] - vertices_center))
        assert vertices_extrusion.is_parallel(circle.dxf.extrusion, abs_tol=1e-9)

    # test transformed circle against transformed WCS vertices of the circle
    for _ in range(10):
        circle0, vertices0 = build()
        check(circle0, vertices0)
        check(*synced_scaling(circle0, vertices0, sx, sy, sz))


@pytest.mark.parametrize('sx, sy, sz', UNIFORM_SCALING)
def test_random_arc_transformation(sx, sy, sz):
    # testing only uniform scaling, for non uniform scaling
    # the circle has to be converted to an ellipse
    vertex_count = 8

    def build():
        arc = Arc.new(dxfattribs={
            'start_angle': random.uniform(0, 360),
            'end_angle': random.uniform(0, 360),
        })

        vertices = list(arc.vertices(arc.angles(vertex_count)))
        arc, vertices = synced_rotation(arc, vertices, axis=Vector.random(), angle=random.uniform(0, math.tau))
        arc, vertices = synced_translation(
            arc, vertices, dx=random.uniform(-2, 2), dy=random.uniform(-2, 2), dz=random.uniform(-2, 2))
        return arc, vertices

    def check(arc, vertices):
        arc_vertices = arc.vertices(arc.angles(vertex_count))
        for vtx, chk in zip(arc_vertices, vertices):
            assert vtx.isclose(chk, abs_tol=1e-9)

    for _ in range(10):
        arc0, vertices0 = build()
        check(arc0, vertices0)
        check(*synced_scaling(arc0, vertices0, sx, sy, sz))


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


@pytest.mark.parametrize('sx, sy, sz', UNIFORM_SCALING + NON_UNIFORM_SCALING)
@pytest.mark.parametrize('start, end', [
    # closed ellipse fails at non uniform scaling test, because no start-
    # and end param adjustment is applied, so generated vertices do not
    # match test vertices.
    (0, math.pi),  # half ellipse as special case
    (math.pi / 6, math.pi / 6 * 11),  # start < end
    (math.pi / 6 * 11, math.pi / 6),  # start > end
])
def test_random_ellipse_transformation(sx, sy, sz, start, end):
    vertex_count = 8

    def build():
        ellipse = Ellipse.new(dxfattribs={
            'start_param': start,
            'end_param': end,
        })

        vertices = list(ellipse.vertices(ellipse.params(vertex_count)))
        ellipse, vertices = synced_rotation(ellipse, vertices, axis=Vector.random(), angle=random.uniform(0, math.tau))
        ellipse, vertices = synced_translation(
            ellipse, vertices, dx=random.uniform(-2, 2), dy=random.uniform(-2, 2), dz=random.uniform(-2, 2))
        return ellipse, vertices

    def check(ellipse, vertices):
        ellipse_vertices = list(ellipse.vertices(ellipse.params(vertex_count)))
        # Ellipse vertices may appear in reverse order
        if not vertices[0].isclose(ellipse_vertices[0], abs_tol=1e-9):
            ellipse_vertices.reverse()

        for vtx, chk in zip(ellipse_vertices, vertices):
            assert vtx.isclose(chk, abs_tol=1e-9)

    for _ in range(10):
        ellipse0, vertices0 = build()
        check(ellipse0, vertices0)
        check(*synced_scaling(ellipse0, vertices0, sx, sy, sz))


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


def test_insert_scaling():
    insert = Insert()
    insert.dxf.insert = (0, 0, 0)

    insert.scale(2, 3, 4)
    assert insert.dxf.xscale == 2
    assert insert.dxf.yscale == 3
    assert insert.dxf.zscale == 4

    insert.scale(-1, 1, 1)
    assert insert.dxf.xscale == -2
    assert insert.dxf.yscale == 3
    assert insert.dxf.zscale == 4

    insert.scale(-1, -1, 1)
    assert insert.dxf.xscale == 2
    assert insert.dxf.yscale == -3
    assert insert.dxf.zscale == 4

    insert.scale(-2, -2, -2)
    assert insert.dxf.xscale == -4
    assert insert.dxf.yscale == 6
    assert insert.dxf.zscale == -8


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
    assert math.isclose(dim.dxf.angle, 90)


if __name__ == '__main__':
    pytest.main([__file__])
