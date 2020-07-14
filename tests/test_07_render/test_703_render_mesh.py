# Copyright (c) 2018-2020, Manfred Moitzi
# License: MIT License
import pytest
from math import radians
import ezdxf
from ezdxf.math import Vector, BoundingBox
from ezdxf.render.forms import cube
from ezdxf.render.mesh import MeshVertexMerger, MeshBuilder, MeshTransformer, MeshAverageVertexMerger
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


def test_average_vertex_merger_indices():
    merger = MeshAverageVertexMerger()
    indices = merger.add_vertices([(1, 2, 3), (4, 5, 6)])
    indices2 = merger.add_vertices([(1, 2, 3), (4, 5, 6)])
    assert indices == indices2


def test_average_vertex_merger_vertices():
    merger = MeshAverageVertexMerger()
    merger.add_vertices([(1, 2, 3), (4, 5, 6)])
    merger.add_vertices([(1, 2, 3), (4, 5, 6)])
    assert merger.vertices == [(1, 2, 3), (4, 5, 6)]


def test_average_vertex_merger_index_of():
    merger = MeshAverageVertexMerger()
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
    pyramid = SierpinskyPyramid(level=4, sides=3)
    faces = pyramid.faces()
    mesh = MeshVertexMerger()
    for vertices in pyramid:
        mesh.add_mesh(vertices=vertices, faces=faces)
    assert len(mesh.vertices) == 514
    assert len(mesh.faces) == 1024


def test_average_vertex_merger():
    pyramid = SierpinskyPyramid(level=4, sides=3)
    faces = pyramid.faces()
    mesh = MeshAverageVertexMerger()
    for vertices in pyramid:
        mesh.add_mesh(vertices=vertices, faces=faces)
    assert len(mesh.vertices) == 514
    assert len(mesh.faces) == 1024


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


@pytest.fixture
def polyface_181_1(msp):
    e = msp.new_entity(
        'POLYLINE',
        dxfattribs={
            'flags': 48,
            'm_count': 2,
            'n_count': 6,
        },
    )
    e.append_vertex((25041.94191089287, 29272.95055566061, 0.0), dxfattribs={'flags': 64})
    e.append_vertex((25020.29127589287, 29285.45055566061, 0.0), dxfattribs={'flags': 64})
    e.append_vertex((25020.29127589287, 29310.45055566061, 0.0), dxfattribs={'flags': 64})
    e.append_vertex((25041.94191089287, 29322.95055566061, 0.0), dxfattribs={'flags': 64})
    e.append_vertex((25063.59254589287, 29310.45055566061, 0.0), dxfattribs={'flags': 64})
    e.append_vertex((25063.59254589287, 29285.45055566061, 0.0), dxfattribs={'flags': 64})
    e.append_vertex((25041.94191089287, 29272.95055566061, 50.0), dxfattribs={'flags': 64})
    e.append_vertex((25020.29127589287, 29285.45055566061, 50.0), dxfattribs={'flags': 64})
    e.append_vertex((25020.29127589287, 29310.45055566061, 50.0), dxfattribs={'flags': 64})
    e.append_vertex((25041.94191089287, 29322.95055566061, 50.0), dxfattribs={'flags': 64})
    e.append_vertex((25063.59254589287, 29310.45055566061, 50.0), dxfattribs={'flags': 64})
    e.append_vertex((25063.59254589287, 29285.45055566061, 50.0), dxfattribs={'flags': 64})
    return e


def test_from_polyface_182_1(polyface_181_1):
    mesh = MeshVertexMerger.from_polyface(polyface_181_1)
    assert len(mesh.vertices) == 12


@pytest.fixture
def polyface_181_2(msp):
    e = msp.new_entity(
        'POLYLINE',
        dxfattribs={
            'flags': 16,
            'm_count': 6,
            'n_count': 3,
        },
    )
    e.append_vertex((16606.65151901649, 81.88147523282441, 2099.9999999999995), dxfattribs={'flags': 64})
    e.append_vertex((16606.65151901649, 81.88147523282441, 1199.9999999999998), dxfattribs={'flags': 64})
    e.append_vertex((16606.65151901649, 81.88147523282441, 1199.9999999999998), dxfattribs={'flags': 64})
    e.append_vertex((16606.65151901649, 1281.8814752328244, 2099.9999999999995), dxfattribs={'flags': 64})
    e.append_vertex((16606.65151901649, 1281.8814752328244, 1199.9999999999998), dxfattribs={'flags': 64})
    e.append_vertex((16606.65151901649, 1281.8814752328244, 1199.9999999999998), dxfattribs={'flags': 64})
    e.append_vertex((16626.65151901649, 1281.8814752328244, 2099.9999999999995), dxfattribs={'flags': 64})
    e.append_vertex((16626.65151901649, 1281.8814752328244, 1199.9999999999998), dxfattribs={'flags': 64})
    e.append_vertex((16606.65151901649, 1281.8814752328244, 1199.9999999999998), dxfattribs={'flags': 64})
    e.append_vertex((16626.65151901649, 81.88147523282441, 2099.9999999999995), dxfattribs={'flags': 64})
    e.append_vertex((16626.65151901649, 81.88147523282441, 1199.9999999999998), dxfattribs={'flags': 64})
    e.append_vertex((16606.65151901649, 81.88147523282441, 1199.9999999999998), dxfattribs={'flags': 64})
    e.append_vertex((16626.65151901649, 81.88147523282441, 2099.9999999999995), dxfattribs={'flags': 64})
    e.append_vertex((16626.65151901649, 81.88147523282441, 2099.9999999999995), dxfattribs={'flags': 64})
    e.append_vertex((16606.65151901649, 81.88147523282441, 2099.9999999999995), dxfattribs={'flags': 64})
    e.append_vertex((16626.65151901649, 1281.8814752328244, 2099.9999999999995), dxfattribs={'flags': 64})
    e.append_vertex((16626.65151901649, 1281.8814752328244, 2099.9999999999995), dxfattribs={'flags': 64})
    e.append_vertex((16606.65151901649, 1281.8814752328244, 2099.9999999999995), dxfattribs={'flags': 64})
    return e


def test_from_polyface_182_2(polyface_181_2):
    mesh = MeshVertexMerger.from_polyface(polyface_181_2)
    assert len(mesh.vertices) == 8
