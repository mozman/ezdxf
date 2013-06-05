#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test dxf dictionary
# Created: 22.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import unittest

from ezdxf.testtools import ClassifiedTags
from ezdxf.dxfobjects import DXFDictionary


class TestNoneEmptyDXFDict(unittest.TestCase):
    def setUp(self):
        self.dxfdict = DXFDictionary(ClassifiedTags.from_text(ROOTDICT))

    def test_getitem(self):
        self.assertEqual(self.dxfdict['ACAD_PLOTSTYLENAME'], 'E')

    def test_len(self):
        self.assertEqual(14, len(self.dxfdict))

    def test_getitem_with_keyerror(self):
        with self.assertRaises(KeyError):
            self.dxfdict['MOZMAN']

    def test_parent(self):
        self.assertEqual(self.dxfdict.dxf.parent, '0')

    def test_handle(self):
        self.assertEqual(self.dxfdict.dxf.handle, 'C')

    def test_get(self):
        self.assertEqual(self.dxfdict.get('ACAD_MOZMAN', 'XXX'), 'XXX')

    def test_get_with_keyerror(self):
        with self.assertRaises(KeyError):
            self.dxfdict.get('ACAD_MOZMAN')

    def test_contains(self):
        self.assertTrue('ACAD_PLOTSTYLENAME' in self.dxfdict)

    def test_not_contains(self):
        self.assertFalse('MOZMAN' in self.dxfdict)

class TestEmptyDXFDict(unittest.TestCase):
    def setUp(self):
        self.dxfdict = DXFDictionary(ClassifiedTags.from_text(EMPTY_DICT))

    def test_len(self):
        self.assertEqual(0, len(self.dxfdict))

    def test_add_first_item(self):
        self.dxfdict['TEST'] = "HANDLE"
        self.assertEqual(1, len(self.dxfdict))
        self.assertEqual("HANDLE", self.dxfdict['TEST'])

    def test_add_first_item_2(self):
        self.dxfdict.add(key='TEST', value="HANDLE")
        self.assertEqual(1, len(self.dxfdict))
        self.assertEqual("HANDLE", self.dxfdict['TEST'])

    def test_add_and_replace_first_item(self):
        self.dxfdict['TEST'] = "HANDLE"
        self.assertEqual(1, len(self.dxfdict))
        self.assertEqual("HANDLE", self.dxfdict['TEST'])
        self.dxfdict['TEST'] = "HANDLE2"
        self.assertEqual(1, len(self.dxfdict))
        self.assertEqual("HANDLE2", self.dxfdict['TEST'])


ROOTDICT = """  0
DICTIONARY
  5
C
330
0
100
AcDbDictionary
281
     1
  3
ACAD_COLOR
350
73
  3
ACAD_GROUP
350
D
  3
ACAD_LAYOUT
350
1A
  3
ACAD_MATERIAL
350
72
  3
ACAD_MLEADERSTYLE
350
D7
  3
ACAD_MLINESTYLE
350
17
  3
ACAD_PLOTSETTINGS
350
19
  3
ACAD_PLOTSTYLENAME
350
E
  3
ACAD_SCALELIST
350
B6
  3
ACAD_TABLESTYLE
350
86
  3
ACAD_VISUALSTYLE
350
99
  3
ACDB_RECOMPOSE_DATA
350
40F
  3
AcDbVariableDictionary
350
66
  3
DWGPROPS
350
410
"""

EMPTY_DICT = """  0
DICTIONARY
  5
C
330
0
100
AcDbDictionary
281
     1
"""

if __name__ == '__main__':
    unittest.main()