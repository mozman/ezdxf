# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
from typing import cast
import pytest
import ezdxf
from ezdxf.entities.idbuffer import IDBuffer
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text

IDBUFFER = """0
IDBUFFER
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
AcDbIdBuffer
"""


@pytest.fixture
def entity():
    return IDBuffer.from_text(IDBUFFER)


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES
    assert 'IDBUFFER' in ENTITY_CLASSES


def test_default_init():
    entity = IDBuffer()
    assert entity.dxftype() == 'IDBUFFER'
    assert entity.dxf.handle is None
    assert entity.dxf.owner is None


def test_default_new():
    entity = IDBuffer.new(handle='ABBA', owner='0', dxfattribs={
    })
    assert len(entity.handles) == 0


def test_load_from_text(entity):
    assert len(entity.handles) == 0


def test_write_dxf():
    entity = IDBuffer.from_text(IDBUFFER)
    result = TagCollector.dxftags(entity)
    expected = basic_tags_from_text(IDBUFFER)
    assert result == expected


@pytest.fixture(scope='module')
def doc():
    return ezdxf.new2('R2007')


def test_generic_id_buffer(doc):
    id_buffer = doc.objects.new_entity('IDBUFFER', {})
    assert id_buffer.dxftype() == 'IDBUFFER'
    assert len(id_buffer.handles) == 0


def test_set_get_id_buffer(doc):
    id_buffer = doc.objects.new_entity('IDBUFFER', {})
    assert id_buffer.dxftype() == 'IDBUFFER'
    id_buffer.handles = ['FF', 'EE', 'DD']
    handles = id_buffer.handles
    assert len(handles) == 3
    assert handles == ['FF', 'EE', 'DD']

    handles.append('FFFF')
    assert handles[-1] == 'FFFF'

    handles.clear()
    assert len(handles) == 0


def test_dxf_tags(doc):
    id_buffer = cast(IDBuffer, doc.objects.new_entity('IDBUFFER', {}))
    id_buffer.handles = ['FF', 'EE', 'DD', 'CC']
    tags = TagCollector.dxftags(id_buffer)[-4:]

    assert len(tags) == 4
    assert tags[0] == (330, 'FF')
    assert tags[-1] == (330, 'CC')


def test_clone(doc):
    id_buffer = cast(IDBuffer, doc.objects.new_entity('IDBUFFER', {}))
    id_buffer.handles = ['FF', 'EE', 'DD', 'CC']
    buffer2 = cast(IDBuffer, id_buffer.copy())
    buffer2.handles[-1] = 'ABCD'
    assert id_buffer.handles[:-1] == buffer2.handles[:-1]
    assert id_buffer.handles[-1] != buffer2.handles[-1]
