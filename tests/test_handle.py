#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test handle
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import sys
import unittest

from ezdxf.handle import HandleGenerator, hexstr

class TestHandleGenerator(unittest.TestCase):
    def test_next(self):
        handgen = HandleGenerator(100)
        self.assertEqual(100, handgen.next)

    def test_seed(self):
        handgen = HandleGenerator(200)
        handgen.next
        self.assertEqual(201, handgen.seed)

    def test_hexstr(self):
        self.assertEqual('FF', hexstr(255))

if __name__=='__main__':
    unittest.main()