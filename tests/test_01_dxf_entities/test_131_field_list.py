# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
from typing import cast
import pytest
import ezdxf
from ezdxf.entities.idbuffer import FieldList
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text

FIELDLIST = """0
FIELDLIST
5
0
102
{ACAD_REACTORS
330
0
102
}
330
0
100
AcDbIdSet
90
12
100
AcDbFieldList
"""


@pytest.fixture
def entity():
    return FieldList.from_text(FIELDLIST)


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES
    assert 'FIELDLIST' in ENTITY_CLASSES


def test_default_init():
    entity = FieldList()
    assert entity.dxftype() == 'FIELDLIST'
    assert entity.dxf.handle is None
    assert entity.dxf.owner is None


def test_default_new():
    entity = FieldList.new(handle='ABBA', owner='0', dxfattribs={
    })
    assert entity.dxf.flags == 0
    assert len(entity.handles) == 0


def test_load_from_text(entity):
    assert entity.dxf.flags == 12
    assert len(entity.handles) == 0


def test_write_dxf():
    entity = FieldList.from_text(FIELDLIST)
    result = TagCollector.dxftags(entity)
    expected = basic_tags_from_text(FIELDLIST)
    assert result == expected


@pytest.fixture(scope='module')
def doc():
    return ezdxf.new2('R2007')


def test_generic_field_list(doc):
    field_list = doc.objects.new_entity('FIELDLIST', {})
    assert field_list.dxftype() == 'FIELDLIST'
    assert len(field_list.handles) == 0


def test_set_get_field_list(doc):
    field_list = doc.objects.new_entity('FIELDLIST', {})
    assert field_list.dxftype() == 'FIELDLIST'
    field_list.handles = ['FF', 'EE', 'DD']
    handles = field_list.handles
    assert len(handles) == 3
    assert handles == ['FF', 'EE', 'DD']

    handles.append('FFFF')
    assert handles[-1] == 'FFFF'


def test_dxf_tags(doc):
    buffer = cast(FieldList, doc.objects.new_entity('FIELDLIST', {}))
    buffer.handles = ['FF', 'EE', 'DD', 'CC']
    tags = TagCollector.dxftags(buffer)[-4:]

    assert len(tags) == 4
    assert tags[0] == (330, 'FF')
    assert tags[-1] == (330, 'CC')


def test_clone(doc):
    buffer = cast(FieldList, doc.objects.new_entity('FIELDLIST', {}))
    buffer.handles = ['FF', 'EE', 'DD', 'CC']
    buffer2 = cast(FieldList, buffer.copy())
    buffer2.handles[-1] = 'ABCD'
    assert buffer.handles[:-1] == buffer2.handles[:-1]
    assert buffer.handles[-1] != buffer2.handles[-1]
