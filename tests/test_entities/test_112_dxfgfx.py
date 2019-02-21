# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created 2019-02-14
import pytest

from ezdxf.entities.dxfgfx import DXFGraphic


@pytest.fixture
def entity():
    return DXFGraphic.from_text(LINE)


def test_init_from_tags(entity):
    assert entity.dxf.layer == 'Layer'


def test_true_color(entity):
    entity.dxf.true_color = 0x0F0F0F
    assert 0x0F0F0F == entity.dxf.true_color
    assert (0x0F, 0x0F, 0x0F) == entity.rgb  # shortcut for modern graphic entities
    entity.rgb = (255, 255, 255)  # shortcut for modern graphic entities
    assert 0xFFFFFF == entity.dxf.true_color


def test_color_name(entity):
    entity.dxf.color_name = "Rot"
    assert "Rot" == entity.dxf.color_name


def test_transparency(entity):
    entity.dxf.transparency = 0x020000FF  # 0xFF = opaque; 0x00 = 100% transparent
    assert 0x020000FF == entity.dxf.transparency
    # recommend usage: helper property ModernGraphicEntity.transparency
    assert 0. == entity.transparency  # 0. =  opaque; 1. = 100% transparent
    entity.transparency = 1.0
    assert 0x02000000 == entity.dxf.transparency


def test_default_attributes():
    entity = DXFGraphic.new()
    assert entity.dxf.layer == '0'
    assert entity.dxf.hasattr('layer') is True, 'real attribute required'
    assert entity.dxf.color == 256
    assert entity.dxf.hasattr('color') is False, 'just the default value'
    assert entity.dxf.linetype == 'BYLAYER'
    assert entity.dxf.hasattr('linetype') is False, 'just the default value'


LINE = """0
LINE
5
0
330
0
100
AcDbEntity
8
Layer
6
Linetype
62
77
370
25
100
AcDbLine
10
0.0
20
0.0
30
0.0
11
1.0
21
1.0
31
1.0
"""


if __name__ == '__main__':
    pytest.main([__file__])

