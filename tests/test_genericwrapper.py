#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test generic wrapper
# Created: 22.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3
from __future__ import unicode_literals

import unittest

from ezdxf.testtools import ClassifiedTags, DXFStructureError, DXFAttr, DXFAttributes, DefSubclass
from ezdxf.entity import GenericWrapper

class PointAccessor(GenericWrapper):
    DXFATTRIBS = DXFAttributes(DefSubclass(None, {
        'point': DXFAttr(10, 'Point3D'),
        'flat': DXFAttr(11, 'Point2D'),
        'xp': DXFAttr(12, 'Point3D'),
        'flex': DXFAttr(13, 'Point2D/3D'),
        'flags': DXFAttr(70, None),
    }))

class TestGenericWrapper(unittest.TestCase):
    def test_getdxfattr_default(self):
        tags = ClassifiedTags.fromtext("10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        self.assertEqual(17, point.get_dxf_attrib('flags', 17))

    def test_getdxfattr_exist(self):
        tags = ClassifiedTags.fromtext("70\n9\n10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        self.assertEqual(9, point.get_dxf_attrib('flags', 17))

    def test_value_error(self):
        tags = ClassifiedTags.fromtext("10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        with self.assertRaises(ValueError):
            point.dxf.flags

    def test_attribute_error(self):
        tags = ClassifiedTags.fromtext("10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        with self.assertRaises(AttributeError):
            point.dxf.xflag

class TestPoint3D(unittest.TestCase):
    def test_get_3d_point(self):
        tags = ClassifiedTags.fromtext("10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        self.assertEqual( (1., 2., 3.), point.dxf.point)

    def test_error_get_2d_point_for_required_3d_point(self):
        tags = ClassifiedTags.fromtext("10\n1.0\n20\n2.0\n")
        point = PointAccessor(tags)
        with self.assertRaises(DXFStructureError):
            point.dxf.point

    def test_set_point(self):
        tags = ClassifiedTags.fromtext("10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        point.dxf.point = (7, 8, 9)
        self.assertEqual(3, len(tags.noclass))
        self.assertEqual( (7., 8., 9.), point.dxf.point)

    def test_error_only_2_axis_exists(self):
        tags = ClassifiedTags.fromtext("10\n1.0\n20\n2.0\n70\n0\n")
        point = PointAccessor(tags)
        with self.assertRaises(DXFStructureError):
            point.dxf.point = (7, 8, 9)

    def test_error_only_1_axis_exists(self):
        tags = ClassifiedTags.fromtext("10\n1.0\n70\n0\n")
        point = PointAccessor(tags)
        with self.assertRaises(DXFStructureError):
            point.dxf.point = (7, 8, 9)

    def test_get_3d_point_shift(self):
        tags = ClassifiedTags.fromtext("12\n1.0\n22\n2.0\n32\n3.0\n")
        point = PointAccessor(tags)
        self.assertEqual( (1., 2., 3.), point.dxf.xp)

    def test_error(self):
        tags = ClassifiedTags.fromtext("12\n1.0\n22\n2.0\n32\n3.0\n")
        point = PointAccessor(tags)
        with self.assertRaises(ValueError):
            point.dxf.point

class TestPoint2D(unittest.TestCase):
    def test_get_2d_point(self):
        point = PointAccessor(ClassifiedTags.fromtext("11\n1.0\n21\n2.0\n40\n3.0\n"))
        self.assertEqual( (1., 2.), point.dxf.flat)

    def test_error_get_2d_point_form_3d_point(self):
        point = PointAccessor(ClassifiedTags.fromtext("11\n1.0\n21\n2.0\n31\n3.0\n"))
        with self.assertRaises(DXFStructureError):
            point.dxf.flat

    def test_set_2d_point(self):
        point = PointAccessor(ClassifiedTags.fromtext("11\n1.0\n21\n2.0\n40\n3.0\n"))
        point.dxf.flat = (4, 5)
        self.assertEqual(3, len(point.tags.noclass))
        self.assertEqual( (4., 5.), point.dxf.flat)

    def test_error_set_2d_point_at_existing_3d_point(self):
        point = PointAccessor(ClassifiedTags.fromtext("11\n1.0\n21\n2.0\n31\n3.0\n"))
        with self.assertRaises(DXFStructureError):
            point.dxf.flat = (4, 5)

class TestFlexPoint(unittest.TestCase):
    def test_get_2d_point(self):
        tags = ClassifiedTags.fromtext("13\n1.0\n23\n2.0\n")
        point = PointAccessor(tags)
        self.assertEqual( (1., 2.), point.dxf.flex)

    def test_get_3d_point(self):
        tags = ClassifiedTags.fromtext("13\n1.0\n23\n2.0\n33\n3.0\n")
        point = PointAccessor(tags)
        self.assertEqual( (1., 2., 3.), point.dxf.flex)

    def test_error_get_1d_point(self):
        point = PointAccessor(ClassifiedTags.fromtext("13\n1.0\n"))
        with self.assertRaises(DXFStructureError):
            point.dxf.flex

    def test_set_2d_point(self):
        tags = ClassifiedTags.fromtext("13\n1.0\n23\n2.0\n")
        point = PointAccessor(tags)
        point.dxf.flex = (3., 4.)
        self.assertEqual(2, len(tags.noclass))
        self.assertEqual( (3., 4.), point.dxf.flex)

    def test_set_3d_point(self):
        tags = ClassifiedTags.fromtext("13\n1.0\n23\n2.0\n40\n0.0\n")
        point = PointAccessor(tags)
        point.dxf.flex = (3., 4., 5.)
        self.assertEqual(4, len(tags.noclass))
        self.assertEqual( (3., 4., 5.), point.dxf.flex)

    def test_set_2d_point_at_existing_3d_point(self):
        tags = ClassifiedTags.fromtext("13\n1.0\n23\n2.0\n33\n3.0\n")
        point = PointAccessor(tags)
        point.dxf.flex = (3., 4.)
        self.assertEqual(2, len(tags.noclass))
        self.assertEqual( (3., 4.), point.dxf.flex)

    def test_error_set_point_dxf_structure_error(self):
        tags = ClassifiedTags.fromtext("13\n1.0\n40\n0.0\n")
        point = PointAccessor(tags)
        with self.assertRaises(DXFStructureError):
            point.dxf.flex = (3., 4., 5.)

    def test_error_set_point_with_wrong_axis_count(self):
        tags = ClassifiedTags.fromtext("13\n1.0\n23\n2.0\n40\n0.0\n")
        point = PointAccessor(tags)
        with self.assertRaises(ValueError):
            point.dxf.flex = (3., 4., 5., 6.)
        with self.assertRaises(ValueError):
            point.dxf.flex = (3., )

if __name__=='__main__':
    unittest.main()