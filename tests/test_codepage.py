#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test codepage
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License

from __future__ import unicode_literals

import unittest

from ezdxf.codepage import toencoding, tocodepage

class TestToEncoding(unittest.TestCase):
    def test_ansi_1250(self):
        self.assertEqual('cp1250', toencoding('ansi_1250'))

    def test_default(self):
        self.assertEqual('cp1252', toencoding('xyz'))

    def test_tocodepage_1252(self):
        self.assertEqual('ANSI_1252', tocodepage('cp1252'))

    def test_tocodepage_936(self):
        self.assertEqual('ANSI_936', tocodepage('hz'))


if __name__=='__main__':
    unittest.main()