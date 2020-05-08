# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from pathlib import Path
import math
import random
import ezdxf
from ezdxf.math import linspace, Vector, Matrix44
from ezdxf.entities import Circle, Arc, Ellipse

DIR = Path('~/Desktop/Outbox/ezdxf').expanduser()


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


def add(msp, entity, vertices, layer='0'):
    entity.dxf.layer = layer
    entity.dxf.color = 3
    msp.add_entity(entity)
    msp.add_polyline3d(vertices, dxfattribs={'layer': 'check', 'color': 6})


def circle(radius=1, count=16):
    circle_ = Circle.new(dxfattribs={'center': (0, 0, 0), 'radius': radius}, doc=doc)
    control_vertices = list(circle_.vertices(linspace(0, 360, count)))
    return circle_, control_vertices


def arc(radius=1, start=30, end=150, count=8):
    arc_ = Arc.new(dxfattribs={'center': (0, 0, 0), 'radius': radius, 'start_angle': start, 'end_angle': end}, doc=doc)
    control_vertices = list(arc_.vertices(arc_.angles(count)))
    return arc_, control_vertices


def ellipse(major_axis=(1, 0), ratio=0.5, start=0, end=math.tau, count=8):
    major_axis = Vector(major_axis).replace(z=0)
    ellipse_ = Ellipse.new(dxfattribs={
        'center': (0, 0, 0),
        'major_axis': major_axis,
        'ratio': min(max(ratio, 1e-6), 1),
        'start_param': start,
        'end_param': end
    }, doc=doc)
    control_vertices = list(ellipse_.vertices(ellipse_.params(count)))
    return ellipse_, control_vertices


UNIFORM_SCALING = [(-1, 1, 1), (1, -1, 1), (1, 1, -1), (-2, -2, 2), (2, -2, -2), (-2, 2, -2), (-3, -3, -3)]
NON_UNIFORM_SCALING = [(-1, 2, 3), (1, -2, 3), (1, 2, -3), (-3, -2, 1), (3, -2, -1), (-3, 2, -1), (-3, -2, -1)]


def main(layout):
    def random_angle():
        return random.uniform(0, math.tau)

    entity, vertices = ellipse(start=random_angle(), end=random_angle())
    axis = Vector.random()
    angle = random_angle()
    entity, vertices = synced_rotation(entity, vertices, axis, angle)
    entity, vertices = synced_translation(
        entity, vertices,
        dx=random.uniform(-2, 2),
        dy=random.uniform(-2, 2),
        dz=random.uniform(-2, 2)
    )

    for sx, sy, sz in UNIFORM_SCALING:
        entity0, vertices0 = synced_scaling(entity, vertices, sx, sy, sz)
        add(layout, entity0, vertices0, layer=f'scale {sx} {sy} {sz}')


if __name__ == '__main__':
    doc = ezdxf.new('R2000')
    msp = doc.modelspace()
    main(msp)
    doc.set_modelspace_vport(5)
    doc.saveas(DIR / 'transform.dxf')
