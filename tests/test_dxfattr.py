#!/usr/bin/env python
#coding:utf-8
# Author:  mozman --<mozman@gmx.at>
# Purpose: test dxfattr
# Created: 2011-04-28
from __future__ import unicode_literals

import unittest

from ezdxf.entity import GenericWrapper
from ezdxf.classifiedtags import ClassifiedTags
from ezdxf.dxfattr import DXFAttr, DefSubclass, DXFAttributes

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


class AttributeChecker(GenericWrapper):
    TEMPLATE = XTEMPLATE
    DXFATTRIBS = DXFAttributes(
        DefSubclass(None, {
            'handle': DXFAttr(5, None),
            'block_record': DXFAttr(330, None),
        }),
        DefSubclass('AcDbEntity', {
            'paperspace': DXFAttr(67, None),
            'layer': DXFAttr(8, None),
            'linetype': DXFAttr(6, None),
            'ltscale': DXFAttr(48, None),
            'invisible': DXFAttr(60, None),
            'color': DXFAttr(62, None),
        }),
        DefSubclass('AcDbLine', {
            'start': DXFAttr(10, 'Point2D/3D'),
            'end': DXFAttr(11, 'Point2D/3D'),
            'thickness': DXFAttr(39, None),
            'extrusion': DXFAttr(210, 'Point3D'),
        }))


class TestDXFAttributes(unittest.TestCase):
    def setUp(self):
        self.dxfattribs = AttributeChecker.DXFATTRIBS

    def test_init(self):
        count = len(list(self.dxfattribs.subclasses()))
        self.assertEqual(3, count)


class TestAttributeAccess(unittest.TestCase):
    def setUp(self):
        self.entity = AttributeChecker(ClassifiedTags.from_text(XTEMPLATE))

    def test_get_from_none_subclass(self):
        self.assertEqual('0', self.entity.dxf.handle)

    def test_set_to_none_subclass(self):
        self.entity.dxf.handle = 'ABCD'
        self.assertEqual('ABCD', self.entity.dxf.handle)

    def test_get_from_AcDbEntity_subclass(self):
        self.assertEqual('0', self.entity.dxf.layer)

    def test_set_to_AcDbEntity_subclass(self):
        self.entity.dxf.layer = 'LAYER'
        self.assertEqual('LAYER', self.entity.dxf.layer)

    def test_get_new_from_AcDbEntity_subclass(self):
        self.assertEqual(7, self.entity.dxf.get('color', 7))

    def test_set_new_to_AcDbEntity_subclass(self):
        self.entity.dxf.color = 7
        self.assertEqual(7, self.entity.dxf.color)

    def test_get_from_AcDbLine_subclass(self):
        self.assertEqual((0, 0, 0), self.entity.dxf.start)


if __name__ == '__main__':
    unittest.main()