# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created 2019-02-14
import pytest
import ezdxf

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


def test_clone_graphical_entity(entity):
    doc = ezdxf.new()
    entity.doc = doc
    msp = doc.modelspace()
    msp.add_entity(entity)

    entity.dxf.handle = 'EFEF'
    entity.dxf.owner = 'ABBA'
    entity.dxf.layer = 'Layer1'
    entity.dxf.color = 13
    entity.set_reactors(['A', 'F'])
    entity.set_xdata('MOZMAN', [(1000, 'extended data')])
    clone = entity.copy()
    assert clone.dxf is not entity.dxf, 'should be different objects'
    assert clone.dxf.handle in doc.entitydb, 'should be stored in entity db'
    assert clone.dxf.owner is None
    assert clone.dxf.layer == 'Layer1'
    assert clone.dxf.color == 13
    assert clone.reactors is not entity.reactors, 'should be different objects'
    assert len(clone.get_reactors()) == 0
    assert clone.xdata is not entity.xdata, 'should be different objects'
    assert clone.get_xdata('MOZMAN') == [(1000, 'extended data')]

    clone.dxf.handle = 'CDCD'
    clone.dxf.owner = 'FEFE'
    clone.dxf.layer = 'Layer2'
    clone.dxf.color = 77
    clone.set_reactors([])
    clone.set_xdata('MOZMAN', [(1000, 'extended data1')])

    # don't change source entity
    assert entity.dxf.handle == 'EFEF'
    assert entity.dxf.owner == 'ABBA'
    assert entity.dxf.layer == 'Layer1'
    assert entity.dxf.color == 13
    assert entity.get_reactors() == ['A', 'F']
    assert entity.get_xdata('MOZMAN') == [(1000, 'extended data')]


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



