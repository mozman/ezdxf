# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from pathlib import Path
import math
import random
import ezdxf
from ezdxf.math import linspace, Vector, Matrix44, Z_AXIS
from ezdxf.entities import Circle, Arc, Ellipse

DIR = Path('~/Desktop/Outbox/ezdxf').expanduser()


def synced_scaling(entity, chk, axis_vertices=None, sx=1, sy=1, sz=1):
    entity = entity.copy()
    entity.scale(sx, sy, sz)
    m = Matrix44.scale(sx, sy, sz)
    chk = list(m.transform_vertices(chk))
    if axis_vertices:
        axis_vertices = list(m.transform_vertices(axis_vertices))
        return entity, chk, axis_vertices
    return entity, chk


def synced_rotation(entity, chk, axis_vertices=None, axis=Z_AXIS, angle=0):
    entity = entity.copy()
    entity.rotate_axis(axis, angle)
    m = Matrix44.axis_rotate(axis, angle)
    chk = list(m.transform_vertices(chk))
    if axis_vertices:
        axis_vertices = list(m.transform_vertices(axis_vertices))
        return entity, chk, axis_vertices
    return entity, chk


def synced_translation(entity, chk, axis_vertices=None, dx=0, dy=0, dz=0):
    entity = entity.copy()
    entity.translate(dx, dy, dz)
    m = Matrix44.translate(dx, dy, dz)
    chk = list(m.transform_vertices(chk))
    if axis_vertices:
        axis_vertices = list(m.transform_vertices(axis_vertices))
        return entity, chk, axis_vertices
    return entity, chk


def add(msp, entity, vertices, layer='0'):
    entity.dxf.layer = layer
    entity.dxf.color = 2
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


UNIFORM_SCALING = [(-1, 1, 1), (1, -1, 1), (1, 1, -1), (-2, -2, 2), (2, -2, -2), (-2, 2, -2), (-3, -3, -3)]
NON_UNIFORM_SCALING = [(-1, 2, 3), (1, -2, 3), (1, 2, -3), (-3, -2, 1), (3, -2, -1), (-3, 2, -1), (-3, -2, -1)]


def main(layout):
    def random_angle():
        return random.uniform(0, math.tau)

    entity, vertices, axis_vertices = ellipse(start=math.pi/2, end=-math.pi/2)
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


if __name__ == '__main__':
    doc = ezdxf.new('R2000', setup=True)
    msp = doc.modelspace()
    main(msp)
    doc.set_modelspace_vport(5)
    doc.saveas(DIR / 'transform.dxf')
