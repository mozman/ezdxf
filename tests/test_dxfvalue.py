#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test dxfvalue
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import sys
import unittest

from ezdxf.dxfvalue import DXFValue

class TestDXFValue(unittest.TestCase):
    def test_single_value_code(self):
        var = DXFValue( (0, 'SECTION') )
        self.assertEqual(0, var.code)

    def test_single_value_value(self):
        var = DXFValue( (0, 'SECTION') )
        self.assertEqual('SECTION', var.value)

    def test_single_value_str(self):
        var = DXFValue( (0, 'SECTION') )
        self.assertEqual('  0\nSECTION\n', str(var))

    def test_not_ispoint(self):
        var = DXFValue( (0, 'SECTION') )
        self.assertFalse(var.ispoint)

    def test_ispoint(self):
        var = DXFValue( ((10, 1), (20, 1)) )
        self.assertTrue(var.ispoint)

    def test_getpoint_2coords(self):
        var = DXFValue( ((10, 1), (20, 1)) )
        self.assertEqual((1, 1), var.getpoint())

    def test_getpoint_3coords(self):
        var = DXFValue( ((10, 1), (20, 2), (30, 3)) )
        self.assertEqual((1, 2, 3), var.getpoint())

    def test_point_str(self):
        var = DXFValue( ((10, 1), (20, 2), (30, 3)) )
        self.assertEqual(" 10\n1\n 20\n2\n 30\n3\n", str(var))

if __name__=='__main__':
    unittest.main()