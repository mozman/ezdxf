# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import cast
from pathlib import Path
import math
import random
import ezdxf
from ezdxf.math import linspace, Vector, Matrix44, Z_AXIS, Y_AXIS, X_AXIS
from ezdxf.entities import Circle, Arc, Ellipse, Insert, Text, MText, Hatch

DIR = Path('~/Desktop/Outbox').expanduser()
UNIFORM_SCALING = [(-1, 1, 1), (1, -1, 1), (1, 1, -1), (-2, -2, 2), (2, -2, -2), (-2, 2, -2), (-3, -3, -3)]
NON_UNIFORM_SCALING = [(-1, 2, 3.1), (1, -2, 3.2), (1, 2, -3.3), (-3.4, -2, 1), (3.5, -2, -1), (-3.6, 2, -1),
                       (-3.7, -2, -1)]

SCALING_WITHOUT_REFLEXION = [(2, 2, 2), (1, 2, 3)]


def setup_csys_blk(name: str):
    blk = doc.blocks.new(name)
    blk.add_line((0, 0, 0), X_AXIS, dxfattribs={'color': 1})
    blk.add_line((0, 0, 0), Y_AXIS, dxfattribs={'color': 3})
    blk.add_line((0, 0, 0), Z_AXIS, dxfattribs={'color': 5})


def random_angle():
    return random.uniform(0, math.tau)


def synced_scaling(entity, chk, axis_vertices=None, sx: float = 1, sy: float = 1, sz: float = 1):
    entity = entity.copy()
    entity.scale(sx, sy, sz)
    m = Matrix44.scale(sx, sy, sz)
    chk = list(m.transform_vertices(chk))
    if axis_vertices:
        axis_vertices = list(m.transform_vertices(axis_vertices))
        return entity, chk, axis_vertices
    return entity, chk


def synced_rotation(entity, chk, axis_vertices=None, axis=Z_AXIS, angle: float = 0):
    entity = entity.copy()
    entity.rotate_axis(axis, angle)
    m = Matrix44.axis_rotate(axis, angle)
    chk = list(m.transform_vertices(chk))
    if axis_vertices:
        axis_vertices = list(m.transform_vertices(axis_vertices))
        return entity, chk, axis_vertices
    return entity, chk


def synced_translation(entity, chk, axis_vertices=None, dx: float = 0, dy: float = 0, dz: float = 0):
    entity = entity.copy()
    entity.translate(dx, dy, dz)
    m = Matrix44.translate(dx, dy, dz)
    chk = list(m.transform_vertices(chk))
    if axis_vertices:
        axis_vertices = list(m.transform_vertices(axis_vertices))
        return entity, chk, axis_vertices
    return entity, chk


def synced_transformation(entity, chk, m: Matrix44):
    entity = entity.copy()
    entity.transform(m)
    chk = list(m.transform_vertices(chk))
    return entity, chk


def add(msp, entity, vertices, layer='0'):
    entity.dxf.layer = layer
    entity.dxf.color = 2
    msp.entitydb.add(entity)
    msp.add_entity(entity)
    msp.add_polyline3d(vertices, dxfattribs={'layer': 'vertices', 'color': 6})


def circle(radius=1, count=16):
    circle_ = Circle.new(dxfattribs={'center': (0, 0, 0), 'radius': radius}, doc=doc)
    control_vertices = list(circle_.vertices(linspace(0, 360, count)))
    return circle_, control_vertices


def arc(radius=1, start=30, end=150, count=8):
    arc_ = Arc.new(dxfattribs={'center': (0, 0, 0), 'radius': radius, 'start_angle': start, 'end_angle': end}, doc=doc)
    control_vertices = list(arc_.vertices(arc_.angles(count)))
    return arc_, control_vertices


def ellipse(major_axis=(1, 0), ratio: float = 0.5, start: float = 0, end: float = math.tau, count: int = 8):
    major_axis = Vector(major_axis).replace(z=0)
    ellipse_ = Ellipse.new(dxfattribs={
        'center': (0, 0, 0),
        'major_axis': major_axis,
        'ratio': min(max(ratio, 1e-6), 1),
        'start_param': start,
        'end_param': end
    }, doc=doc)
    control_vertices = list(ellipse_.vertices(ellipse_.params(count)))
    axis_vertices = list(ellipse_.vertices([0, math.pi / 2, math.pi, math.pi * 1.5]))
    return ellipse_, control_vertices, axis_vertices


