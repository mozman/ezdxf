# Copyright (c) 2018-2020, Manfred Moitzi
# License: MIT License
import pytest
from math import radians
import ezdxf
from ezdxf.math import Vector, BoundingBox
from ezdxf.render.forms import cube
from ezdxf.render.mesh import MeshVertexMerger, MeshBuilder
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
