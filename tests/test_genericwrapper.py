#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test generic wrapper
# Created: 22.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import sys
import unittest

from ezdxf.tags import Tags, DXFStructureError
from ezdxf.entity import GenericWrapper

class PointAccessor(GenericWrapper):
    CODE = {
        'point': (10, 'Point3D'),
        'xp': (12, 'Point3D'),
    }
class TestPointAccessor(unittest.TestCase):
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


if __name__=='__main__':
    unittest.main()