#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test drawing
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import unittest

from ezdxf.tags import StringIterator

from ezdxf.drawing import Drawing
from ezdxf.templates import TemplateFinder
from ezdxf import is_dxf_file


DWG12 = Drawing.new('AC1009')


class TestDrawing(unittest.TestCase):
    def test_dxfversion(self):
        dwg = Drawing(StringIterator(TEST_HEADER))
        self.assertEqual('AC1009', dwg.dxfversion)


class TestNewDrawingAC1009(unittest.TestCase):
    def setUp(self):
        self.dwg = DWG12

    def test_get_layer(self):
        layer = self.dwg.layers.get('0')
        self.assertEqual('0', layer.dxf.name)

    def test_error_getting_not_existing_layer(self):
        with self.assertRaises(ValueError):
            layer = self.dwg.layers.get('TEST_NOT_EXISTING_LAYER')

    def test_create_layer(self):
        layer = self.dwg.layers.create('TEST_NEW_LAYER')
        self.assertEqual('TEST_NEW_LAYER', layer.dxf.name)

    def test_error_adding_existing_layer(self):
        with self.assertRaises(ValueError):
            layer = self.dwg.layers.create('0')

    def test_has_layer(self):
        self.assertTrue('0' in self.dwg.layers)

    def test_has_not_layer(self):
        self.assertFalse('TEST_LAYER_NOT_EXISTS' in self.dwg.layers)

    def test_removing_layer(self):
        self.dwg.layers.create('TEST_NEW_LAYER_2')
        self.assertTrue('TEST_NEW_LAYER_2' in self.dwg.layers)
        self.dwg.layers.remove('TEST_NEW_LAYER_2')
        self.assertFalse('TEST_NEW_LAYER_2' in self.dwg.layers)

    def test_error_removing_not_existing_layer(self):
        with self.assertRaises(ValueError):
            self.dwg.layers.remove('TEST_LAYER_NOT_EXISTS')

DWG2000 = Drawing.new('AC1015')


class TestNewDrawingAC1015(TestNewDrawingAC1009):
    def setUp(self):
        self.dwg = DWG2000


class TestIsDXFFile(unittest.TestCase):
    def test_template(self):
        template_file = TemplateFinder().filepath('AC1009')
        self.assertTrue(is_dxf_file(template_file))


TEST_HEADER = """  0
SECTION
  2
HEADER
  9
$ACADVER
  1
AC1009
  9
$DWGCODEPAGE
  3
ANSI_1252
  9
$HANDSEED
  5
FF
  0
ENDSEC
  0
SECTION
  2
ENTITIES
  0
ENDSEC
  0
EOF
"""

TESTCOPY = """  0
SECTION
  2
HEADER
  9
$ACADVER
  1
AC1018
  9
$DWGCODEPAGE
  3
ANSI_1252
  9
$TDUPDATE
 40
0.
  9
$HANDSEED
  5
FF
  0
ENDSEC
  0
SECTION
  2
OBJECTS
  0
ENDSEC
  0
SECTION
  2
FANTASYSECTION
  1
everything should be copied
  0
ENDSEC
  0
SECTION
  2
ALPHASECTION
  1
everything should be copied
  0
ENDSEC
  0
SECTION
  2
OMEGASECTION
  1
everything should be copied
  0
ENDSEC
  0
EOF
"""

if __name__ == '__main__':
    unittest.main()