def insert():
    return Insert.new(dxfattribs={
        'name': 'UCS',
        'insert': (0, 0, 0),
        'xscale': 1,
        'yscale': 1,
        'zscale': 1,
        'rotation': 0,
        'layer': 'insert',
    }, doc=doc), [(0, 0, 0), X_AXIS, Y_AXIS, Z_AXIS]


def main_ellipse(layout):
    entity, vertices, axis_vertices = ellipse(start=math.pi / 2, end=-math.pi / 2)
    axis = Vector.random()
    angle = random_angle()
    entity, vertices, axis_vertices = synced_rotation(entity, vertices, axis_vertices, axis=axis, angle=angle)
    entity, vertices, axis_vertices = synced_translation(
        entity, vertices, axis_vertices,
        dx=random.uniform(-2, 2),
        dy=random.uniform(-2, 2),
        dz=random.uniform(-2, 2)
    )

    for sx, sy, sz in UNIFORM_SCALING + NON_UNIFORM_SCALING:
        entity0, vertices0, axis0 = synced_scaling(entity, vertices, axis_vertices, sx, sy, sz)
        add(layout, entity0, vertices0, layer=f'new ellipse')
        layout.add_line(axis0[0], axis0[2], dxfattribs={'color': 6, 'linetype': 'DASHED', 'layer': 'old axis'})
        layout.add_line(axis0[1], axis0[3], dxfattribs={'color': 6, 'linetype': 'DASHED', 'layer': 'old axis'})
        p = list(entity0.vertices([0, math.pi / 2, math.pi, math.pi * 1.5]))
        layout.add_line(p[0], p[2], dxfattribs={'color': 1, 'layer': 'new axis'})
        layout.add_line(p[1], p[3], dxfattribs={'color': 3, 'layer': 'new axis'})


def main_multi_ellipse(layout):
    m = Matrix44.chain(
        Matrix44.scale(1.1, 1.3, 1),
        Matrix44.z_rotate(math.radians(10)),
        Matrix44.translate(1, 1, 0),
    )
    entity, vertices, axis_vertices = ellipse(start=math.pi / 2, end=-math.pi / 2)

    for index in range(5):
        entity, vertices = synced_transformation(entity, vertices, m)
        add(layout, entity, vertices)


def main_insert(layout):
    entity, vertices = insert()
    entity, vertices = synced_translation(entity, vertices, dx=1, dy=0, dz=0)
    axis = Vector.random()
    angle = random_angle()

    for sx, sy, sz in NON_UNIFORM_SCALING:
        # 1. scale
        entity0, vertices0 = synced_scaling(entity, vertices, sx=sx, sy=sy, sz=sz)
        # 2. rotate
        entity0, vertices0 = synced_rotation(entity0, vertices0, axis=axis, angle=angle)
        # 3. translate
        entity0, vertices0 = synced_translation(
            entity0, vertices0,
            dx=random.uniform(-2, 2),
            dy=random.uniform(-2, 2),
            dz=random.uniform(-2, 2)
        )
        layout.entitydb.add(entity0)
        layout.add_entity(entity0)
        origin, x, y, z = list(vertices0)
        layout.add_line(origin, x, dxfattribs={'color': 2, 'layer': 'new axis'})
        layout.add_line(origin, y, dxfattribs={'color': 4, 'layer': 'new axis'})
        layout.add_line(origin, z, dxfattribs={'color': 6, 'layer': 'new axis'})

        for line in entity0.virtual_entities():
            line.dxf.layer = 'exploded axis'
            line.dxf.color = 7
            layout.entitydb.add(line)
            layout.add_entity(line)


def main_insert2(layout):
    entity, vertices = insert()
    m = Matrix44.chain(
        Matrix44.scale(-1.1, 1.1, 1),
        Matrix44.z_rotate(math.radians(10)),
        Matrix44.translate(1, 1, 1),
    )
    doc.layers.new('exploded axis', dxfattribs={'color': -7})

    for i in range(5):
        entity, vertices = synced_transformation(entity, vertices, m)
        layout.entitydb.add(entity)
        layout.add_entity(entity)

        origin, x, y, z = list(vertices)
        layout.add_line(origin, x, dxfattribs={'color': 2, 'layer': 'new axis'})
        layout.add_line(origin, y, dxfattribs={'color': 4, 'layer': 'new axis'})
        layout.add_line(origin, z, dxfattribs={'color': 6, 'layer': 'new axis'})

        for line in entity.virtual_entities():
            line.dxf.layer = 'exploded axis'
            line.dxf.color = 7
            layout.entitydb.add(line)
            layout.add_entity(line)


