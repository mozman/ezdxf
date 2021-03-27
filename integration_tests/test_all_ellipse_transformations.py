#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from itertools import product
import math
from ezdxf.math import Matrix44, linspace, Vec3
from ezdxf.entities import Ellipse

UNIFORM_SCALING = [(2, 2, 2), (-1, 1, 1), (1, -1, 1), (1, 1, -1), (-2, -2, 2),
                   (2, -2, -2), (-2, 2, -2), (-3, -3, -3)]
NON_UNIFORM_SCALING = [(-1, 2, 3), (1, -2, 3), (1, 2, -3), (-3, -2, 1),
                       (3, -2, -1), (-3, 2, -1), (-3, -2, -1)]

# chose fixed "random" values to narrow error space:
DELTA = [-2, -1, 0, 1, 2]


def synced_transformation(entity, chk, m: Matrix44):
    entity = entity.copy()
    entity.transform(m)
    chk = list(m.transform_vertices(chk))
    return entity, chk


def synced_scaling(entity, chk, sx=1, sy=1, sz=1):
    entity = entity.copy()
    entity.scale(sx, sy, sz)
    chk = list(Matrix44.scale(sx, sy, sz).transform_vertices(chk))
    return entity, chk


# Detected error conditions:
# CONFIG sx=-3, sy=2, sz=-1; start=5.7596, end=0.5236; dx=2, dy=2, dz=2; axis=(0.9071626602531079, 0.30514034769743803, -0.28973311175906485)

@pytest.mark.parametrize('sx, sy, sz', UNIFORM_SCALING + NON_UNIFORM_SCALING)
@pytest.mark.parametrize('start, end', [
    # closed ellipse fails at non uniform scaling test, because no start-
    # and end param adjustment is applied, so generated vertices do not
    # match test vertices.
    (0, math.pi),  # half ellipse as special case
    (math.pi / 6, math.pi / 6 * 11),  # start < end
    (math.pi / 6 * 11, math.pi / 6),  # start > end
])
def test_random_ellipse_transformations(sx, sy, sz, start, end):
    vertex_count = 8

    def build(angle, dx, dy, dz, axis):
        ellipse = Ellipse.new(dxfattribs={
            'start_param': start,
            'end_param': end,
        })
        vertices = list(ellipse.vertices(ellipse.params(vertex_count)))
        m = Matrix44.chain(
            Matrix44.axis_rotate(axis=axis, angle=angle),
            Matrix44.translate(dx=dx, dy=dy, dz=dz)
        )
        return synced_transformation(ellipse, vertices, m)

    def check(ellipse, vertices):
        ellipse_vertices = list(ellipse.vertices(ellipse.params(vertex_count)))
        # Ellipse vertices may appear in reverse order
        if not vertices[0].isclose(ellipse_vertices[0], abs_tol=1e-9):
            ellipse_vertices.reverse()

        for vtx, chk in zip(ellipse_vertices, vertices):
            assert vtx.isclose(chk, abs_tol=1e-9) is True, config

    for angle in linspace(0, math.tau, 19):
        for dx, dy, dz in product([2, 0, -2], repeat=3):
            axis = Vec3.random()  # TODO: fixed rotation axis

            config = f"CONFIG sx={sx}, sy={sy}, sz={sz}; " \
                     f"start={start:.4f}, end={end:.4f}; angle={angle};" \
                     f"dx={dx}, dy={dy}, dz={dz}; axis={str(axis)}"
            ellipse0, vertices0 = build(angle, dx, dy, dz, axis)
            check(ellipse0, vertices0)
            check(*synced_scaling(ellipse0, vertices0, sx, sy, sz))


if __name__ == '__main__':
    pytest.main([__file__])
