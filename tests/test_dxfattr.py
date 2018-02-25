# Purpose: test dxfattr
# Copyright (c) 2011-2018 Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest

from ezdxf.dxfentity import DXFEntity
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.lldxf.attributes import DXFAttr, DefSubclass, DXFAttributes

XTEMPLATE = """  0
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


class AttributeChecker(DXFEntity):
    TEMPLATE = XTEMPLATE
    DXFATTRIBS = DXFAttributes(
        DefSubclass(None, {
            'handle': DXFAttr(5),
            'block_record': DXFAttr(330),
        }),
        DefSubclass('AcDbEntity', {
            'paperspace': DXFAttr(67, default=0),
            'layer': DXFAttr(8, default='0'),
            'linetype': DXFAttr(6, default='BYLAYER'),
            'ltscale': DXFAttr(48, default=1.0),
            'invisible': DXFAttr(60, default=0),
            'color': DXFAttr(62, default=256),
        }),
        DefSubclass('AcDbLine', {
            'start': DXFAttr(10, 'Point2D/3D'),
            'end': DXFAttr(11, 'Point2D/3D'),
            'thickness': DXFAttr(39),
            'extrusion': DXFAttr(210, 'Point3D'),
        }))


class TestDXFAttributes:
    @pytest.fixture
    def dxfattribs(self):
        return AttributeChecker.DXFATTRIBS

    def test_init(self, dxfattribs):
        count = len(list(dxfattribs.subclasses()))
        assert 3 == count


class TestAttributeAccess:
    @pytest.fixture
    def entity(self):
        return AttributeChecker(ExtendedTags.from_text(XTEMPLATE))

    def test_get_from_none_subclass(self, entity):
        assert '0' == entity.dxf.handle

    def test_set_to_none_subclass(self, entity):
        entity.dxf.handle = 'ABCD'
        assert 'ABCD' == entity.dxf.handle

    def test_get_from_AcDbEntity_subclass(self, entity):
        assert '0' == entity.dxf.layer

    def test_set_to_AcDbEntity_subclass(self, entity):
        entity.dxf.layer = 'LAYER'
        assert 'LAYER' == entity.dxf.layer

    def test_set_new_to_AcDbEntity_subclass(self, entity):
        entity.dxf.color = 7
        assert 7 == entity.dxf.color

    def test_get_from_AcDbLine_subclass(self, entity):
        assert (0, 0, 0) == entity.dxf.start

    def test_get_default_values(self, entity):
        assert 256 == entity.get_dxf_default_value('color')