def main_text(layout):
    content = '{}RSKNZQ'

    def text(num):
        height = 1.0
        width = 1.0
        p1 = Vector(0, 0, 0)

        t = Text.new(dxfattribs={
            'text': content.format(num),  # should easily show reflexion errors
            'height': height,
            'width': width,
            'rotation': 0,
            'layer': 'text',
        }, doc=doc)
        t.set_pos(p1, align='LEFT')
        tlen = height * len(t.dxf.text) * width
        p2 = p1.replace(x=tlen)
        p3 = p2.replace(y=height)
        p4 = p1.replace(y=height)
        v = [p1, p2, p3, p4, p3.lerp(p4), p2.lerp(p3)]
        return t, v

    def add_box(vertices):
        p1, p2, p3, p4, center_top, center_right = vertices
        layout.add_line(p1, p2, dxfattribs={'color': 1, 'layer': 'rect'})
        layout.add_line(p2, p3, dxfattribs={'color': 3, 'layer': 'rect'})
        layout.add_line(p3, p4, dxfattribs={'color': 1, 'layer': 'rect'})
        layout.add_line(p4, p1, dxfattribs={'color': 3, 'layer': 'rect'})
        layout.add_line(center_right, p1, dxfattribs={'color': 2, 'layer': 'rect'})
        layout.add_line(center_right, p4, dxfattribs={'color': 2, 'layer': 'rect'})
        layout.add_line(center_top, p1, dxfattribs={'color': 4, 'layer': 'rect'})
        layout.add_line(center_top, p2, dxfattribs={'color': 4, 'layer': 'rect'})

    entity0, vertices0 = text(1)
    entity0, vertices0 = synced_rotation(entity0, vertices0, axis=Z_AXIS, angle=math.radians(30))
    entity0, vertices0 = synced_translation(entity0, vertices0, dx=3, dy=3)

    for i, reflexion in enumerate([(1, 2), (-1, 2), (-1, -2), (1, -2)]):
        rx, ry = reflexion
        m = Matrix44.chain(
            Matrix44.scale(rx, ry, 1),
        )
        entity, vertices = synced_transformation(entity0, vertices0, m)
        entity.dxf.text = content.format(i + 1)

        layout.add_entity(entity)
        add_box(vertices)


def main_mtext(layout):
    content = '{}RSKNZQ'

    def mtext(num):
        height = 1.0
        width = 1.0
        p1 = Vector(0, 0, 0)

        t = MText.new(dxfattribs={
            'char_height': height,
            'width': width,
            'text_direction': (1, 0, 0),
            'attachment_point': 7,
            'layer': 'text',
        }, doc=doc)
        t.text = content.format(num)
        tlen = height * len(t.text) * width
        p2 = p1.replace(x=tlen)
        p3 = p2.replace(y=height)
        p4 = p1.replace(y=height)
        v = [p1, p2, p3, p4, p3.lerp(p4), p2.lerp(p3)]
        return t, v

    def add_box(vertices):
        p1, p2, p3, p4, center_top, center_right = vertices
        layout.add_line(p1, p2, dxfattribs={'color': 1, 'layer': 'rect'})
        layout.add_line(p2, p3, dxfattribs={'color': 3, 'layer': 'rect'})
        layout.add_line(p3, p4, dxfattribs={'color': 1, 'layer': 'rect'})
        layout.add_line(p4, p1, dxfattribs={'color': 3, 'layer': 'rect'})
        layout.add_line(center_right, p1, dxfattribs={'color': 2, 'layer': 'rect'})
        layout.add_line(center_right, p4, dxfattribs={'color': 2, 'layer': 'rect'})
        layout.add_line(center_top, p1, dxfattribs={'color': 4, 'layer': 'rect'})
        layout.add_line(center_top, p2, dxfattribs={'color': 4, 'layer': 'rect'})

    entity0, vertices0 = mtext(1)
    entity0, vertices0 = synced_rotation(entity0, vertices0, axis=Z_AXIS, angle=math.radians(30))
    entity0, vertices0 = synced_translation(entity0, vertices0, dx=3, dy=3)

    for i, reflexion in enumerate([(1, 2), (-1, 2), (-1, -2), (1, -2)]):
        rx, ry = reflexion
        m = Matrix44.chain(
            Matrix44.scale(rx, ry, 1),
        )
        entity, vertices = synced_transformation(entity0, vertices0, m)
        entity.text = content.format(i + 1)

        layout.add_entity(entity)
        add_box(vertices)


