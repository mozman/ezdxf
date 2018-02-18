# Created: 17.02.2018
# Copyright (C) 2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <me@mozman.at>"
import pytest
import ezdxf
from ezdxf.addons import MeshVertexMerger, SierpinskyPyramid


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
