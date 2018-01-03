#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test classifiedtags
# Created: 30.04.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import unittest
from io import StringIO

from ezdxf.lldxf.tags import Tags, DXFTag
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.lldxf.repair import join_subclasses


class TestClassifiedTags(unittest.TestCase):
    def setUp(self):
        self.xtags = ExtendedTags.from_text(XTAGS1)

    def test_init_appdata(self):
        self.assertIsNotNone(self.xtags.get_app_data('{ACAD_XDICTIONARY'))

    def test_init_with_tags(self):
        tags = Tags.from_text(XTAGS1)
        xtags = ExtendedTags(tags)
        self.assertEqual(3, len(xtags.subclasses))
        self.assertEqual(1, len(xtags.xdata))

    def test_init_xdata(self):
        self.assertIsNotNone(self.xtags.get_xdata('RAK'))

    def test_appdata_content_count(self):
        xdict = self.xtags.get_app_data('{ACAD_XDICTIONARY')
        self.assertEqual(3, len(xdict))

    def test_appdata_content(self):
        xdict = self.xtags.get_app_data('{ACAD_XDICTIONARY')
        self.assertEqual(xdict.find_first(360), "63D5")

    def test_tags_skips_appdata_content(self):
        with self.assertRaises(ValueError):
            self.xtags.noclass.find_first(360)

    def test_xdata_content_count(self):
        rak = self.xtags.get_xdata('RAK')
        self.assertEqual(17, len(rak))

    def test_tags_skips_xdata_content(self):
        with self.assertRaises(ValueError):
            self.xtags.noclass.find_first(1000)

    def test_copy(self):
        stream = StringIO()
        self.xtags.write(stream)
        self.assertEqual(XTAGS1, stream.getvalue())
        stream.close()

    def test_getitem_layer(self):
        self.assertEqual(self.xtags.noclass[0], (0, 'LAYER'))

    def test_getitem_xdict(self):
        self.assertEqual(self.xtags.noclass[2], (102, 0))

    def test_getitem_parent(self):
        self.assertEqual(self.xtags.noclass[3], (330, '18'))

    def test_get_last_item(self):
        self.assertEqual(self.xtags.noclass[-1], (330, '18'))

    def test_tagscount(self):
        """ apdata counts as one tag and xdata counts as one tag. """
        self.assertEqual(4, len(self.xtags.noclass))

    def test_subclass_AcDbSymbolTableRecord(self):
        subclass = self.xtags.get_subclass('AcDbSymbolTableRecord')
        self.assertEqual(1, len(subclass))

    def test_subclass_AcDbLayerTableRecord(self):
        subclass = self.xtags.get_subclass('AcDbLayerTableRecord')
        self.assertEqual(8, len(subclass))

    def test_clone_is_equal(self):
        clone = self.xtags.clone()
        self.assertTrue(self.xtags is not clone)
        self.assertTrue(self.xtags.appdata is not clone.appdata)
        self.assertTrue(self.xtags.subclasses is not clone.subclasses)
        self.assertTrue(self.xtags.xdata is not clone.xdata)
        self.assertEqual(list(self.xtags), list(clone))

    def test_replace_handle(self):
        self.xtags.replace_handle('AA')
        self.assertEqual('AA', self.xtags.get_handle())


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
        self.tags = ExtendedTags.from_text(XTAGS2)

    def test_xdata_count(self):
        self.assertEqual(3, len(self.tags.xdata))

    def test_tags_count(self):
        """ 3 xdata chunks and two 'normal' tag. """
        self.assertEqual(2, len(self.tags.noclass))

    def test_xdata3_tags(self):
        xdata = self.tags.get_xdata('XDATA3')
        self.assertEqual(xdata[0], (1001, 'XDATA3'))
        self.assertEqual(xdata[1], (1000, 'TEXT-XDATA3'))
        self.assertEqual(xdata[2], (1070, 2))
        self.assertEqual(xdata[3], (1070, 3))

    def test_new_data(self):
        self.tags.new_xdata('NEWXDATA', [(1000, 'TEXT')])
        self.assertTrue(self.tags.has_xdata('NEWXDATA'))

        xdata = self.tags.get_xdata('NEWXDATA')
        self.assertEqual(xdata[0], (1001, 'NEWXDATA'))
        self.assertEqual(xdata[1], (1000, 'TEXT'))

    def test_set_new_data(self):
        self.tags.new_xdata('NEWXDATA', tags=[(1000, "Extended Data String")])
        self.assertTrue(self.tags.has_xdata('NEWXDATA'))

        xdata = self.tags.get_xdata('NEWXDATA')
        self.assertEqual((1001, 'NEWXDATA'), xdata[0])
        self.assertEqual((1000, "Extended Data String"), xdata[1])

    def test_append_xdata(self):
        xdata = self.tags.get_xdata('MOZMAN')
        self.assertEqual(4, len(xdata))

        xdata.append(DXFTag(1000, "Extended Data String"))
        xdata = self.tags.get_xdata('MOZMAN')
        self.assertEqual(5, len(xdata))

        self.assertEqual(DXFTag(1000, "Extended Data String"), xdata[4])

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
1001
XDATA3
1000
TEXT-XDATA3
1070
2
1070
3
"""


class Test2xSubclass(unittest.TestCase):
    def setUp(self):
        self.tags = ExtendedTags.from_text(SPECIALCASE_TEXT)

    def test_read_tags(self):
        subclass2 = self.tags.get_subclass('AcDbText')
        self.assertEqual((100, 'AcDbText'), subclass2[0])

    def test_read_tags_2(self):
        subclass2 = self.tags.get_subclass('AcDbText')
        self.assertEqual((100, 'AcDbText'), subclass2[0])
        self.assertEqual((1, 'Title:'), subclass2[3])

    def test_read_tags_3(self):
        subclass2 = self.tags.get_subclass('AcDbText', 3)
        self.assertEqual((100, 'AcDbText'), subclass2[0])
        self.assertEqual((73, 2), subclass2[1])

    def test_key_error(self):
        with self.assertRaises(KeyError):
            self.tags.get_subclass('AcDbText', pos=4)

    def test_skip_empty_subclass(self):
        self.tags.subclasses[1] = Tags()
        subclass2 = self.tags.get_subclass('AcDbText')
        self.assertEqual((100, 'AcDbText'), subclass2[0])


SPECIALCASE_TEXT = """  0
TEXT
  5