def hatch_polyline(msp, edge_path=True):
    vertices = [(0, 0, 1), (10, 0), (10, 10, -0.5), (0, 10)]
    hatch = msp.add_hatch(color=1)
    hatch.paths.add_polyline_path(vertices, is_closed=1)
    if edge_path:
        hatch.paths.arc_edges_to_ellipse_edges()
    lwpoly = msp.add_lwpolyline(vertices, format='xyb', dxfattribs={'color': 1, 'closed': 1})
    return hatch, lwpoly


def main_uniform_hatch_polyline(layout):
    entitydb = layout.doc.entitydb
    hatch, lwpolyline = hatch_polyline(layout, edge_path=False)
    m = Matrix44.chain(
        Matrix44.scale(-1.1, 1.1, 1),
        Matrix44.z_rotate(math.radians(10)),
        Matrix44.translate(1, 1, 1),
    )
    for index in range(4):
        color = 2 + index

        hatch = hatch.copy()
        entitydb.add(hatch)
        hatch.dxf.color = color
        hatch.transform(m)

        lwpolyline = lwpolyline.copy()
        entitydb.add(lwpolyline)
        lwpolyline.dxf.color = color
        lwpolyline.transform(m)

        layout.add_entity(lwpolyline)
        layout.add_entity(hatch)


def main_non_uniform_hatch_polyline(layout, spline=False):
    entitydb = layout.doc.entitydb
    hatch, lwpolyline = hatch_polyline(layout)
    if spline:
        hatch.paths.all_to_spline_edges()

    m = Matrix44.chain(
        Matrix44.scale(-1.1, 1.1, 1),
        Matrix44.z_rotate(math.radians(10)),
        Matrix44.translate(1, 1, 1),
    )
    for index in range(4):
        color = 2 + index
        hatch = hatch.copy()
        entitydb.add(hatch)
        hatch.dxf.color = color
        hatch.transform(m)
        layout.add_entity(hatch)


def main_ellipse_hatch(layout, spline=False):
    def draw_ellipse_axis(ellipse):
        center = ellipse.center
        major_axis = ellipse.major_axis
        msp.add_line(center, center + major_axis)

    entitydb = layout.doc.entitydb
    hatch = cast(Hatch, layout.add_hatch(color=1))
    path = hatch.paths.add_edge_path()
    path.add_line((0, 0), (5, 0))
    path.add_ellipse((2.5, 0), (2.5, 0), ratio=.5, start_angle=0, end_angle=180, ccw=1)
    if spline:
        hatch.paths.all_to_line_edges(spline_factor=4)

    chk_ellipse, chk_vertices, _ = ellipse((2.5, 0), ratio=0.5, start=0, end=math.pi)
    chk_ellipse, chk_vertices = synced_translation(chk_ellipse, chk_vertices, dx=2.5)

    m = Matrix44.chain(
        Matrix44.scale(1.1, 1.3, 1),
        Matrix44.z_rotate(math.radians(15)),
        Matrix44.translate(1, 1, 0),
    )
    for index in range(3):
        color = 2 + index

        hatch = hatch.copy()
        entitydb.add(hatch)
        hatch.dxf.color = color
        hatch.transform(m)
        layout.add_entity(hatch)

        ellipse_edge = hatch.paths[0].edges[1]
        if not spline:
            draw_ellipse_axis(ellipse_edge)

        chk_ellipse, chk_vertices = synced_transformation(chk_ellipse, chk_vertices, m)
        add(layout, chk_ellipse, chk_vertices)


def add_hatch_for_all_ellipses(layout):
    for ellipse in layout.query('ELLIPSE'):
        hatch = layout.add_hatch(color=2, dxfattribs={
            'extrusion': ellipse.dxf.extrusion,
            'layer': 'HATCH',
        })
        path = hatch.paths.add_edge_path()
        e = ellipse.construction_tool().to_ocs()
        hatch.dxf.elevation = e.center.replace(x=0, y=0)
        edge = path.add_ellipse(
            center=e.center.vec2,
            major_axis=e.major_axis.vec2,
            ratio=e.ratio,
        )
        edge.start_param = e.start_param
        edge.end_param = e.end_param


if __name__ == '__main__':
    doc = ezdxf.new('R2000', setup=True)
    setup_csys_blk('UCS')
    msp = doc.modelspace()
    # main_ellipse(msp)
    # main_multi_ellipse(msp)
    # add_hatch_for_all_ellipses(msp)
    # main_text(msp)
    # main_mtext(msp)
    # main_insert(msp)
    # main_insert2(msp)
    # main_uniform_hatch_polyline(msp)
    main_ellipse_hatch(msp, spline=True)
    # main_non_uniform_hatch_polyline(msp, spline=True)
    doc.set_modelspace_vport(5)
    doc.saveas(DIR / 'transform.dxf')
