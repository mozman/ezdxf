#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test sections
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import sys
import unittest
from io import StringIO

from ezdxf.tags import text2tags
from ezdxf.tables import TablesSection

class DrawingMock:
    pass

def cmplines(text1, text2):
    lines1 = text1.split('\n')
    lines2 = text2.split('\n')
    for line1, line2 in zip(lines1, lines2):
        if line1.strip() != line2.strip():
            return False
    return True


class TestTables(unittest.TestCase):
    def setUp(self):
        self.dwg = DrawingMock()
        self.tables = TablesSection(text2tags(TEST_TABLES), self.dwg)

    def test_constructor(self):
        self.assertIsNotNone(self.tables.layer)

    def test_getattr(self):
        self.assertIsNotNone(self.tables.ltype)

    def test_error_getattr(self):
        with self.assertRaises(AttributeError):
            self.tables.test

    def test_write(self):
        stream = StringIO()
        self.tables.write(stream)
        result = stream.getvalue()
        stream.close()
        self.assertTrue(cmplines(TEST_TABLES, result))


TEST_TABLES = """  0
SECTION
  2
TABLES
  0
TABLE
  2
LTYPE
 70
     1
  0
LTYPE
  2
CONTINUOUS
 70
     0
  3
Solid line
 72
    65
 73
     0
 40
0.0
  0
ENDTAB
  0
TABLE
  2
LAYER
 70
     1
  0
LAYER
  2
0
 70
     0
 62
     7
  6
CONTINUOUS
  0
ENDTAB
  0
TABLE
  2
STYLE
 70
     1
  0
STYLE
  2
STANDARD
 70
     0
 40
0.0
 41
1.0
 50
0.0
 71
     0
 42
0.2
  3
txt
  4

  0
ENDTAB
  0
TABLE
  2
VIEW
 70
     0
  0
ENDTAB
  0
TABLE
  2
UCS
 70
     0
  0
ENDTAB
  0
TABLE
  2
APPID
 70
    0
  0
ENDTAB
  0
ENDSEC
"""

if __name__=='__main__':
    unittest.main()