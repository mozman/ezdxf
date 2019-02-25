# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-13
import pytest
import copy
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.entities.appdata import AppData


class TagWriter:
    """ Mockup """

    def __init__(self):
        self.tags = []

    def write_tags(self, tags):
        self.tags.append(tags)


@pytest.fixture
def tags():
    return ExtendedTags.from_text(APPDATA)


def test_app_data_get(tags):
    appdata = AppData()
    appdata.set(tags.appdata[0])
    mozman = appdata.get('MOZMAN')
    assert mozman[0] == (102, "{MOZMAN")
    assert mozman[-1] == (102, "}")


def test_app_data_add():
    appdata = AppData()
    appdata.add('XXX', [
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


def test_app_data_add_data():
    appdata = AppData()
    appdata.add('XXX', [
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
    appdata.set(tags.appdata[0])
    assert 'MOZMAN' in appdata
    appdata.discard('MOZMAN')
    assert 'MOZMAN' not in appdata
    # nothing happens if appid does not exist
    appdata.discard('MOZMAN')


def test_app_data_dxf_export(tags):
    appdata = AppData()
    appdata.set(tags.appdata[0])
    appdata.add('XXX', [
        (40, 3),
        (70, 19),
        (1, "Text"),
    ])
    assert len(appdata) == 2
    tagwriter = TagWriter()
    appdata.export_dxf(tagwriter)

    assert len(tagwriter.tags) == 2
    tags1, tags2 = tagwriter.tags
    assert tags1[0] == (102, '{MOZMAN')
    assert tags1[-1] == (102, '}')
    assert tags2[0] == (102, '{XXX')
    assert tags2[-1] == (102, '}')


def test_clone(tags):
    appdata = AppData()
    appdata.set(tags.appdata[0])
    new_appdata = copy.deepcopy(appdata)
    new_appdata.add('MOZMAN', [
        (1, "Text"),
    ])
    d1 = appdata.get('MOZMAN')
    d2 = new_appdata.get('MOZMAN')
    assert len(d1) == 4
    assert len(d2) == 3
    assert d1[1] == (40, 1.)
    assert d2[1] == (1, "Text")


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
