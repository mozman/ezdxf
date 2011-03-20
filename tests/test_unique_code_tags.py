#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test UniqueCodeTags
# Created: 20.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import sys
import unittest

from ezdxf.tags import Tags, UniqueTags

TESTTAGS = """  2
TAGB
  2
TAGC
  0
TAGA
  7
TAGC
"""

class TestUniqueTags(unittest.TestCase):
    def setUp(self):
        self.tags = Tags.fromtext(TESTTAGS)
        self.uniquetags = UniqueTags(self.tags)

    def test_is_unique(self):
        self.assertTrue(0 in self.uniquetags)

    def test_is_not_unique(self):
        self.assertFalse(2 in self.uniquetags)

    def test_not_exist_is_unique(self):
        self.assertFalse(3 in self.uniquetags)

    def test_get_value_of_unique_code(self):
        self.assertEqual('TAGA', self.uniquetags[0])

    def test_error_for_getting_not_unique_code(self):
        with self.assertRaises(KeyError):
            self.uniquetags[2]

    def test_error_for_getting_not_existing_code(self):
        with self.assertRaises(KeyError):
            self.uniquetags[3]

    def test_set_value_of_unique_code(self):
        self.uniquetags[0] = 'NEWTAG'
        self.assertEqual('NEWTAG', self.uniquetags[0])

    def test_error_for_setting_not_unique_code(self):
        with self.assertRaises(KeyError):
            self.uniquetags[2] = 'ERROR'

    def test_error_for_setting_not_existing_code(self):
        with self.assertRaises(KeyError):
            self.uniquetags[3] = 'ERROR'

if __name__=='__main__':
    unittest.main()