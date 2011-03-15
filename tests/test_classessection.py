#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test entity section
# Created: 15.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import sys
import unittest
from io import StringIO

from ezdxf.handle import HandleGenerator
from ezdxf.tags import Tags

from ezdxf.entitysection import ClassesSection

class DrawingMock:
    entitydb = dict()
    handles = HandleGenerator()

def normlines(text):
    lines = text.split('\n')
    return [line.strip() for line in lines]

class TestClassesSection(unittest.TestCase):
    def setUp(self):
        self.dwg = DrawingMock()
        self.section = ClassesSection(Tags.fromtext(TESTCLASSES), self.dwg)

    def test_write(self):
        stream = StringIO()
        self.section.write(stream)
        result = stream.getvalue()
        stream.close()
        self.assertEqual(normlines(TESTCLASSES), normlines(result))

    def test_empty_section(self):
        section = ClassesSection(Tags.fromtext(EMPTYSEC), self.dwg)
        stream = StringIO()
        section.write(stream)
        result = stream.getvalue()
        stream.close()
        self.assertEqual(EMPTYSEC, result)

EMPTYSEC = """  0
SECTION
  2
CLASSES
  0
ENDSEC
"""

TESTCLASSES = """  0
SECTION
  2
CLASSES
  0
CLASS
  1
ACDBDICTIONARYWDFLT
  2
AcDbDictionaryWithDefault
  3
ObjectDBX Classes
 90
        0
 91
        1
280
     0
281
     0
  0
CLASS
  1
DICTIONARYVAR
  2
AcDbDictionaryVar
  3
ObjectDBX Classes
 90
        0
 91
       13
280
     0
281
     0
  0
CLASS
  1
TABLESTYLE
  2
AcDbTableStyle
  3
ObjectDBX Classes
 90
     4095
 91
        1
280
     0
281
     0
  0
ENDSEC
"""

if __name__=='__main__':
    unittest.main()