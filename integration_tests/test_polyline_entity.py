# Copyright 2018, Manfred Moitzi
# License: MIT License
import os
import math
import random
import pytest
import ezdxf
from ezdxf.lldxf.const import versions_supported_by_new

MSIZE = 20
HEIGHT = 3.


@pytest.fixture(params=versions_supported_by_new)
def drawing(request):
    return ezdxf.new(request.param)


def build_mesh(polymesh):
    m_size = polymesh.dxf.m_count
    n_size = polymesh.dxf.n_count
    m_delta = math.pi / m_size
    n_delta = math.pi / n_size

    for x in range(m_size):
        sinx = math.sin(float(x)*m_delta)
        for y in range(n_size):
            cosy = math.cos(float(y)*n_delta)
            z = sinx * cosy * HEIGHT
            # set the m,n vertex to 3d point x,y,z
            polymesh.set_mesh_vertex(pos=(x, y), point=(x, y, z))


def build_cube(layout, basepoint, length):
    def scale(point):
        return ((basepoint[0]+point[0]*length),
                (basepoint[1]+point[1]*length),
                (basepoint[2]+point[2]*length))

    # cube corner points
    p1 = scale((0, 0, 0))
    p2 = scale((0, 0, 1))
    p3 = scale((0, 1, 0))
    p4 = scale((0, 1, 1))
    p5 = scale((1, 0, 0))
    p6 = scale((1, 0, 1))
    p7 = scale((1, 1, 0))
    p8 = scale((1, 1, 1))

    # define the 6 cube faces
    # look into -x direction
    # Every add_face adds 4 vertices 6x4 = 24 vertices
    pface = layout.add_polyface()
    pface.append_face([p1, p5, p7, p3], {'color': 1})  # base
    pface.append_face([p1, p5, p6, p2], {'color': 2})  # left
    pface.append_face([p5, p7, p8, p6], {'color': 3})  # front
    pface.append_face([p7, p8, p4, p3], {'color': 4})  # right
    pface.append_face([p1, p3, p4, p2], {'color': 5})  # back
    pface.append_face([p2, p6, p8, p4], {'color': 6})  # top


def add_polymesh(layout):
    polymesh = layout.add_polymesh(size=(MSIZE, MSIZE))
    build_mesh(polymesh)


def add_polyfaces(layout):
    for x in range(10):
        for y in range(10):
            build_cube(layout, basepoint=(x, y, random.random()), length=random.random())


def add_polyline2d(layout):
    points2d = [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0), (1, 1), (.5, 1.5), (0, 1), (1, 0)]
    layout.add_polyline2d(points2d)


def add_polyline3d(layout):
    points3d = [(3, 3, 0), (6, 3, 1), (6, 6, 2), (3, 6, 3), (3, 3, 4)]
    layout.add_polyline3d(points3d)


def test_create_polyline_entities(drawing, tmpdir):
    modelspace = drawing.modelspace()

    add_polyline2d(modelspace)
    add_polyline3d(modelspace)
    add_polyfaces(modelspace)
    add_polymesh(modelspace)

    filename = str(tmpdir.join('polyline_entities_%s.dxf' % drawing.dxfversion))
    try:
        drawing.saveas(filename)
    except ezdxf.DXFError as e:
        pytest.fail("DXFError: {0} for DXF version {1}".format(str(e), drawing.dxfversion))
    assert os.path.exists(filename)

