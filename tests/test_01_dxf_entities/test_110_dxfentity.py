# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created 2019-02-14
import pytest
import ezdxf

from ezdxf.lldxf.const import DXFAttributeError, DXF12, DXFValueError
from ezdxf.lldxf.tagwriter import TagCollector
from ezdxf.entities.dxfentity import DXFEntity
from ezdxf.lldxf.extendedtags import DXFTag
from ezdxf.entities.line import Line

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


def test_is_alive(entity):
    assert entity.is_alive is True
    entity.destroy()
    assert entity.is_alive is False


def test_dont_write_handles_for_R12(entity):
    from ezdxf.lldxf.tagwriter import TagWriter
    from io import StringIO
    s = StringIO()
    t = TagWriter(s)
    t.dxfversion = DXF12
    t.write_handles = False
    entity.export_dxf(t)
    result = s.getvalue()
    assert '5\nFFFF\n' not in result


LINE_DATA = """  0
LINE
  5
0
330
0
100
AcDbEntity
  8
0
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


@pytest.fixture
def line():
    return Line.from_text(LINE_DATA)


def test_str(line):
    assert str(line) == "LINE(#0)"
    assert repr(line) == "<class 'ezdxf.entities.line.Line'> LINE(#0)"


def test_get_dxf_defaul(line):
    # get_dxf_default returns the DXF default value for unset attributes
    assert line.dxf.get_default('thickness') == 0
    # get returns the given default for unset attributes, which is None by default :)
    assert line.dxf.get('thickness') is None


def test_ocs(line):
    ocs = line.ocs()
    assert ocs.uz == (0, 0, 1)
    assert ocs.transform is False


class TestAppData:
    @pytest.fixture
    def entity(self):
        return Line.from_text(LINE_DATA)

    def test_new_app_data(self, entity):
        assert entity.has_app_data('{MOZMAN') is False
        entity.set_app_data('{MOZMAN', tags=[DXFTag(330, 'DEAD')])
        assert entity.has_app_data('{MOZMAN') is True

    def test_get_app_data(self, entity):
        entity.set_app_data('{MOZMAN', tags=[DXFTag(330, 'DEAD')])

        app_data = entity.get_app_data('{MOZMAN')
        assert len(app_data) == 1
        assert DXFTag(330, 'DEAD') == app_data[0]

    def test_set_app_data(self, entity):
        entity.set_app_data('{MOZMAN', tags=[DXFTag(330, 'DEAD')])
        app_data = entity.get_app_data('{MOZMAN')
        assert 1 == len(app_data)
        assert DXFTag(330, 'DEAD') == app_data[0]
        app_data.append(DXFTag(360, 'DEAD2'))
        entity.set_app_data('{MOZMAN', app_data)

        app_data = entity.get_app_data('{MOZMAN')
        assert 2 == len(app_data)
        assert DXFTag(330, 'DEAD') == app_data[0]
        assert DXFTag(360, 'DEAD2') == app_data[1]

    def test_not_existing_appid(self, entity):
        with pytest.raises(DXFValueError):
            entity.get_app_data("XYZ")


class TestXData:
    @pytest.fixture
    def entity(self):
        return Line.from_text(LINE_DATA)

    def test_new_app_data(self, entity):
        assert entity.has_xdata('MOZMAN') is False
        entity.set_xdata('MOZMAN', tags=[DXFTag(1000, 'Extended Data String')])
        assert entity.has_xdata('MOZMAN') is True

    def test_get_xdata(self, entity):
        entity.set_xdata('MOZMAN', tags=[DXFTag(1000, 'Extended Data String')])

        xdata = entity.get_xdata('MOZMAN')
        assert len(xdata) == 1
        assert DXFTag(1000, 'Extended Data String') == xdata[0]

    def test_set_xdata(self, entity):
        entity.set_xdata('MOZMAN', tags=[DXFTag(1000, 'Extended Data String')])
        xdata = entity.get_xdata('MOZMAN')
        assert 1 == len(xdata)
        assert DXFTag(1000, 'Extended Data String') == xdata[0]
        xdata.append(DXFTag(1000, 'Extended Data String2'))
        entity.set_xdata('MOZMAN', xdata)

        xdata = entity.get_xdata('MOZMAN')
        assert 2 == len(xdata)
        assert DXFTag(1000, 'Extended Data String') == xdata[0]
        assert DXFTag(1000, 'Extended Data String2') == xdata[1]

    def test_not_existing_appid(self, entity):
        with pytest.raises(DXFValueError):
            entity.get_xdata("XYZ")

    def test_get_xdata_list_exception(self, entity):
        with pytest.raises(DXFValueError):
            _ = entity.get_xdata_list('ACAD', 'DSTYLE')
        entity.set_xdata('ACAD', tags=[DXFTag(1000, 'Extended Data String')])

        with pytest.raises(DXFValueError):
            _ = entity.get_xdata_list('ACAD', 'DSTYLE')

    def test_has_xdata_list(self, entity):
        assert entity.has_xdata_list('ACAD', 'DSTYLE') is False
        entity.set_xdata('ACAD', tags=[DXFTag(1000, 'Extended Data String')])
        assert entity.has_xdata_list('ACAD', 'DSTYLE') is False

    def test_set_xdata_list(self, entity):
        entity.set_xdata_list('ACAD', 'DSTYLE', [(1070, 1), (1000, 'String')])
        xdata_list = entity.get_xdata_list('ACAD', 'DSTYLE')
        assert len(xdata_list) == 5
        assert xdata_list == [
            (1000, 'DSTYLE'),
            (1002, '{'),
            (1070, 1),
            (1000, 'String'),
            (1002, '}'),
        ]
        # add another list to ACAD
        entity.set_xdata_list('ACAD', 'MOZMAN', [(1070, 2), (1000, 'mozman')])
        xdata = entity.get_xdata_list('ACAD', 'MOZMAN')
        assert len(xdata) == 5
        assert xdata == [
            (1000, 'MOZMAN'),
            (1002, '{'),
            (1070, 2),
            (1000, 'mozman'),
            (1002, '}'),
        ]
        xdata = entity.get_xdata('ACAD')
        assert len(xdata) == 10

    def test_discard_xdata_list(self, entity):
        entity.set_xdata_list('ACAD', 'DSTYLE', [(1070, 1), (1000, 'String')])
        xdata_list = entity.get_xdata_list('ACAD', 'DSTYLE')
        assert len(xdata_list) == 5
        entity.discard_xdata_list('ACAD', 'DSTYLE')
        with pytest.raises(DXFValueError):
            _ = entity.get_xdata_list('ACAD', 'DSTYLE')

        entity.discard_xdata_list('ACAD', 'DSTYLE')

    def test_replace_xdata_list(self, entity):
        entity.set_xdata_list('ACAD', 'DSTYLE', [(1070, 1), (1000, 'String')])
        xdata_list = entity.get_xdata_list('ACAD', 'DSTYLE')
        assert len(xdata_list) == 5
        assert xdata_list == [
            (1000, 'DSTYLE'),
            (1002, '{'),
            (1070, 1),
            (1000, 'String'),
            (1002, '}'),
        ]
        entity.set_xdata_list('ACAD', 'DSTYLE', [(1070, 2), (1000, 'mozman'), (1000, 'data')])
        xdata_list = entity.get_xdata_list('ACAD', 'DSTYLE')
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
        entity.replace_xdata_list('ACAD', 'MOZMAN', [(1070, 3), (1000, 'new')])
        xdata_list = entity.get_xdata_list('ACAD', 'MOZMAN')
        assert len(xdata_list) == 5
        assert xdata_list == [
            (1000, 'MOZMAN'),
            (1002, '{'),
            (1070, 3),
            (1000, 'new'),
            (1002, '}'),
        ]
        xdata = entity.get_xdata('ACAD')
        assert len(xdata) == 6+5


class TestReactors:
    @pytest.fixture
    def entity(self):
        return Line.from_text(LINE_DATA)

    def test_has_no_reactors(self, entity):
        assert entity.has_reactors() is False

    def test_set_reactors(self, entity):
        entity.set_reactors(['A000', 'B000', 'C000'])
        assert entity.has_reactors() is True
        handles = entity.get_reactors()
        assert ['A000', 'B000', 'C000'] == handles

    def test_append_handle(self, entity):
        entity.set_reactors([])
        assert 0 == len(entity.get_reactors())
        entity.append_reactor_handle('A000')
        assert 'A000' in entity.get_reactors()
        entity.append_reactor_handle('B000')
        assert 'B000' in entity.get_reactors()
        assert 2 == len(entity.get_reactors())

        entity.append_reactor_handle('B000')  # same handle again
        assert 'B000' in entity.get_reactors()
        assert 2 == len(entity.get_reactors()), 'handle entries should be unique'

        entity.append_reactor_handle('FF')  # smallest handle, should be first handle in reactors
        assert entity.get_reactors()[0] == 'FF'

        entity.append_reactor_handle('FFFF')  # biggest handle, should be last handle in reactors
        assert 'FFFF' == entity.get_reactors()[-1]

    def test_discard_handle(self, entity):
        entity.set_reactors(['A000', 'B000', 'C000'])
        entity.discard_reactor_handle('A000')
        assert 2 == len(entity.get_reactors()), 'Handle not deleted'
        entity.discard_reactor_handle('FFFF')  # ignore not existing handles
        assert 2 == len(entity.get_reactors())


class TestGetLayout:
    @pytest.fixture(scope='class')
    def doc(self):
        return ezdxf.new()

    def test_get_layout_model_space(self, doc):
        msp = doc.modelspace()
        circle = msp.add_circle(center=(0, 0), radius=1)
        layout = circle.get_layout()
        assert msp.name == layout.name

    def test_get_layout_paper_space(self, doc):
        psp = doc.layout()
        circle = psp.add_circle(center=(0, 0), radius=1)
        layout = circle.get_layout()
        assert psp.name == layout.name

    def test_get_layout_block(self, doc):
        block = doc.blocks.new('TEST')
        circle = block.add_circle(center=(0, 0), radius=1)
        layout = circle.get_layout()
        assert block.name == layout.name

    def test_get_layout_without_layout(self, doc):
        msp = doc.modelspace()
        circle = msp.add_circle(center=(0, 0), radius=1)
        msp.unlink_entity(circle)
        assert circle.get_layout() is None
