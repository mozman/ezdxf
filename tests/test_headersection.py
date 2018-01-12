#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test header section
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import unittest

from ezdxf.tools.test import DrawingProxy, Tags
from ezdxf.sections.header import HeaderSection
from ezdxf import DXFKeyError, DXFValueError, DXFStructureError
from ezdxf.lldxf.validator import header_validator


INVALID_HEADER_STRUCTURE = """   9
$ACADVER
  1
AC1009
  100
$INSBASE
 10
0.0
 20
0.0
 30
0.0
"""

INVALID_HEADER_VAR_NAME = """   9
$ACADVER
  1
AC1009
  9
INSBASE
 10
0.0
 20
0.0
 30
0.0
"""


class TestHeaderValidator(unittest.TestCase):
    def test_valid_header(self):
        tags = Tags.from_text(TESTHEADER)
        result = list(header_validator(tags[2:-1]))
        self.assertEqual(8, len(result))

    def test_invalid_header_tructure(self):
        tags = Tags.from_text(INVALID_HEADER_STRUCTURE)
        with self. assertRaises(DXFStructureError):
            list(header_validator(tags))

    def test_invalid_header_var_name(self):
        tags = Tags.from_text(INVALID_HEADER_VAR_NAME)
        with self. assertRaises(DXFValueError):
            list(header_validator(tags))


class TestHeaderSection(unittest.TestCase):
    def setUp(self):
        tags = Tags.from_text(TESTHEADER)
        dwg = DrawingProxy('AC1009')
        self.header = HeaderSection(tags)
        self.header.set_headervar_factory(dwg.dxffactory.headervar_factory)

    def test_get_acadver(self):
        result = self.header['$ACADVER']
        self.assertEqual('AC1009', result)

    def test_get_insbase(self):
        result = self.header['$INSBASE']
        self.assertEqual((0., 0., 0.), result)

    def test_getitem_keyerror(self):
        with self.assertRaises(DXFKeyError):
            var = self.header['$TEST']

    def test_get(self):
        result = self.header.get('$TEST', 'TEST')
        self.assertEqual('TEST', result)

    def test_set_existing_var(self):
        self.header['$ACADVER'] = 'AC666'
        self.assertEqual('AC666', self.header['$ACADVER'])

    def test_set_existing_point(self):
        self.header['$INSBASE'] = (1, 2, 3)
        self.assertEqual((1, 2, 3), self.header['$INSBASE'])

    def test_set_unknown_var(self):
        with self.assertRaises(DXFKeyError):
            self.header['$TEST'] = 'test'

    def test_create_var(self):
        self.header['$LIMMAX'] = (10, 20)
        self.assertEqual((10, 20), self.header['$LIMMAX'])

    def test_create_var_wrong_args_2d(self):
        self.header['$LIMMAX'] = (10, 20, 30)
        self.assertEqual((10, 20), self.header['$LIMMAX'])

    def test_create_var_wrong_args_3d(self):
        with self.assertRaises(DXFValueError):
            self.header['$PUCSORG'] = (10, 20)

    def test_contains(self):
        self.assertTrue('$ACADVER' in self.header)

    def test_not_contains(self):
        self.assertFalse('$MOZMAN' in self.header)

    def test_remove_headervar(self):
        del self.header['$ACADVER']
        self.assertTrue('$ACADVER' not in self.header)

    def test_str_point(self):
        insbase_str = str(self.header.hdrvars['$INSBASE'])
        self.assertEqual(INSBASE, insbase_str)


class TestCustomProperties(unittest.TestCase):
    def setUp(self):
        tags = Tags.from_text(TESTCUSTOMPROPERTIES)
        dwg = DrawingProxy('AC1009')
        self.header = HeaderSection(tags)
        self.header.set_headervar_factory(dwg.dxffactory.headervar_factory)

    def test_custom_properties_exists(self):
        self.assertTrue(self.header.custom_vars.has_tag("Custom Property 1"))

    def test_order_of_occurrence(self):
        properties = self.header.custom_vars.properties
        self.assertEqual(("Custom Property 1", "Custom Value 1"), properties[0])
        self.assertEqual(("Custom Property 2", "Custom Value 2"), properties[1])

    def test_get_custom_property(self):
        self.assertEqual("Custom Value 1", self.header.custom_vars.get("Custom Property 1"))

    def test_get_custom_property_2(self):
        self.assertEqual("Custom Value 2", self.header.custom_vars.get("Custom Property 2"))

    def test_add_custom_property(self):
        self.header.custom_vars.append("Custom Property 3", "Custom Value 3")
        self.assertEqual(3, len(self.header.custom_vars))
        self.assertEqual("Custom Value 3", self.header.custom_vars.get("Custom Property 3"))

    def test_remove_custom_property(self):
        self.header.custom_vars.remove("Custom Property 1")
        self.assertEqual(1, len(self.header.custom_vars))

    def test_remove_not_existing_property(self):
        with self.assertRaises(ValueError):
            self.header.custom_vars.remove("Does not Exist")

    def test_replace_custom_property(self):
        self.header.custom_vars.replace("Custom Property 1", "new value")
        self.assertEqual("new value", self.header.custom_vars.get("Custom Property 1"))

    def test_replace_not_existing_property(self):
        with self.assertRaises(ValueError):
            self.header.custom_vars.replace("Does not Exist", "new value")


INSBASE = """ 10
0.0
 20
0.0
 30
0.0
"""

TESTHEADER = """  0
SECTION
  2
HEADER
  9
$ACADVER
  1
AC1009
  9
$INSBASE
 10
0.0
 20
0.0
 30
0.0
  9
$EXTMIN
 10
1.0000000000000000E+020
 20
1.0000000000000000E+020
 30
1.0000000000000000E+020
  9
$EXTMAX
 10
-1.0000000000000000E+020
 20
-1.0000000000000000E+020
 30
-1.0000000000000000E+020
  0
ENDSEC
"""

TESTCUSTOMPROPERTIES = """  0
SECTION
  2
HEADER
  9
$ACADVER
  1
AC1009
  9
$CUSTOMPROPERTYTAG
  1
Custom Property 1
  9
$CUSTOMPROPERTY
  1
Custom Value 1
  9
$CUSTOMPROPERTYTAG
  1
Custom Property 2
  9
$CUSTOMPROPERTY
  1
Custom Value 2
  0
ENDSEC
"""

if __name__ == '__main__':
    unittest.main()