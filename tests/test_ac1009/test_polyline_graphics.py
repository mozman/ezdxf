#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test basic graphic entities
# Created: 25.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import sys
import unittest

from tests.tools import DrawingProxy
from ezdxf.entityspace import EntitySpace

from ezdxf.ac1009.layouts import AC1009Layout

class TestPolyline(unittest.TestCase):
    def setUp(self):
        self.dwg = DrawingProxy('AC1009')
        self.entityspace = EntitySpace(self.dwg.entitydb)
        self.layout = AC1009Layout(self.entityspace, self.dwg.dxffactory, 0)

    def test_create_polyline2D(self):
        polyline = self.layout.add_polyline2D( [(0, 0), (1, 1)] )
        self.assertEqual((0., 0.), polyline[0].location)
        self.assertEqual((1., 1.), polyline[1].location)
        self.assertEqual('polyline2d', polyline.getmode())

    def test_create_polyline3D(self):
        polyline = self.layout.add_polyline3D( [(1, 2, 3), (4, 5, 6)] )
        self.assertEqual((1., 2., 3.), polyline[0].location)
        self.assertEqual((4., 5., 6.), polyline[1].location)
        self.assertEqual('polyline3d', polyline.getmode())


if __name__=='__main__':
    unittest.main()