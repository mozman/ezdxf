#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test generic wrapper
# Created: 22.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import sys
import unittest
from functools import lru_cache

from ezdxf.tags import Tags, DXFStructureError
from ezdxf.entity import GenericWrapper

class PointAccessor(GenericWrapper):
    CODE = {
        'point': (10, 'Point3D'),
        'flat': (11, 'Point2D'),
        'xp': (12, 'Point3D'),
        'flex': (13, 'Point2D/3D'),
    }

class TestPoint3D(unittest.TestCase):
    def test_get_3d_point(self):
        tags = Tags.fromtext("10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        self.assertEqual( (1., 2., 3.), point.point)

    def test_error_get_2d_point_for_required_3d_point(self):
        tags = Tags.fromtext("10\n1.0\n20\n2.0\n")
        point = PointAccessor(tags)
        with self.assertRaises(DXFStructureError):
            point.point

    def test_set_point(self):
        tags = Tags.fromtext("10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        point.point = (7, 8, 9)
        self.assertEqual(3, len(tags))
        self.assertEqual( (7., 8., 9.), point.point)

    def test_error_only_2_axis_exists(self):
        tags = Tags.fromtext("10\n1.0\n20\n2.0\n70\n0\n")
        point = PointAccessor(tags)
        with self.assertRaises(DXFStructureError):
            point.point = (7, 8, 9)

    def test_error_only_1_axis_exists(self):
        tags = Tags.fromtext("10\n1.0\n70\n0\n")
        point = PointAccessor(tags)
        with self.assertRaises(DXFStructureError):
            point.point = (7, 8, 9)

    def test_get_3d_point_shift(self):
        tags = Tags.fromtext("12\n1.0\n22\n2.0\n32\n3.0\n")
        point = PointAccessor(tags)
        self.assertEqual( (1., 2., 3.), point.xp)

    def test_error(self):
        tags = Tags.fromtext("12\n1.0\n22\n2.0\n32\n3.0\n")
        point = PointAccessor(tags)
        with self.assertRaises(ValueError):
            point.point

class TestPoint2D(unittest.TestCase):
    def test_get_2d_point(self):
        point = PointAccessor(Tags.fromtext("11\n1.0\n21\n2.0\n40\n3.0\n"))
        self.assertEqual( (1., 2.), point.flat)

    def test_error_get_2d_point_form_3d_point(self):
        point = PointAccessor(Tags.fromtext("11\n1.0\n21\n2.0\n31\n3.0\n"))
        with self.assertRaises(DXFStructureError):
            point.flat

    def test_set_2d_point(self):
        point = PointAccessor(Tags.fromtext("11\n1.0\n21\n2.0\n40\n3.0\n"))
        point.flat = (4, 5)
        self.assertEqual(3, len(point.tags))
        self.assertEqual( (4., 5.), point.flat)

    def test_error_set_2d_point_at_existing_3d_point(self):
        point = PointAccessor(Tags.fromtext("11\n1.0\n21\n2.0\n31\n3.0\n"))
        with self.assertRaises(DXFStructureError):
            point.flat = (4, 5)

class TestFlexPoint(unittest.TestCase):
    def test_get_2d_point(self):
        tags = Tags.fromtext("13\n1.0\n23\n2.0\n")
        point = PointAccessor(tags)
        self.assertEqual( (1., 2.), point.flex)

    def test_get_3d_point(self):
        tags = Tags.fromtext("13\n1.0\n23\n2.0\n33\n3.0\n")
        point = PointAccessor(tags)
        self.assertEqual( (1., 2., 3.), point.flex)

    def test_error_get_1d_point(self):
        point = PointAccessor(Tags.fromtext("13\n1.0\n"))
        with self.assertRaises(DXFStructureError):
            point.flex

    def test_set_2d_point(self):
        tags = Tags.fromtext("13\n1.0\n23\n2.0\n")
        point = PointAccessor(tags)
        point.flex = (3., 4.)
        self.assertEqual(2, len(tags))
        self.assertEqual( (3., 4.), point.flex)

    def test_set_3d_point(self):
        tags = Tags.fromtext("13\n1.0\n23\n2.0\n40\n0.0\n")
        point = PointAccessor(tags)
        point.flex = (3., 4., 5.)
        self.assertEqual(4, len(tags))
        self.assertEqual( (3., 4., 5.), point.flex)

    def test_set_2d_point_at_existing_3d_point(self):
        tags = Tags.fromtext("13\n1.0\n23\n2.0\n33\n3.0\n")
        point = PointAccessor(tags)
        point.flex = (3., 4.)
        self.assertEqual(2, len(tags))
        self.assertEqual( (3., 4.), point.flex)

    def test_error_set_point_dxf_structure_error(self):
        tags = Tags.fromtext("13\n1.0\n40\n0.0\n")
        point = PointAccessor(tags)
        with self.assertRaises(DXFStructureError):
            point.flex = (3., 4., 5.)

    def test_error_set_point_with_wrong_axis_count(self):
        tags = Tags.fromtext("13\n1.0\n23\n2.0\n40\n0.0\n")
        point = PointAccessor(tags)
        with self.assertRaises(ValueError):
            point.flex = (3., 4., 5., 6.)
        with self.assertRaises(ValueError):
            point.flex = (3., )

if __name__=='__main__':
    unittest.main()