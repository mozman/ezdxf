#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test generic wrapper
# Created: 22.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import sys
import unittest

from ezdxf.tags import Tags
from ezdxf.entity import GenericWrapper

class PointAccessor(GenericWrapper):
    CODE = {
        'point': 10, # test 3d points
        'xp': 12, # test second 3d points
    }
class TestPointAccessor(unittest.TestCase):
    def test_get_3d_point(self):
        tags = Tags.fromtext("10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        self.assertEqual( (1., 2., 3.), point.point)

    def test_get_2d_point(self):
        tags = Tags.fromtext("10\n1.0\n20\n2.0\n")
        point = PointAccessor(tags)
        self.assertEqual( (1., 2.), point.point)

    def test_set_point(self):
        tags = Tags.fromtext("10\n1.0\n20\n2.0\n30\n3.0\n")
        point = PointAccessor(tags)
        point.point = (7, 8)
        self.assertEqual(3, len(tags))
        self.assertEqual( (7., 8., 0.), point.point)

    def test_add_coordinate(self):
        tags = Tags.fromtext("10\n1.0\n20\n2.0\n70\n0\n")
        point = PointAccessor(tags)
        point.point = (7, 8, 9)
        self.assertEqual(4, len(tags))
        self.assertEqual( (30, 9.), tags[2])

    def test_add_two_coordinates(self):
        tags = Tags.fromtext("10\n1.0\n70\n0\n")
        point = PointAccessor(tags)
        point.point = (7, 8, 9)
        self.assertEqual(4, len(tags))
        self.assertEqual( (20, 8.), tags[1])
        self.assertEqual( (30, 9.), tags[2])

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