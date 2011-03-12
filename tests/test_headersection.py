#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test header section
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import sys
import unittest

from ezdxf.dxfengine import dxfengine

from ezdxf.tags import text2tags
from ezdxf.header import HeaderSection

class DrawingProxy:
    dxfengine = dxfengine('AC1009')


class TestHeaderSection(unittest.TestCase):
    def setUp(self):
        tags = text2tags(TESTHEADER)
        self.header = HeaderSection(tags, DrawingProxy())

    def test_get_acadver(self):
        result = self.header['$ACADVER']
        self.assertEqual('AC1009', result)

    def test_get_insbase(self):
        result = self.header['$INSBASE']
        self.assertEqual((0., 0., 0.), result)

    def test_getitem_keyerror(self):
        with self.assertRaises(KeyError):
            var = self.header['$TEST']

    def test_get(self):
        result = self.header.get('$TEST', 'TEST')
        self.assertEqual('TEST', result)

    def test_set_existing_var(self):
        self.header['$ACADVER'] = 'AC666'
        self.assertEqual('AC666', self.header['$ACADVER'])

    def test_set_existing_point(self):
        self.header['$INSBASE'] = (1, 2, 3)
        self.assertEqual((1, 2, 3), self.header['$INSBASE'])

    def test_set_unknown_var(self):
        with self.assertRaises(KeyError):
            self.header['$TEST'] = 'test'

    def test_create_var(self):
        self.header['$LIMMAX'] = (10, 20)
        self.assertEqual((10, 20), self.header['$LIMMAX'])

    def test_create_var_wrong_args_2d(self):
        self.header['$LIMMAX'] = (10, 20, 30)
        self.assertEqual((10, 20), self.header['$LIMMAX'])

    def test_create_var_wrong_args_3d(self):
        with self.assertRaises(IndexError):
            self.header['$PUCSORG'] = (10, 20)

TESTHEADER = """  0
SECTION
  2
HEADER
  9
$ACADVER
  1
AC1009
  9
$INSBASE
 10
0.0
 20
0.0
 30
0.0
  9
$EXTMIN
 10
1.0000000000000000E+020
 20
1.0000000000000000E+020
 30
1.0000000000000000E+020
  9
$EXTMAX
 10
-1.0000000000000000E+020
 20
-1.0000000000000000E+020
 30
-1.0000000000000000E+020
  0
ENDSEC"""

if __name__=='__main__':
    unittest.main()