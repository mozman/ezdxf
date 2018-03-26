# Purpose: test generic wrapper
# Created: 22.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest
import ezdxf
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.dxfentity import DXFEntity, DXFTag
from ezdxf.tools import set_flag_state
from ezdxf import DXFStructureError, DXFAttributeError, DXFValueError

DWG = ezdxf.new('R12')


class PointAccessor(DXFEntity):
    DXFATTRIBS = DXFAttributes(DefSubclass(None, {
        'point': DXFAttr(10, 'Point3D'),
        'flat': DXFAttr(11, 'Point2D'),
        'xp': DXFAttr(12, 'Point3D'),
        'flex': DXFAttr(13, 'Point2D/3D'),
        'flags': DXFAttr(70),
        'just_AC1015': DXFAttr(71, default=777, dxfversion='AC1015'),
    }))

    def __init__(self, tags):
        super(PointAccessor, self).__init__(tags, drawing=DWG)


def test_set_flag_state():
    assert set_flag_state(0, 1, True) == 1
    assert set_flag_state(0b10, 1, True) == 0b11
    assert set_flag_state(0b111, 0b010, False) == 0b101
    assert set_flag_state(0b010, 0b111, True) == 0b111
    assert set_flag_state(0b1111, 0b1001, False) == 0b0110


