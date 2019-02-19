# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created 2019-02-15
import pytest

from ezdxf.entities.dxfclass import DXFClass
from ezdxf.lldxf.const import DXF12, DXF2000, DXF2004
from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.tagwriter import TagCollector

HELIXCLS = """  0
CLASS
1
HELIX
2
AcDbHelix
3
ObjectDBX Classes
90
4095
91
0
280
0
281
1
"""


@pytest.fixture
def entity():
    return DXFClass.from_text(HELIXCLS)


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES
    assert 'CLASS' in ENTITY_CLASSES


def test_default_init():
    dxfclass = DXFClass()
    assert dxfclass.dxftype() == 'CLASS'
    assert dxfclass.dxf.handle is None
    assert dxfclass.dxf.owner is None


def test_default_new():
    entity = DXFClass.new(dxfattribs={
        'name': 'HELIX',
        'cpp_class_name': 'AcDbHelix',
        'flags': 4095,
        'app_name': 'ObjectDBX Classes',
        'is_an_entity': 1,
    })
    assert entity.dxf.name == 'HELIX'
    assert entity.dxf.cpp_class_name == 'AcDbHelix'
    assert entity.dxf.app_name == 'ObjectDBX Classes'
    assert entity.dxf.flags == 4095
    assert entity.dxf.instance_count == 0
    assert entity.dxf.was_a_proxy == 0
    assert entity.dxf.is_an_entity == 1


def test_load_from_text(entity):
    assert entity.dxf.name == 'HELIX'
    assert entity.dxf.cpp_class_name == 'AcDbHelix'
    assert entity.dxf.app_name == 'ObjectDBX Classes'
    assert entity.dxf.flags == 4095
    assert entity.dxf.instance_count == 0
    assert entity.dxf.was_a_proxy == 0
    assert entity.dxf.is_an_entity == 1


def test_write_dxf_2000(entity):
    expected = Tags.from_text(HELIXCLS)
    expected.remove_tags((91, ))
    collector = TagCollector(dxfversion=DXF2000)
    entity.export_dxf(collector)
    assert collector.tags == expected


def test_write_dxf_2004(entity):
    expected = Tags.from_text(HELIXCLS)
    collector = TagCollector(dxfversion=DXF2004)
    entity.export_dxf(collector)
    assert collector.tags == expected


def test_write_dxf_r12(entity):
    collector = TagCollector(dxfversion=DXF12)
    entity.export_dxf(collector)
    assert len(collector.tags) == 0