8C9
330
6D
100
AcDbEntity
  8
0
100
AcDbText
 10
4.30
 20
1.82
 30
0.0
 40
0.125
  1
Title:
 41
0.85
  7
ARIALNARROW
100
AcDbText
 73
2
"""

ACAD_REACTORS = '{ACAD_REACTORS'


class TestAppData(unittest.TestCase):
    def setUp(self):
        self.tags = ExtendedTags.from_text(NO_REACTORS)

    def test_get_not_existing_reactor(self):
        with self.assertRaises(ValueError):
            self.tags.get_app_data(ACAD_REACTORS)

    def test_new_reactors(self):
        self.tags.new_app_data(ACAD_REACTORS)
        self.assertEqual((102, 0), self.tags.noclass[-1])  # code = 102, value = index in appdata list

    def test_append_not_existing_reactors(self):
        self.tags.new_app_data(ACAD_REACTORS, [DXFTag(330, 'DEAD')])
        reactors = self.tags.get_app_data_content(ACAD_REACTORS)
        self.assertEqual(1, len(reactors))
        self.assertEqual(DXFTag(330, 'DEAD'), reactors[0])

    def test_append_to_existing_reactors(self):
        self.tags.new_app_data(ACAD_REACTORS, [DXFTag(330, 'DEAD')])
        reactors = self.tags.get_app_data_content(ACAD_REACTORS)
        reactors.append(DXFTag(330, 'DEAD2'))
        self.tags.set_app_data_content(ACAD_REACTORS, reactors)

        reactors = self.tags.get_app_data_content(ACAD_REACTORS)
        self.assertEqual(DXFTag(330, 'DEAD'), reactors[0])
        self.assertEqual(DXFTag(330, 'DEAD2'), reactors[1])

NO_REACTORS = """  0
TEXT
  5
8C9
330
6D
100
AcDbEntity
  8
0
100
AcDbText
 10
4.30
 20
1.82
 30
0.0
 40
0.125
  1
Title:
 41
0.85
  7
ARIALNARROW
"""


class TestRepairLeicaDistoDXF12Files(unittest.TestCase):
    def test_join_subclasses(self):
        tags = ExtendedTags.from_text(LEICA_DISTO_TAGS)
        join_subclasses(tags.subclasses)
        self.assertEqual(9, len(tags.noclass))
        self.assertEqual(1, len(tags.subclasses))


LEICA_DISTO_TAGS = """0
LINE
100
AcDbEntity
8
LEICA_DISTO_3D
62
256
6
ByLayer
5
75
100
AcDbLine
10
0.819021
20
-0.633955
30
-0.273577
11
0.753216
21
-0.582009
31
-0.276937
39
0
210
0
220
0
230
1
"""

if __name__ == '__main__':
    unittest.main()