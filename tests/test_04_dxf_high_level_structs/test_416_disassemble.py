#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.math import Vec3
from ezdxf import disassemble
from ezdxf.entities import factory


def test_do_nothing():
    assert list(disassemble.recursive_decompose([])) == []
    assert list(disassemble.to_primitives([])) == []
    assert list(disassemble.to_vertices([])) == []


def test_convert_unsupported_entity_to_primitive():
    p = disassemble.make_primitive(factory.new('WIPEOUT'))
    assert p.path is None
    assert p.mesh is None
    assert list(p.vertices()) == []


def test_point_to_primitive():
    e = factory.new('POINT', dxfattribs={'location': (1, 2, 3)})
    p = disassemble.make_primitive(e)
    assert p.path is not None
    assert p.mesh is None
    assert list(p.vertices()) == [(1, 2, 3)]


def test_line_to_primitive():
    start = Vec3(1, 2, 3)
    end = Vec3(4, 5, 6)
    e = factory.new('LINE', dxfattribs={'start': start, 'end': end})
    p = disassemble.make_primitive(e)
    assert p.path is not None
    assert p.mesh is None
    assert list(p.vertices()) == [start, end]


def test_lwpolyline_to_primitive():
    p1 = Vec3(1, 1)
    p2 = Vec3(2, 2)
    p3 = Vec3(2, 2)
    e = factory.new('LWPOLYLINE')
    e.append_points([p1, p2, p3], format="xy")
    p = disassemble.make_primitive(e)
    assert p.path is not None
    assert p.mesh is None
    assert list(p.vertices()) == [p1, p2, p3]


def test_circle_to_primitive():
    e = factory.new('CIRCLE', dxfattribs={'radius': 5})
    p = disassemble.make_primitive(e)
    assert p.path is not None
    assert p.mesh is None
    assert len(list(p.vertices())) > 32


if __name__ == '__main__':
    pytest.main([__file__])
