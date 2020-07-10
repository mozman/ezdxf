# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
# created 2019-02-15
import pytest
import ezdxf

from ezdxf.entities.polyline import vertex_attribs, DXFVertex
from ezdxf.math import Vector


def test_vertext_attribs_xy():
    result = vertex_attribs((1, 2), format='xy')
    assert result == {'location': Vector(1, 2)}


def test_vertext_attribs_xyb():
    result = vertex_attribs((1, 2, .5), format='xyb')
    assert result == {'location': Vector(1, 2), 'bulge': 0.5}


def test_vertext_attribs_xyseb():
    result = vertex_attribs((1, 2, 3, 4, .5), format='xyseb')
    assert result == {'location': Vector(1, 2), 'bulge': 0.5, 'start_width': 3, 'end_width': 4}


def test_vertext_attribs_vseb():
    result = vertex_attribs(((1, 2), 3, 4, .5), format='vseb')
    assert result == {'location': Vector(1, 2), 'bulge': 0.5, 'start_width': 3, 'end_width': 4}


def test_append_formatted_vertices():
    doc = ezdxf.new('R2000')
    msp = doc.modelspace()
    p = msp.add_polyline2d([(1, 2, .5), (3, 4, .7)], format='xyb')
    assert len(p) == 2
    v1 = p.vertices[0]
    assert v1.dxf.location == (1, 2)
    assert v1.dxf.bulge == 0.5
    v2 = p.vertices[1]
    assert v2.dxf.location == (3, 4)
    assert v2.dxf.bulge == 0.7


def test_vertex_format():
    v = DXFVertex.new(dxfattribs={'location': (1, 2, 3), 'bulge': 5, 'end_width': 7, 'start_width': 6})
    assert v.format('xyz') == (1, 2, 3)
    assert v.format('xyb') == (1, 2, 5)
    assert v.format('vb') == ((1, 2, 3), 5)
    assert v.format('se') == (6, 7)


if __name__ == '__main__':
    pytest.main([__file__])
