#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test drawing
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import sys
import unittest
from io import StringIO

from ezdxf.tags import StringIterator

from ezdxf.drawing import Drawing

class TestDrawing(unittest.TestCase):
    def setUp(self):
        self.dwg = Drawing(StringIterator(TEST_HEADER))

    def test_dxfversion(self):
        self.assertEqual('AC1018', self.dwg.dxfversion)

    def test_copy_file(self):
        fp = StringIO(TESTCOPY)
        dwg = Drawing.read(fp)
        fp.close()
        dest = StringIO()
        dwg.write(dest)
        result = dest.getvalue()
        dest.close()
        self.assertEqual(TESTCOPY, result)


TEST_HEADER = """  0
SECTION
  2
HEADER
  9
$ACADVER
  1
AC1018
  9
$DWGCODEPAGE
  3
ANSI_1252
  0
ENDSEC
  0
EOF
"""

TESTCOPY = """  0
SECTION
  2
HEADER
  9
$ACADVER
  1
AC1018
  9
$DWGCODEPAGE
  3
ANSI_1252
  0
ENDSEC
  0
SECTION
  2
OBJECTS
  0
ENDSEC
  0
SECTION
  2
FANTASYSECTION
  1
everything should be copied
  0
ENDSEC
  0
SECTION
  2
ALPHASECTION
  1
everything should be copied
  0
ENDSEC
  0
SECTION
  2
OMEGASECTION
  1
everything should be copied
  0
ENDSEC
  0
EOF
"""

if __name__=='__main__':
    unittest.main()