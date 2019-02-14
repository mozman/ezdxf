# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-13
import pytest

from ezdxf.lldxf.const import DXFValueError, DXFKeyError
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.entities.xdata import XData
from ezdxf.clone import clone


class TagWriter:
    """ Mockup """
    def __init__(self):
        self.tags = []

    def write_tags(self, tags):
        self.tags.append(tags)


@pytest.fixture
def xdata():
    xtags = ExtendedTags.from_text("""0
DXFENTITY
1001
MOZMAN
1000
DataStr1
1000
DataStr2
1040
3.14
1001
ACAD
1000
AutoDesk
1000
Revit""")
    return XData(xtags.xdata)


def test_empty_xdata():
    xdata = XData()
    assert len(xdata) == 0
    tagwriter = TagWriter()
    xdata.export_dxf(tagwriter)
    assert len(tagwriter.tags) == 0


def test_add_data(xdata):
    assert 'XXX' not in xdata
    xdata.add('XXX', [(1000, 'Extended Data String')])
    assert 'XXX' in xdata


def test_get_data(xdata):
    assert 'MOZMAN' in xdata
    tags = xdata.get('MOZMAN')
    assert len(tags) == 4
    assert tags[0] == (1001, 'MOZMAN')
    assert tags[1] == (1000, 'DataStr1')
    assert tags[2] == (1000, 'DataStr2')
    assert tags[3] == (1040, 3.14)

    with pytest.raises(DXFKeyError):
        _ = xdata.get('XXX')


def test_replace_xdata(xdata):
    assert len(xdata) == 2
    xdata.add('MOZMAN', [(1000, 'XXX')])
    assert len(xdata) == 2, "replace existing XDATA"

    tags = xdata.get('MOZMAN')
    assert tags[0] == (1001, 'MOZMAN')
    assert tags[1] == (1000, 'XXX')


def test_discard_xdata(xdata):
    assert len(xdata) == 2
    xdata.discard('MOZMAN')
    assert len(xdata) == 1
    assert 'MOZMAN' not in xdata
    # ignore none existing appids
    xdata.discard('xxx')
    assert len(xdata) == 1


def test_cloning(xdata):
    xdata2 = clone(xdata)
    assert len(xdata2) == 2

    assert 'MOZMAN' in xdata2
    tags = xdata2.get('MOZMAN')
    assert len(tags) == 4
    assert tags[0] == (1001, 'MOZMAN')
    assert tags[1] == (1000, 'DataStr1')
    assert tags[2] == (1000, 'DataStr2')
    assert tags[3] == (1040, 3.14)
    xdata2.discard('MOZMAN')
    assert 'MOZMAN' in xdata
    assert 'MOZMAN' not in xdata2


def test_dxf_export(xdata):
    tagwriter = TagWriter()
    xdata.export_dxf(tagwriter)
    result = tagwriter.tags
    assert len(result) == 2
    # sorted appids!
    assert result[0][0] == (1001, 'ACAD')
    assert result[1][0] == (1001, 'MOZMAN')


def test_has_xdata_list(xdata):
    assert xdata.has_xlist('ACAD', 'DSTYLE') is False


def test_get_xlist_exception(xdata):
    with pytest.raises(DXFValueError):
        _ = xdata.get_xlist('ACAD', 'DSTYLE')


def test_set_xdata_list(xdata):
    xdata.set_xlist('ACAD', 'DSTYLE', [(1070, 1), (1000, 'String')])
    data = xdata.get_xlist('ACAD', 'DSTYLE')
    assert len(data) == 5
    assert data == [
        (1000, 'DSTYLE'),
        (1002, '{'),
        (1070, 1),
        (1000, 'String'),
        (1002, '}'),
    ]
    # add another list to ACAD
    xdata.set_xlist('ACAD', 'MOZMAN', [(1070, 2), (1000, 'mozman')])
    data = xdata.get_xlist('ACAD', 'MOZMAN')
    assert len(data) == 5
    assert data == [
        (1000, 'MOZMAN'),
        (1002, '{'),
        (1070, 2),
        (1000, 'mozman'),
        (1002, '}'),
    ]
    data = xdata.get('ACAD')
    assert len(data) == 10+3


def test_discard_xdata_list(xdata):
    xdata.set_xlist('ACAD', 'DSTYLE', [(1070, 1), (1000, 'String')])
    xdata_list = xdata.get_xlist('ACAD', 'DSTYLE')
    assert len(xdata_list) == 5
    xdata.discard_xlist('ACAD', 'DSTYLE')
    with pytest.raises(DXFValueError):
        _ = xdata.get_xlist('ACAD', 'DSTYLE')

    xdata.discard_xlist('ACAD', 'DSTYLE')


def test_replace_xdata_list(xdata):
    xdata.set_xlist('ACAD', 'DSTYLE', [(1070, 1), (1000, 'String')])
    xdata_list = xdata.get_xlist('ACAD', 'DSTYLE')
    assert len(xdata_list) == 5
    assert xdata_list == [
        (1000, 'DSTYLE'),
        (1002, '{'),
        (1070, 1),
        (1000, 'String'),
        (1002, '}'),
    ]
    xdata.set_xlist('ACAD', 'DSTYLE', [(1070, 2), (1000, 'mozman'), (1000, 'data')])
    xdata_list = xdata.get_xlist('ACAD', 'DSTYLE')
    assert len(xdata_list) == 6
    assert xdata_list == [
        (1000, 'DSTYLE'),
        (1002, '{'),
        (1070, 2),
        (1000, 'mozman'),
        (1000, 'data'),
        (1002, '}'),
    ]
    # replace not existing list -> append list
    xdata.replace_xlist('ACAD', 'MOZMAN', [(1070, 3), (1000, 'new')])
    xdata_list = xdata.get_xlist('ACAD', 'MOZMAN')
    assert len(xdata_list) == 5
    assert xdata_list == [
        (1000, 'MOZMAN'),
        (1002, '{'),
        (1070, 3),
        (1000, 'new'),
        (1002, '}'),
    ]
    data = xdata.get('ACAD')
    assert len(data) == 6 + 5 + 3


if __name__ == '__main__':
    pytest.main([__file__])
