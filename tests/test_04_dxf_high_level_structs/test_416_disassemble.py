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
    p = disassemble.Primitive(factory.new('WIPEOUT'))
    assert p.is_path is False
    assert p.is_mesh is False
    assert list(p.vertices()) == []


def test_point_to_primitive():
    e = factory.new('POINT', dxfattribs={'location': (1, 2, 3)})
    p = disassemble.Primitive(e)
    assert p.is_path is True
    assert p.is_mesh is False
    assert list(p.vertices()) == [(1, 2, 3)]


def test_line_to_primitive():
    start = Vec3(1, 2, 3)
    end = Vec3(4, 5, 6)
    e = factory.new('LINE', dxfattribs={'start': start, 'end': end})
    p = disassemble.Primitive(e)
    assert p.is_path is True
    assert p.is_mesh is False
    assert list(p.vertices()) == [start, end]


if __name__ == '__main__':
    pytest.main([__file__])
