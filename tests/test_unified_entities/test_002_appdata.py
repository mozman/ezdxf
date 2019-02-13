# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-13
import pytest

from ezdxf.lldxf.const import DXFKeyError
from ezdxf.entities.dxfentity import AppData, ExtendedTags


class TagWriterMock:
    def __init__(self):
        self.tags = []

    def write_tags(self, tags):
        self.tags.append(tags)


@pytest.fixture
def tags():
    return ExtendedTags.from_text(APPDATA)


def test_app_data_get(tags):
    appdata = AppData()
    appdata.add(tags.appdata[0])
    mozman = appdata.get('MOZMAN')
    assert mozman[0] == (102, "{MOZMAN")
    assert mozman[-1] == (102, "}")


def test_app_data_add():
    appdata = AppData()
    appdata.add([
        (102, "{XXX"),
        (40, 3),
        (70, 19),
        (1, "Text"),
        (102, "}"),
    ])
    assert 'XXX' in appdata
    data = appdata.get('XXX')
    assert len(data) == 5
    # is DXFTag()
    assert data[0].code == 102
    assert data[0].value == '{XXX'
    assert data[-1].code == 102
    assert data[-1].value == '}'


def test_app_data_new():
    appdata = AppData()
    appdata.new('XXX', [
        (40, 3),
        (70, 19),
        (1, "Text"),
    ])
    assert 'XXX' in appdata
    data = appdata.get('XXX')
    assert len(data) == 5
    # is DXFTag()
    assert data[0].code == 102
    assert data[0].value == '{XXX'
    assert data[-1].code == 102
    assert data[-1].value == '}'


def test_app_data_delete(tags):
    appdata = AppData()
    appdata.add(tags.appdata[0])
    assert 'MOZMAN' in appdata
    appdata.delete('MOZMAN')
    assert 'MOZMAN' not in appdata
    with pytest.raises(DXFKeyError):
        appdata.delete('MOZMAN')


def test_app_data_dxf_export(tags):
    appdata = AppData()
    appdata.add(tags.appdata[0])
    appdata.new('XXX', [
        (40, 3),
        (70, 19),
        (1, "Text"),
    ])
    assert len(appdata) == 2
    tagwriter = TagWriterMock()
    appdata.export_dxf(tagwriter)

    assert len(tagwriter.tags) == 2
    tags1, tags2 = tagwriter.tags
    assert tags1[0] == (102, '{MOZMAN')
    assert tags1[-1] == (102, '}')
    assert tags2[0] == (102, '{XXX')
    assert tags2[-1] == (102, '}')


APPDATA = """0
DXFENTITY
5
FFFF
102
{MOZMAN
40
1.0
70
9
102
}
"""

if __name__ == '__main__':
    pytest.main([__file__])
