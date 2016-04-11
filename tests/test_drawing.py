#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test drawing
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import unittest

from ezdxf.lldxf.tagger import string_tagger
from ezdxf.drawing import Drawing
from ezdxf.templates import TemplateLoader
from ezdxf import is_dxf_file


DWG12 = Drawing.new('AC1009')


class TestDrawing(unittest.TestCase):
    def test_dxfversion(self):
        dwg = Drawing(string_tagger(TEST_HEADER))
        self.assertEqual('AC1009', dwg.dxfversion)


class TestNewDrawingAC1009(unittest.TestCase):
    def setUp(self):
        self.dwg = DWG12

    def test_dxfversion(self):
        self.assertEqual('AC1009', self.dwg.dxfversion)

    def test_acad_release(self):
        self.assertEqual('R12', self.dwg.acad_release)

    def test_get_layer(self):
        layer = self.dwg.layers.get('0')
        self.assertEqual('0', layer.dxf.name)

    def test_error_getting_not_existing_layer(self):
        with self.assertRaises(ValueError):
            layer = self.dwg.layers.get('TEST_NOT_EXISTING_LAYER')

    def test_create_layer(self):
        layer = self.dwg.layers.new('TEST_NEW_LAYER')
        self.assertEqual('TEST_NEW_LAYER', layer.dxf.name)

    def test_error_adding_existing_layer(self):
        with self.assertRaises(ValueError):
            layer = self.dwg.layers.new('0')

    def test_has_layer(self):
        self.assertTrue('0' in self.dwg.layers)

    def test_has_not_layer(self):
        self.assertFalse('TEST_LAYER_NOT_EXISTS' in self.dwg.layers)

    def test_removing_layer(self):
        self.dwg.layers.new('TEST_NEW_LAYER_2')
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

    def test_dxfversion(self):
        self.assertEqual('AC1015', self.dwg.dxfversion)

    def test_acad_release(self):
        self.assertEqual('R2000', self.dwg.acad_release)


class TestIsDXFFile(unittest.TestCase):
    def test_template(self):
        template_file = TemplateLoader().filepath('AC1009')
        self.assertTrue(is_dxf_file(template_file))


class TestMinimalisticDXF12Drawing(unittest.TestCase):
    def setUp(self):
        self.dwg = Drawing(string_tagger(MINIMALISTIC_DXF12))

    def test_header_section(self):
        self.assertTrue(hasattr(self.dwg, 'header'))
        self.assertTrue(self.dwg.header['$ACADVER'], 'AC1009')
        self.assertTrue(self.dwg.header['$DWGCODEPAGE'], 'ANSI_1252')

    def test_layers_table(self):
        self.assertTrue(hasattr(self.dwg, 'layers'))
        self.assertEqual(len(self.dwg.layers), 0)

    def test_styles_table(self):
        self.assertTrue(hasattr(self.dwg, 'styles'))
        self.assertEqual(len(self.dwg.styles), 0)

    def test_linetypes_table(self):
        self.assertTrue(hasattr(self.dwg, 'linetypes'))
        self.assertEqual(len(self.dwg.linetypes), 0)

    def test_blocks_section(self):
        self.assertTrue(hasattr(self.dwg, 'blocks'))
        self.assertEqual(len(self.dwg.blocks), 0)

    def test_entity_section(self):
        self.assertTrue(hasattr(self.dwg, 'entities'))
        self.assertEqual(len(self.dwg.entities), 0)



MINIMALISTIC_DXF12 = """  0
SECTION
  2
ENTITIES
  0
ENDSEC
  0
EOF
"""

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