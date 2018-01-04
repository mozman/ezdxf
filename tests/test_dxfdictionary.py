#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test dxf dictionary
# Created: 22.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import unittest

import ezdxf
from ezdxf.tools.test import ExtendedTags
from ezdxf.modern.dxfobjects import DXFDictionary, DXFDictionaryWithDefault


class TestNoneEmptyDXFDict(unittest.TestCase):
    def setUp(self):
        self.dxfdict = DXFDictionary(ExtendedTags.from_text(ROOTDICT))

    def test_getitem(self):
        self.assertEqual(self.dxfdict['ACAD_PLOTSTYLENAME'], 'E')

    def test_len(self):
        self.assertEqual(14, len(self.dxfdict))

    def test_getitem_with_keyerror(self):
        with self.assertRaises(ezdxf.DXFKeyError):
            self.dxfdict['MOZMAN']

    def test_owner(self):
        self.assertEqual(self.dxfdict.dxf.owner, '0')

    def test_handle(self):
        self.assertEqual(self.dxfdict.dxf.handle, 'C')

    def test_get(self):
        self.assertEqual(self.dxfdict.get('ACAD_MOZMAN', 'XXX'), 'XXX')

    def test_get_entity(self):
        # returns just the handle, because no associated drawing exists
        self.assertEqual('E', self.dxfdict.get_entity('ACAD_PLOTSTYLENAME'))

    def test_get_with_keyerror(self):
        with self.assertRaises(ezdxf.DXFKeyError):
            self.dxfdict.get('ACAD_MOZMAN')

    def test_contains(self):
        self.assertTrue('ACAD_PLOTSTYLENAME' in self.dxfdict)

    def test_not_contains(self):
        self.assertFalse('MOZMAN' in self.dxfdict)

    def test_delete_existing_key(self):
        del self.dxfdict['ACAD_PLOTSTYLENAME']
        self.assertFalse('ACAD_PLOTSTYLENAME' in self.dxfdict)
        self.assertEqual(13, len(self.dxfdict))

    def test_delete_not_existing_key(self):
        with self.assertRaises(ezdxf.DXFKeyError):
            del self.dxfdict['MOZMAN']

    def test_remove_existing_key(self):
        self.dxfdict.remove('ACAD_PLOTSTYLENAME')
        self.assertFalse('ACAD_PLOTSTYLENAME' in self.dxfdict)
        self.assertEqual(13, len(self.dxfdict))

    def test_remove_not_existing_key(self):
        with self.assertRaises(ezdxf.DXFKeyError):
            self.dxfdict.remove('MOZMAN')

    def test_discard_existing_key(self):
        self.dxfdict.discard('ACAD_PLOTSTYLENAME')
        self.assertFalse('ACAD_PLOTSTYLENAME' in self.dxfdict)
        self.assertEqual(13, len(self.dxfdict))

    def test_discard_not_existing_key(self):
        self.dxfdict.discard('MOZMAN')
        self.assertEqual(14, len(self.dxfdict))

    def test_clear(self):
        self.assertEqual(14, len(self.dxfdict))
        self.dxfdict.clear()
        self.assertEqual(0, len(self.dxfdict))


class TestEmptyDXFDict(unittest.TestCase):
    def setUp(self):
        self.dxfdict = DXFDictionary(ExtendedTags.from_text(EMPTY_DICT))

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

    def test_clear(self):
        self.assertEqual(0, len(self.dxfdict))
        self.dxfdict.clear()
        self.assertEqual(0, len(self.dxfdict))


class TestDXFDictSubDictCreation(unittest.TestCase):
    def setUp(self):  # this tests require a proper setup DXF drawing
        self.dwg = ezdxf.new('AC1015')

    def test_add_sub_dict(self):
        rootdict = self.dwg.rootdict
        self.assertFalse('MOZMAN_TEST' in rootdict)
        new_dict = rootdict.get_required_dict('MOZMAN_TEST')
        self.assertEqual('DICTIONARY', new_dict.dxftype())
        self.assertTrue('MOZMAN_TEST' in rootdict)


class TestDXFDictWithDefault(unittest.TestCase):
    def setUp(self):
        self.dxfdict = DXFDictionaryWithDefault(ExtendedTags.from_text(DEFAULT_DICT))

    def test_get_existing_value(self):
        self.assertEqual('F', self.dxfdict['Normal'])

    def test_get_not_existing_value(self):
        self.assertEqual('F', self.dxfdict['Mozman'])

    def test_get_default_value(self):
        self.assertEqual('F', self.dxfdict.dxf.default)

    def test_set_default_value(self):
        self.dxfdict.dxf.default = "MOZMAN"
        self.assertEqual('MOZMAN', self.dxfdict['Mozman'])


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

DEFAULT_DICT = """  0
ACDBDICTIONARYWDFLT
  5
E
102
{ACAD_REACTORS
330
C
102
}
330
C
100
AcDbDictionary
281
     1
  3
Normal
350
F
100
AcDbDictionaryWithDefault
340
F
"""

if __name__ == '__main__':
    unittest.main()