class TestDXFEntity:
    def test_supports_dxfattrib(self):
        tags = ExtendedTags.from_text("10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        assert point.supports_dxf_attrib('xp') is True

    def test_supports_dxfattrib2(self):
        tags = ExtendedTags.from_text("10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        assert point.supports_dxf_attrib('mozman') is False
        assert point.supports_dxf_attrib('just_AC1015') is False

    def test_getdxfattr_default(self):
        tags = ExtendedTags.from_text("10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        assert  point.get_dxf_attrib('flags', 17) == 17

    def test_getdxfattr_no_DXF_default_value_at_wrong_dxf_version(self):
        tags = ExtendedTags.from_text("10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        # just_AC1015 has a DXF default value, but the drawing has an insufficient DXF version
        with pytest.raises(DXFValueError):
            point.get_dxf_attrib('just_AC1015')
        # except the USER defined default value
            assert point.get_dxf_attrib('just_AC1015', 17) == 17

    def test_getdxfattr_exist(self):
        tags = ExtendedTags.from_text("70\n9\n10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        assert 9 == point.get_dxf_attrib('flags', 17)

    def test_dxfattr_exists(self):
        tags = ExtendedTags.from_text("70\n9\n10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        assert point.dxf_attrib_exists('flags') is True

    def test_dxfattr_doesnt_exist(self):
        tags = ExtendedTags.from_text("70\n9\n10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        assert point.dxf_attrib_exists('xp') is False

    def test_value_error(self):
        tags = ExtendedTags.from_text("10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        with pytest.raises(DXFValueError):
            point.dxf.flags

    def test_attribute_error(self):
        tags = ExtendedTags.from_text("10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        with pytest.raises(DXFAttributeError):
            point.dxf.xflag

    def test_valid_dxf_attrib_names(self):
        tags = ExtendedTags.from_text("10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        # just_AC1015 - is not valid for AC1009
        assert ['flags', 'flat', 'flex', 'point', 'xp'] == sorted(point.valid_dxf_attrib_names())

    def test_set_and_get_dxfattrib(self):
        tags = ExtendedTags.from_text("10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        point.dxf.flags = 7
        assert 7 == point.dxf.flags

    def test_set_dxfattrib_for_wrong_dxfversion_error(self):
        tags = ExtendedTags.from_text("10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        with pytest.raises(DXFAttributeError):
            point.dxf.just_AC1015 = 7

    def test_get_dxfattrib_for_wrong_dxfversion_without_error(self):
        tags = ExtendedTags.from_text("10\n1.0\n20\n2.0\n30\n3.0\n71\n999\n")
        point = PointAccessor(tags)
        assert 999 == point.dxf.just_AC1015, "If false tags are there, don't care"

    def test_delete_simple_dxfattrib(self):
        tags = ExtendedTags.from_text("70\n7\n10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        assert 7 == point.dxf.flags
        del point.dxf.flags
        assert point.dxf_attrib_exists('flags') is False

    def test_delete_xtype_dxfattrib(self):
        tags = ExtendedTags.from_text("70\n7\n10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        assert (1.0, 2.0, 3.0) == point.dxf.point
        del point.dxf.point
        assert point.dxf_attrib_exists('point') is False
        # low level check
        point_tags = [tag for tag in point.tags.noclass if tag.code in (10, 20, 30)]
        assert 0 == len(point_tags)

    def test_delete_not_supported_dxfattrib(self):
        tags = ExtendedTags.from_text("70\n7\n10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        with pytest.raises(DXFAttributeError):
            del point.dxf.mozman

    def test_set_not_existing_3D_point(self):
        tags = ExtendedTags.from_text("70\n7\n10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        assert point.dxf_attrib_exists('xp') is False
        point.dxf.xp = (7, 8, 9)
        assert (7, 8, 9) == point.dxf.xp

    def test_set_not_existing_3D_point_with_wrong_axis_count(self):
        tags = ExtendedTags.from_text("70\n7\n10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        assert point.dxf_attrib_exists('xp') is False
        with pytest.raises(DXFValueError):
            point.dxf.xp = (7, 8)

    def test_set_not_existing_flex_point_as_3D(self):
        tags = ExtendedTags.from_text("70\n7\n10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        assert point.dxf_attrib_exists('flex') is False
        point.dxf.flex = (7, 8, 9)
        assert (7, 8, 9) == point.dxf.flex

    def test_set_not_existing_flex_point_as_2D(self):
        tags = ExtendedTags.from_text("70\n7\n10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        assert point.dxf_attrib_exists('flex') is False
        point.dxf.flex = (7, 8)
        assert (7, 8) == point.dxf.flex

    def test_get_flag_state(self):
        tags = ExtendedTags.from_text("70\n7\n10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        assert point.get_flag_state(1, name='flags') is True
        assert point.get_flag_state(2) is True
        assert point.get_flag_state(4) is True
        assert point.get_flag_state(16) is False

    def test_get_flag_state_non__existing_flags(self):
        tags = ExtendedTags.from_text("10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        # non-existing flags are always 0
        assert point.get_flag_state(1, name='flags') is False
        assert point.get_flag_state(16, name='flags') is False

    def test_set_flag_state(self):
        tags = ExtendedTags.from_text("70\n7\n10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        point.set_flag_state(1, state=False, name='flags')
        assert point.dxf.flags == 6
        point.set_flag_state(1, state=True, name='flags')
        assert point.dxf.flags == 7

    def test_set_flag_state_none_existing_flags(self):
        tags = ExtendedTags.from_text("10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        point.set_flag_state(1, state=True, name='flags')
        assert point.dxf.flags == 1
        with pytest.raises(DXFAttributeError):
            point.set_flag_state(1, state=True, name='plot_flags')


class TestPoint3D:
    def test_get_3d_point(self):
        tags = ExtendedTags.from_text("10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        assert (1., 2., 3.) == point.dxf.point

    def test_error_get_2d_point_for_required_3d_point(self):
        tags = ExtendedTags.from_text("10\n1.0\n20\n2.0\n  0\nVALUE\n")
        point = PointAccessor(tags)
        with pytest.raises(DXFStructureError):
            point.dxf.point

    def test_set_point(self):
        tags = ExtendedTags.from_text("10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        point.dxf.point = (7, 8, 9)
        assert 1 == len(tags.noclass), 'points represented by just one tag since v0.6 (code, (x, y[, z]))'
        assert (7., 8., 9.) == point.dxf.point

    def test_get_3d_point_shift(self):
        tags = ExtendedTags.from_text("12\n1.0\n22\n2.0\n32\n3.0\n")
        point = PointAccessor(tags)
        assert (1., 2., 3.) == point.dxf.xp

    def test_error(self):
        tags = ExtendedTags.from_text("12\n1.0\n22\n2.0\n32\n3.0\n")
        point = PointAccessor(tags)
        with pytest.raises(DXFValueError):
            point.dxf.point


class TestPoint2D:
    def test_get_2d_point(self):
        point = PointAccessor(ExtendedTags.from_text("11\n1.0\n21\n2.0\n40\n3.0\n"))
        assert (1., 2.) == point.dxf.flat

    def test_error_get_2d_point_form_3d_point(self):
        point = PointAccessor(ExtendedTags.from_text("11\n1.0\n21\n2.0\n31\n3.0\n"))
        with pytest.raises(DXFStructureError):
            point.dxf.flat

    def test_set_2d_point(self):
        point = PointAccessor(ExtendedTags.from_text("11\n1.0\n21\n2.0\n40\n3.0\n"))
        point.dxf.flat = (4, 5)
        assert 2 == len(point.tags.noclass), 'points represented by just one tag since v0.6 (code, (x, y[, z]))'
        assert (4., 5.) == point.dxf.flat


class TestFlexPoint:
    def test_get_2d_point(self):
        tags = ExtendedTags.from_text("13\n1.0\n23\n2.0\n")
        point = PointAccessor(tags)
        assert (1., 2.) == point.dxf.flex

    def test_get_3d_point(self):
        tags = ExtendedTags.from_text("13\n1.0\n23\n2.0\n33\n3.0\n")
        point = PointAccessor(tags)
        assert (1., 2., 3.) == point.dxf.flex

    def test_set_2d_point(self):
        tags = ExtendedTags.from_text("13\n1.0\n23\n2.0\n") # points represented by just one tag since v0.6 (code, (x, y[, z]))
        point = PointAccessor(tags)
        point.dxf.flex = (3., 4.)
        assert 1 == len(tags.noclass)
        assert (3., 4.) == point.dxf.flex

    def test_set_3d_point(self):
        tags = ExtendedTags.from_text("13\n1.0\n23\n2.0\n40\n0.0\n")
        point = PointAccessor(tags)
        point.dxf.flex = (3., 4., 5.)
        assert 2 == len(tags.noclass), 'points represented by just one tag since v0.6 (code, (x, y[, z]))'
        assert (3., 4., 5.) == point.dxf.flex

    def test_set_2d_point_at_existing_3d_point(self):
        tags = ExtendedTags.from_text("13\n1.0\n23\n2.0\n33\n3.0\n")
        point = PointAccessor(tags)
        point.dxf.flex = (3., 4.)
        assert 1 == len(tags.noclass), 'points represented by just one tag since v0.6 (code, (x, y[, z]))'
        assert (3., 4.) == point.dxf.flex

    def test_error_set_point_with_wrong_axis_count(self):
        tags = ExtendedTags.from_text("13\n1.0\n23\n2.0\n40\n0.0\n")
        point = PointAccessor(tags)
        with pytest.raises(DXFValueError):
            point.dxf.flex = (3., 4., 5., 6.)
        with pytest.raises(DXFValueError):
            point.dxf.flex = (3., )

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


def test_str():
    from ezdxf.legacy.graphics import Line
    line = Line(ExtendedTags.from_text(LINE_DATA))
    assert str(line) == "LINE(#0)"
    assert repr(line) == "<class 'ezdxf.legacy.graphics.Line'> LINE(#0)"


def test_ocs():
    from ezdxf.legacy.graphics import Line
    line = Line(ExtendedTags.from_text(LINE_DATA))
    ocs = line.ocs()
    assert ocs.uz == (0, 0, 1)
    assert ocs.transform is False


class TestAppData:
    @pytest.fixture
    def entity(self):
        return DXFEntity(ExtendedTags.from_text(LINE_DATA))

    def test_new_app_data(self, entity):
        assert entity.has_app_data('{MOZMAN') is False
        entity.set_app_data('{MOZMAN', app_data_tags=[DXFTag(330, 'DEAD')])
        assert entity.has_app_data('{MOZMAN') is True

    def test_get_app_data(self, entity):
        entity.set_app_data('{MOZMAN', app_data_tags=[DXFTag(330, 'DEAD')])

        app_data = entity.get_app_data('{MOZMAN')
        assert 1 == len(app_data)
        assert DXFTag(330, 'DEAD') == app_data[0]

    def test_set_app_data(self, entity):
        entity.set_app_data('{MOZMAN', app_data_tags=[DXFTag(330, 'DEAD')])
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
        return DXFEntity(ExtendedTags.from_text(LINE_DATA))

    def test_new_app_data(self, entity):
        assert entity.has_xdata('MOZMAN') is False
        entity.set_xdata('MOZMAN', xdata_tags=[DXFTag(1000, 'Extended Data String')])
        assert entity.has_xdata('MOZMAN') is True

    def test_get_xdata(self, entity):
        entity.set_xdata('MOZMAN', xdata_tags=[DXFTag(1000, 'Extended Data String')])

        xdata = entity.get_xdata('MOZMAN')
        assert 1 == len(xdata)
        assert DXFTag(1000, 'Extended Data String') == xdata[0]

    def test_set_xdata(self, entity):
        entity.set_xdata('MOZMAN', xdata_tags=[DXFTag(1000, 'Extended Data String')])
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


class TestReactors:
    @pytest.fixture
    def entity(self):
        return DXFEntity(ExtendedTags.from_text(LINE_DATA))

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
        assert 'FF' == entity.get_reactors()[0]

        entity.append_reactor_handle('FFFF')  # biggest handle, should be last handle in reactors
        assert 'FFFF' == entity.get_reactors()[-1]

    def test_remove_handle(self, entity):
        entity.set_reactors(['A000', 'B000', 'C000'])
        entity.remove_reactor_handle('A000')
        assert 2 == len(entity.get_reactors()), 'Handle not deleted'
        entity.remove_reactor_handle('FFFF')  # ignore not existing handles
        assert 2 == len(entity.get_reactors())


class TestGetLayoutR2000:
    @pytest.fixture(scope='class')
    def dwg(self):
        return ezdxf.new('R2000')

    def test_get_layout_model_space(self, dwg):
        msp = dwg.modelspace()
        circle = msp.add_circle(center=(0, 0), radius=1)
        layout = circle.get_layout()
        assert msp.name == layout.name

    def test_get_layout_paper_space(self, dwg):
        psp = dwg.layout()
        circle = psp.add_circle(center=(0, 0), radius=1)
        layout = circle.get_layout()
        assert psp.name == layout.name

    def test_get_layout_block(self, dwg):
        block = dwg.blocks.new('TEST')
        circle = block.add_circle(center=(0, 0), radius=1)
        layout = circle.get_layout()
        assert block.name == layout.name

    def test_get_layout_without_layout(self, dwg):
        msp = dwg.modelspace()
        circle = msp.add_circle(center=(0, 0), radius=1)
        msp.unlink_entity(circle)
        assert circle.get_layout() is None


class TestExtensionDict:
    @pytest.fixture(scope='class')
    def dwg(self):
        return ezdxf.new('R2000')

    def test_new_extension_dict(self, dwg):
        msp = dwg.modelspace()
        entity = msp.add_line((0, 0), (10, 0))
        with pytest.raises(DXFValueError):
            entity.get_extension_dict()

        xdict = entity.new_extension_dict()
        assert xdict.dxftype() == 'DICTIONARY'
        assert xdict.dxf.owner == entity.dxf.handle
        assert entity.has_app_data('{ACAD_XDICTIONARY')
        assert entity.has_extension_dict() is True

        xdict2 = entity.get_extension_dict()
        assert xdict.dxf.handle == xdict2.dxf.handle


class TestGetLayoutR12:
    @pytest.fixture(scope='class')
    def dwg(self):
        return ezdxf.new('R12')

    def test_get_layout_model_space(self, dwg):
        msp = dwg.modelspace()
        circle = msp.add_circle(center=(0, 0), radius=1)
        layout = circle.get_layout()
        assert layout._paperspace == 0

    def test_get_layout_paper_space(self, dwg):
        psp = dwg.layout()
        circle = psp.add_circle(center=(0, 0), radius=1)
        layout = circle.get_layout()
        assert layout._paperspace == 1

    def test_get_layout_block(self, dwg):
        block = dwg.blocks.new('TEST')
        circle = block.add_circle(center=(0, 0), radius=1)
        layout = circle.get_layout()
        assert block.name == layout.name

    def test_get_layout_without_layout(self, dwg):
        msp = dwg.modelspace()
        circle = msp.add_circle(center=(0, 0), radius=1)
        msp.unlink_entity(circle)
        assert circle.get_layout() is None

