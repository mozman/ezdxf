# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created 2019-02-14
import pytest

from ezdxf.lldxf.const import DXFAttributeError, DXF12
from ezdxf.lldxf.tagwriter import TagCollector
from ezdxf.entities.dxfentity import DXFEntity

ENTITY = """0
DXFENTITY
5
FFFF
330
ABBA
"""


@pytest.fixture
def entity():
    return DXFEntity.from_text(ENTITY)


def test_default_constructor():
    entity = DXFEntity()
    assert entity.dxftype() == 'DXFENTITY'
    assert entity.dxf.handle is None
    assert entity.dxf.owner is None
    assert entity.priority == 0
    assert entity == entity
    assert entity != DXFEntity()


def test_init_with_tags(entity):
    assert entity.dxftype() == 'DXFENTITY'
    assert entity.dxf.handle == 'FFFF'
    assert entity.dxf.owner == 'ABBA'
    assert str(entity) == 'DXFENTITY(#FFFF)'
    assert repr(entity) == "<class 'ezdxf.entities.dxfentity.DXFEntity'> DXFENTITY(#FFFF)"


def test_invalid_dxf_attrib(entity):
    with pytest.raises(DXFAttributeError):
        _ = entity.dxf.color


def test_get_all_dxf_attribs(entity):
    dxfattribs = entity.dxfattribs()
    assert len(dxfattribs) == 2
    assert dxfattribs['handle'] == 'FFFF'
    assert dxfattribs['owner'] == 'ABBA'


def test_write_r12_dxf(entity):
    tagwriter = TagCollector(dxfversion=DXF12)
    entity.export_dxf(tagwriter)
    tag = tagwriter.tags
    assert len(tag) == 2
    assert tag[0] == (0, 'DXFENTITY')
    assert tag[1] == (5, 'FFFF')


def test_write_latest_dxf(entity):
    tagwriter = TagCollector()
    entity.export_dxf(tagwriter)
    tag = tagwriter.tags
    assert len(tag) == 3
    assert tag[0] == (0, 'DXFENTITY')
    assert tag[1] == (5, 'FFFF')
    assert tag[2] == (330, 'ABBA')


def test_destroy(entity):
    entity.destroy()
    assert entity.is_destroyed is True

