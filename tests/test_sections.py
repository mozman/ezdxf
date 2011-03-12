#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test sections
# Created: 12.03.2011
# Copyright (C) , Manfred Moitzi
# License: GPLv3

import sys
import unittest

from ezdxf.tags import StringIterator
from ezdxf.sections import Sections

class DrawingMock:
    pass

class TestSections(unittest.TestCase):
    def setUp(self):
        self.dwg = DrawingMock()
        self.sections = Sections(self.dwg, StringIterator(TEST_HEADER))

    def test_constructor(self):
        self.assertTrue('header' in self.sections)

    def test_getitem(self):
        result = self.sections['header']
        self.assertIsNotNone(result)

    def test_getattr(self):
        result = self.sections.header
        self.assertIsNotNone(result)

    def test_error_getitem(self):
        with self.assertRaises(KeyError):
            self.sections['test']

    def test_error_getattr(self):
        with self.assertRaises(AttributeError):
            self.sections.test

    def test_ignore_struct_error(self):
        sections = Sections(self.dwg, StringIterator(TEST_NO_EOF))
        self.assertTrue('header' in self.sections)

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
SECTION
  2
TABLES
  0
ENDSEC
  0
EOF
"""

TEST_NO_EOF = """  0
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
"""

if __name__=='__main__':
    unittest.main()