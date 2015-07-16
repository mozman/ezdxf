#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test entity section
# Created: 13.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import unittest
from io import StringIO

from ezdxf.tools.test import DrawingProxy, Tags, normlines
from ezdxf.entitysection import ObjectsSection


class TestObjectsSection(unittest.TestCase):
    def setUp(self):
        self.dwg = DrawingProxy('AC1009')
        self.section = ObjectsSection(Tags.from_text(TESTOBJECTS), self.dwg)

    def test_write(self):
        stream = StringIO()
        self.section.write(stream)
        result = stream.getvalue()
        stream.close()
        self.assertEqual(normlines(TESTOBJECTS), normlines(result))

    def test_empty_section(self):
        section = ObjectsSection(Tags.from_text(EMPTYSEC), self.dwg)
        stream = StringIO()
        section.write(stream)
        result = stream.getvalue()
        stream.close()
        self.assertEqual(EMPTYSEC, result)


EMPTYSEC = """  0
SECTION
  2
OBJECTS
  0
ENDSEC
"""

TESTOBJECTS = """  0
SECTION
  2
OBJECTS
  0
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
499
  3
AcDbVariableDictionary
350
66
  0
DICTIONARY
  5
2A2
330
2
100
AcDbDictionary
280
     1
281
     1
  3
ACAD_LAYERSTATES
360
2A3
  0
DICTIONARY
  5
E6
330
10
100
AcDbDictionary
280
     1
281
     1
  0
DICTIONARY
  5
15D
330
1F
100
AcDbDictionary
280
     1
281
     1
  0
DICTIONARY
  5
28C
330
28B
100
AcDbDictionary
280
     1
281
     1
  3
ASDK_XREC_ANNOTATION_SCALE_INFO
360
28D
  0
DICTIONARY
  5
291
330
290
100
AcDbDictionary
280
     1
281
     1
  3
ASDK_XREC_ANNOTATION_SCALE_INFO
360
292
  0
ENDSEC
"""

if __name__ == '__main__':
    unittest.main()