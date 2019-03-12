# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created 2019-02-15
import pytest

from ezdxf.lldxf.types import DXFTag
from ezdxf.lldxf.const import DXF2000
from ezdxf.entities.dxfobj import XRecord
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text

XRECORD = """  0
XRECORD
5
0
330
0
100
AcDbXrecord
280
1
"""

@pytest.fixture
def entity():
    return XRecord.from_text(XRECORD)


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES
    assert 'XRECORD' in ENTITY_CLASSES


def test_default_init():
    entity = XRecord()
    assert entity.dxftype() == 'XRECORD'
    assert entity.dxf.handle is None
    assert entity.dxf.owner is None


def test_default_new():
    entity = XRecord.new(handle='ABBA', owner='0', dxfattribs={
    })
    assert entity.dxf.cloning == 1
    assert len(entity.tags) == 0


def test_load_from_text(entity):
    assert entity.dxf.cloning == 1
    assert len(entity.tags) == 0


def test_write_dxf():
    entity = XRecord.from_text(XRECORD)
    result = TagCollector.dxftags(entity)
    expected = basic_tags_from_text(XRECORD)
    assert result == expected


@pytest.fixture
def xrecord():
    return XRecord.from_text(XRECORD1)


def test_handle(xrecord):
    assert '43A' == xrecord.dxf.handle


def test_parent_handle(xrecord):
    assert '28C' == xrecord.dxf.owner


def test_cloning_parameter(xrecord):
    assert 1 == xrecord.dxf.cloning


def test_get_data(xrecord):
    assert DXFTag(102, 'SHADEPLOT') == xrecord.tags[0]
    assert DXFTag(70, 0) == xrecord.tags[1]


def test_last_data(xrecord):
    assert DXFTag(70, 0) == xrecord.tags[-1]


def test_iter_data(xrecord):
    tags = list(xrecord.tags)
    assert DXFTag(102, 'SHADEPLOT') == tags[0]
    assert DXFTag(70, 0) == tags[1]


def test_len(xrecord):
    assert 2 == len(xrecord.tags)


def test_set_data(xrecord):
    xrecord.tags[0] = DXFTag(103, 'MOZMAN')
    assert DXFTag(103, 'MOZMAN') == xrecord.tags[0]
    assert DXFTag(70, 0) == xrecord.tags[1]


def test_append_data(xrecord):
    xrecord.tags.append(DXFTag(103, 'MOZMAN'))
    assert DXFTag(103, 'MOZMAN') == xrecord.tags[-1]


XRECORD1 = """  0
XRECORD
  5
43A
102
{ACAD_REACTORS
330
28C
102
}
330
28C
100
AcDbXrecord
280
     1
102
SHADEPLOT
 70
     0
"""

