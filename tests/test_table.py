#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test table
# Created: 13.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import sys
import unittest
from io import StringIO

from ezdxf.handle import HandleGenerator
from ezdxf.dxffactory import dxffactory

from ezdxf.tags import Tags
from ezdxf.table import Table

class DrawingMock:
    def __init__(self):
        self.entitydb = dict()
        self.handles = HandleGenerator()
        self.dxffactory = dxffactory('AC1009')

def normlines(text):
    lines = text.split('\n')
    return [line.strip() for line in lines]

AC1009TABLE = """  0
TABLE
  2
APPID
 70
    10
  0
APPID
  2
ACAD
 70
     0
  0
APPID
  2
ACADANNOPO
 70
     0
  0
APPID
  2
ACADANNOTATIVE
 70
     0
  0
APPID
  2
ACAD_DSTYLE_DIMJAG
 70
     0
  0
APPID
  2
ACAD_DSTYLE_DIMTALN
 70
     0
  0
APPID
  2
ACAD_MLEADERVER
 70
     0
  0
APPID
  2
ACAECLAYERSTANDARD
 70
     0
  0
APPID
  2
ACAD_EXEMPT_FROM_CAD_STANDARDS
 70
     0
  0
APPID
  2
ACAD_DSTYLE_DIMBREAK
 70
     0
  0
APPID
  2
ACAD_PSEXT
 70
     0
  0
ENDTAB
"""

AC1024TABLE = """  0
TABLE
  2
APPID
  5
9
330
0
100
AcDbSymbolTable
 70
    10
  0
APPID
  5
12
330
9
100
AcDbSymbolTableRecord
100
AcDbRegAppTableRecord
  2
ACAD
 70
     0
  0
APPID
  5
DD
330
9
100
AcDbSymbolTableRecord
100
AcDbRegAppTableRecord
  2
AcadAnnoPO
 70
     0
  0
APPID
  5
DE
330
9
100
AcDbSymbolTableRecord
100
AcDbRegAppTableRecord
  2
AcadAnnotative
 70
     0
  0
APPID
  5
DF
330
9
100
AcDbSymbolTableRecord
100
AcDbRegAppTableRecord
  2
ACAD_DSTYLE_DIMJAG
 70
     0
  0
APPID
  5
E0
330
9
100
AcDbSymbolTableRecord
100
AcDbRegAppTableRecord
  2
ACAD_DSTYLE_DIMTALN
 70
     0
  0
APPID
  5
107
330
9
100
AcDbSymbolTableRecord
100
AcDbRegAppTableRecord
  2
ACAD_MLEADERVER
 70
     0
  0
APPID
  5
1B5
330
9
100
AcDbSymbolTableRecord
100
AcDbRegAppTableRecord
  2
AcAecLayerStandard
 70
     0
  0
APPID
  5
1BA
330
9
100
AcDbSymbolTableRecord
100
AcDbRegAppTableRecord
  2
ACAD_EXEMPT_FROM_CAD_STANDARDS
 70
     0
  0
APPID
  5
237
330
9
100
AcDbSymbolTableRecord
100
AcDbRegAppTableRecord
  2
ACAD_DSTYLE_DIMBREAK
 70
     0
  0
APPID
  5
28E
330
9
100
AcDbSymbolTableRecord
100
AcDbRegAppTableRecord
  2
ACAD_PSEXT
 70
     0
  0
ENDTAB
"""

class TestR12Table(unittest.TestCase):
    TABLE = AC1009TABLE
    def setUp(self):
        self.dwg = DrawingMock()
        self.table = Table(Tags.fromtext(self.TABLE), self.dwg)

    def test_table_setup(self):
        self.assertEqual(10, len(self.table))

    def test_write(self):
        stream = StringIO()
        self.table.write(stream)
        result = stream.getvalue()
        stream.close()
        self.maxDiff = None
        self.assertEqual(normlines(self.TABLE), normlines(result))

    def test_get_table_entry(self):
        entry = self.table.get_entry('ACAD')
        self.assertEqual('ACAD', entry.name)

class TestR2010Table(TestR12Table):
    TABLE = AC1024TABLE

if __name__=='__main__':
    unittest.main()