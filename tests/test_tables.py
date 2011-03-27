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

from tools import DrawingProxy, normlines, Tags

from ezdxf.tablessection import TablesSection

class TestTables(unittest.TestCase):
    def setUp(self):
        self.dwg = DrawingProxy('AC1009')
        self.tables = TablesSection(Tags.fromtext(TEST_TABLES), self.dwg)

    def test_constructor(self):
        self.assertIsNotNone(self.tables.layers)

    def test_getattr(self):
        self.assertIsNotNone(self.tables.linetypes)

    def test_error_getattr(self):
        with self.assertRaises(AttributeError):
            self.tables.test

    def test_write(self):
        stream = StringIO()
        self.tables.write(stream)
        result = stream.getvalue()
        stream.close()
        self.assertEqual(normlines(TEST_TABLES), normlines(result))


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