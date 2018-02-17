# Created: 17.02.2018
# Copyright (C) 2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <me@mozman.at>"
import pytest
from ezdxf.addons import MeshVertexMerger


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



