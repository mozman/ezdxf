# Copyright (c) 2018-2020, Manfred Moitzi
# License: MIT License
import pytest
from math import radians
import ezdxf
from ezdxf.math import Vector, BoundingBox
from ezdxf.render.forms import cube
from ezdxf.render.mesh import MeshVertexMerger, MeshBuilder, MeshTransformer
from ezdxf.addons import SierpinskyPyramid


def test_vertex_merger_indices():
    merger = MeshVertexMerger()
    indices = merger.add_vertices([(1, 2, 3), (4, 5, 6)])
    indices2 = merger.add_vertices([(1, 2, 3), (4, 5, 6)])
    assert indices == indices2


def test_vertex_merger_vertices():
    merger = MeshVertexMerger()
    merger.add_vertices([(1, 2, 3), (4, 5, 6)])
    merger.add_vertices([(1, 2, 3), (4, 5, 6)])
    assert merger.vertices == [(1, 2, 3), (4, 5, 6)]


def test_vertex_merger_index_of():
    merger = MeshVertexMerger()
    merger.add_vertices([(1, 2, 3), (4, 5, 6)])
    assert merger.index((1, 2, 3)) == 0
    assert merger.index((4, 5, 6)) == 1
    with pytest.raises(IndexError):
        merger.index((7, 8, 9))


def test_mesh_builder():
    dwg = ezdxf.new('R2000')
    pyramid = SierpinskyPyramid(level=4, sides=3)
    pyramid.render(dwg.modelspace(), merge=False)
    meshes = dwg.modelspace().query('MESH')
    assert len(meshes) == 256


def test_vertex_merger():
    dwg = ezdxf.new('R2000')
    pyramid = SierpinskyPyramid(level=4, sides=3)
    pyramid.render(dwg.modelspace(), merge=True)
    meshes = dwg.modelspace().query('MESH')
    assert len(meshes) == 1


REGULAR_FACE = Vector.list([(0, 0, 0), (1, 0, 1), (1, 1, 1), (0, 1, 0)])
IRREGULAR_FACE = Vector.list([(0, 0, 0), (1, 0, 1), (1, 1, 0), (0, 1, 0)])


def test_has_none_planar_faces():
    mesh = MeshBuilder()
    mesh.add_face(REGULAR_FACE)
    assert mesh.has_none_planar_faces() is False
    mesh.add_face(IRREGULAR_FACE)
    assert mesh.has_none_planar_faces() is True


def test_scale_mesh():
    mesh = cube(center=False)
    mesh.scale(2, 3, 4)
    bbox = BoundingBox(mesh.vertices)
    assert bbox.extmin.isclose((0, 0, 0))
    assert bbox.extmax.isclose((2, 3, 4))


def test_rotate_x():
    mesh = cube(center=False)
    mesh.rotate_x(radians(90))
    bbox = BoundingBox(mesh.vertices)
    assert bbox.extmin.isclose((0, -1, 0))
    assert bbox.extmax.isclose((1, 0, 1))


@pytest.fixture(scope='module')
def msp():
    doc = ezdxf.new()
    return doc.modelspace()


@pytest.fixture(scope='module')
def cube_polyface(msp):
    p = msp.add_polyface()
    p.append_faces(cube().faces_as_vertices())
    return p


def test_from_empty_polyface(msp):
    empty_polyface = msp.add_polyface()
    b = MeshBuilder.from_polyface(empty_polyface)
    assert len(b.vertices) == 0
    assert len(b.faces) == 0


def test_from_cube_polyface(cube_polyface):
    b = MeshBuilder.from_polyface(cube_polyface)
    assert len(b.vertices) == 24  # unoptimized mesh builder
    assert len(b.faces) == 6


def test_render_polyface(cube_polyface):
    doc = ezdxf.new()
    msp = doc.modelspace()
    t = MeshTransformer.from_polyface(cube_polyface)
    assert len(t.vertices) == 24  # unoptimized mesh builder
    assert len(t.faces) == 6
    t.render_polyface(msp)
    new_polyface = msp[-1]
    assert new_polyface.dxftype() == 'POLYLINE'
    assert new_polyface.is_poly_face_mesh is True
    assert len(new_polyface.vertices) == 8 + 6
    assert new_polyface.vertices[0] is not cube_polyface.vertices[0]


def test_from_polymesh(msp):
    polymesh = msp.add_polymesh(size=(4, 4))
    b = MeshBuilder.from_polyface(polymesh)
    n = polymesh.dxf.n_count
    m = polymesh.dxf.m_count
    nfaces = (n - 1) * (m - 1)
    assert len(b.vertices) == nfaces * 4  # unoptimized mesh builder
    assert len(b.faces) == nfaces


def test_from_polyface_type_error(msp):
    polyline = msp.add_polyline3d([(0, 0, 0), (1, 0, 0)])
    with pytest.raises(TypeError):
        MeshBuilder.from_polyface(polyline)

    line = msp.add_line(start=(0, 0, 0), end=(1, 0, 0))
    with pytest.raises(TypeError):
        MeshBuilder.from_polyface(line)
