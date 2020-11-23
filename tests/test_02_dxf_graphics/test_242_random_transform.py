# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING
import pytest
import random
import math
from ezdxf.entities import Circle, Arc, Ellipse, Insert
from ezdxf.math import Matrix44, Vec3, linspace, X_AXIS, Y_AXIS, Z_AXIS
import ezdxf

if TYPE_CHECKING:
    from ezdxf.eztypes import Drawing

UNIFORM_SCALING = [(2, 2, 2), (-1, 1, 1), (1, -1, 1), (1, 1, -1), (-2, -2, 2), (2, -2, -2), (-2, 2, -2), (-3, -3, -3)]
NON_UNIFORM_SCALING = [(-1, 2, 3), (1, -2, 3), (1, 2, -3), (-3, -2, 1), (3, -2, -1), (-3, 2, -1), (-3, -2, -1)]
SCALING_WITHOUT_REFLEXIONS = [(1, 1, 1), (2, 2, 2), (1, 2, 3)]


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


def synced_transformation(entity, chk, m: Matrix44):
    entity = entity.copy()
    entity.transform(m)
    chk = list(m.transform_vertices(chk))
    return entity, chk


@pytest.mark.parametrize('sx, sy, sz', UNIFORM_SCALING)
def test_random_circle_transformation(sx, sy, sz):
    # testing only uniform scaling, for non uniform scaling
    # the circle has to be converted to an ellipse
    vertex_count = 8

    def build():
        circle = Circle()
        vertices = list(circle.vertices(linspace(0, 360, vertex_count, endpoint=False)))
        m = Matrix44.chain(
            Matrix44.axis_rotate(axis=Vec3.random(), angle=random.uniform(0, math.tau)),
            Matrix44.translate(dx=random.uniform(-2, 2), dy=random.uniform(-2, 2), dz=random.uniform(-2, 2)),
        )
        return synced_transformation(circle, vertices, m)

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
        m = Matrix44.chain(
            Matrix44.axis_rotate(axis=Vec3.random(), angle=random.uniform(0, math.tau)),
            Matrix44.translate(dx=random.uniform(-2, 2), dy=random.uniform(-2, 2), dz=random.uniform(-2, 2)),
        )
        return synced_transformation(arc, vertices, m)

    def check(arc, vertices):
        arc_vertices = arc.vertices(arc.angles(vertex_count))
        for vtx, chk in zip(arc_vertices, vertices):
            assert vtx.isclose(chk, abs_tol=1e-9)

    for _ in range(10):
        arc0, vertices0 = build()
        check(arc0, vertices0)
        check(*synced_scaling(arc0, vertices0, sx, sy, sz))


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
        m = Matrix44.chain(
            Matrix44.axis_rotate(axis=Vec3.random(), angle=random.uniform(0, math.tau)),
            Matrix44.translate(dx=random.uniform(-2, 2), dy=random.uniform(-2, 2), dz=random.uniform(-2, 2)),
        )
        return synced_transformation(ellipse, vertices, m)

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


@pytest.fixture(scope='module')
def doc1() -> 'Drawing':
    doc = ezdxf.new()
    blk = doc.blocks.new('AXIS')
    blk.add_line((0, 0, 0), X_AXIS, dxfattribs={'color': 1})
    blk.add_line((0, 0, 0), Y_AXIS, dxfattribs={'color': 3})
    blk.add_line((0, 0, 0), Z_AXIS, dxfattribs={'color': 5})
    return doc


@pytest.mark.parametrize('sx, sy, sz', UNIFORM_SCALING + NON_UNIFORM_SCALING)
def test_random_block_reference_transformation(sx, sy, sz, doc1: 'Drawing'):
    def insert():
        return Insert.new(dxfattribs={
            'name': 'AXIS',
            'insert': (0, 0, 0),
            'xscale': 1,
            'yscale': 1,
            'zscale': 1,
            'rotation': 0,
            'layer': 'insert',
        }, doc=doc1), [Vec3(0, 0, 0), X_AXIS, Y_AXIS, Z_AXIS]

    def check(lines, chk):
        origin, x, y, z = chk
        l1, l2, l3 = lines
        assert origin.isclose(l1.dxf.start)
        assert x.isclose(l1.dxf.end)
        assert origin.isclose(l2.dxf.start)
        assert y.isclose(l2.dxf.end)
        assert origin.isclose(l3.dxf.start)
        assert z.isclose(l3.dxf.end)

    entity0, vertices0 = insert()
    entity0, vertices0 = synced_scaling(entity0, vertices0, 1, 2, 3)

    m = Matrix44.chain(
        # Transformation order is important: scale - rotate - translate
        # Because scaling after rotation leads to a non orthogonal
        # coordinate system, which can not represented by the
        # INSERT entity.
        Matrix44.scale(sx, sy, sz),
        Matrix44.axis_rotate(axis=Vec3.random(), angle=random.uniform(0, math.tau)),
        Matrix44.translate(dx=random.uniform(-2, 2), dy=random.uniform(-2, 2), dz=random.uniform(-2, 2)),
    )
    entity, vertices = synced_transformation(entity0, vertices0, m)
    lines = list(entity.virtual_entities())
    check(lines, vertices)


@pytest.mark.parametrize('sx, sy, sz', [
    # Non uniform scaling will throw InsertTransformationError(),
    # because this multiple applied transformations cause non orthogonal
    # target coordinate systems, which can not represented by the INSERT entity.
    (1.1, 1.1, 1.1), (-1.1, -1.1, -1.1),
    (-1.1, 1.1, 1.1), (1.1, -1.1, 1.1), (1.1, 1.1, -1.1),
    (-1.1, -1.1, 1.1), (1.1, -1.1, -1.1), (-1.1, 1.1, -1.1),
])
def test_apply_transformation_multiple_times(sx, sy, sz, doc1: 'Drawing'):
    def insert():
        return Insert.new(dxfattribs={
            'name': 'AXIS',
            'insert': (0, 0, 0),
            'xscale': 1,
            'yscale': 1,
            'zscale': 1,
            'rotation': 0,
        }, doc=doc1), [(0, 0, 0), X_AXIS, Y_AXIS, Z_AXIS]

    entity, vertices = insert()
    m = Matrix44.chain(
        Matrix44.scale(sx, sy, sz),
        Matrix44.z_rotate(math.radians(10)),
        Matrix44.translate(1, 1, 1),
    )

    for i in range(5):
        entity, vertices = synced_transformation(entity, vertices, m)
        points = list(vertices)
        for num, line in enumerate(entity.virtual_entities()):
            assert points[0].isclose(line.dxf.start, abs_tol=1e-9)
            assert points[num + 1].isclose(line.dxf.end, abs_tol=1e-9)


if __name__ == '__main__':
    pytest.main([__file__])
