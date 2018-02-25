# Copyright (C) 2013- 2018, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals
import pytest
from ezdxf.lldxf.extendedtags import ExtendedTags, DXFTag
from ezdxf.modern.dxfobjects import XRecord


@pytest.fixture
def xrecord():
    return XRecord(ExtendedTags.from_text(XRECORD1))


def test_handle(xrecord):
    assert '43A' == xrecord.dxf.handle


def test_parent_handle(xrecord):
    assert '28C' == xrecord.dxf.owner


def test_cloning_parameter(xrecord):
    assert 1 == xrecord.dxf.cloning


def test_get_data(xrecord):
    assert DXFTag(102, 'SHADEPLOT') == xrecord[0]
    assert DXFTag(70, 0) == xrecord[1]


def test_last_data(xrecord):
    assert DXFTag(70, 0) == xrecord[-1]


def test_iter_data(xrecord):
    tags = list(xrecord)
    assert DXFTag(102, 'SHADEPLOT') == tags[0]
    assert DXFTag(70, 0) == tags[1]


def test_len(xrecord):
    assert 2 == len(xrecord)


def test_set_data(xrecord):
    xrecord[0] = DXFTag(103, 'MOZMAN')
    assert DXFTag(103, 'MOZMAN') == xrecord[0]
    assert DXFTag(70, 0) == xrecord[1]


def test_append_data(xrecord):
    xrecord.append(DXFTag(103, 'MOZMAN'))
    assert DXFTag(103, 'MOZMAN') == xrecord[-1]


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

