#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test basic graphic entities
# Created: 25.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import sys
import unittest

import ezdxf

class TestLine(unittest.TestCase):
    def setUp(self):
        self.dwg = ezdxf.new('AC1015')
        self.entityspace = self.dwg.modelspace()

    def test_create_line(self):
        line = self.entityspace.add_line((0, 0), (1, 1))
        self.assertEqual((0.,0.), line.dxf.start)
        self.assertEqual((1.,1.), line.dxf.end)

if __name__=='__main__':
    unittest.main()