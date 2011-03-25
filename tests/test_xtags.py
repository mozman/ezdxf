#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test ExtendedTags
# Created: 25.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import sys
import unittest

from io import StringIO

from ezdxf.tags import Tags, ExtendedTags

class TestExtendedTags(unittest.TestCase):
    def setUp(self):
        self.xtags = ExtendedTags.fromtext(XTAGS1)

    def test_init_appdata(self):
        self.assertTrue('{ACAD_XDICTIONARY' in self.xtags.appdata)

    def test_init_with_tags(self):
        tags = Tags.fromtext(XTAGS1)
        xtags = ExtendedTags(tags)
        self.assertEqual(14, len(xtags))

    def test_init_xdata(self):
        self.assertTrue('RAK' in self.xtags.xdata)

    def test_appdata_content_count(self):
        xdict = self.xtags.appdata['{ACAD_XDICTIONARY']
        self.assertEqual(3, len(xdict))

    def test_appdata_content(self):
        xdict = self.xtags.appdata['{ACAD_XDICTIONARY']
        self.assertEqual(xdict.getvalue(360), "63D5")

    def test_tags_skips_appdata_content(self):
        with self.assertRaises(ValueError):
            self.xtags.getvalue(360)

    def test_xdata_content_count(self):
        rak = self.xtags.xdata['RAK']
        self.assertEqual(17, len(rak))

    def test_tags_skips_xdata_content(self):
        with self.assertRaises(ValueError):
            self.xtags.getvalue(1000)

    def test_copy(self):
        stream = StringIO()
        self.xtags.write(stream)
        self.assertEqual(XTAGS1, stream.getvalue())
        stream.close()

    def test_getitem_layer(self):
        self.assertEqual(self.xtags[0], (0, 'LAYER'))

    def test_getitem_xdict(self):
        self.assertEqual(self.xtags[2], (102, '{ACAD_XDICTIONARY'))

    def test_getitem_parent(self):
        self.assertEqual(self.xtags[3], (330, '18'))

    def test_get_last_item(self):
        self.assertEqual(self.xtags[-1], (1001, 'RAK'))

    def test_tagscount(self):
        """ apdata counts as one tag and xdata counts as one tag. """
        self.assertEqual(14, len(self.xtags))

XTAGS1 = """  0
LAYER
  5
7
102
{ACAD_XDICTIONARY
360
63D5
102
}
330
18
100
AcDbSymbolTableRecord
100
AcDbLayerTableRecord
  2
0
 70
0
 62
7
  6
CONTINUOUS
370
-3
390
8
347
805
1001
RAK
1000
{75-LÄNGENSCHNITT-14
1070
0
1070
7
1000
CONTINUOUS
1071
-3
1071
1
1005
8
1000
75-LÄNGENSCHNITT-14}
1000
{75-LÄNGENSCHNITT-2005
1070
0
1070
7
1000
CONTINUOUS
1071
-3
1071
1
1005
8
1000
75-LÄNGENSCHNITT-2005}
"""

class TestXDATA(unittest.TestCase):
    def setUp(self):
        self.tags = ExtendedTags.fromtext(XTAGS2)

    def test_xdata_count(self):
        self.assertEqual(3, len(self.tags.xdata))

    def test_tags_count(self):
        """ 3 xdata chunks and three 'normal' tag. """
        self.assertEqual(6, len(self.tags))

    def test_tag_40(self):
        self.assertEqual(self.tags.getvalue(40), 1)

    def test_xdata3_tags(self):
        xdata = self.tags.xdata['XDATA3']
        self.assertEqual(xdata[0], (1001, 'XDATA3'))
        self.assertEqual(xdata[1], (1000, 'TEXT-XDATA3'))
        self.assertEqual(xdata[2], (1070, 2))
        self.assertEqual(xdata[3], (1070, 3))

XTAGS2 = """  0
LAYER
  5
7
1001
RAK
1000
TEXT-RAK
1070
1
1070
1
1001
MOZMAN
1000
TEXT-MOZMAN
1070
2
1070
2
 40
1
1001
XDATA3
1000
TEXT-XDATA3
1070
2
1070
3
"""
if __name__=='__main__':
    unittest.main()