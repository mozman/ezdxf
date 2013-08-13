#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test tools
# Created: 27.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import unittest

import ezdxf

from ezdxf.testtools import DrawingProxy

def getattributes(obj):
    return ( attr for attr in dir(obj) if not attr.startswith('_DrawingProxy__') )


class TestDrawingProxy(unittest.TestCase):
    def test_drawing(self):
        dwg = ezdxf.new('AC1024')
        for attr in getattributes(DrawingProxy('AC1024')):
            if not hasattr(dwg, attr):
                raise Exception("attribute '%s' of DrawingProxy() does not exist in Drawing() class" % attr)

from ezdxf.tools import safe_3D_point

class TestSafe3DPoint(unittest.TestCase):
    def test_3D_point(self):
        self.assertEqual((1, 2, 3), safe_3D_point((1, 2, 3)))

    def test_2D_point(self):
        self.assertEqual((1, 2, 0), safe_3D_point((1, 2)))

    def test_1D_point(self):
        with self.assertRaises(ValueError):
            safe_3D_point((1, ))

    def test_with_int(self):
        with self.assertRaises(TypeError):
            safe_3D_point(1)

    def test_with_float(self):
        with self.assertRaises(TypeError):
            safe_3D_point(1.1)

    def test_with_str(self):
        with self.assertRaises(TypeError):
            safe_3D_point("abc")


if __name__ == '__main__':
    unittest.main()