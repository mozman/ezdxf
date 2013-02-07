#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test type caster
# Created: 10.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import unittest

from ezdxf.tags import tagcast

class TestTypeCaster(unittest.TestCase):

    def test_cast_string(self):
        result = tagcast( (1, 'STRING') )
        self.assertEqual( (1, 'STRING'), result)

    def test_cast_float(self):
        result = tagcast( (10, '3.1415') )
        self.assertEqual( (10, 3.1415), result)

    def test_cast_int(self):
        result = tagcast( (60, '4711') )
        self.assertEqual( (60, 4711), result)

    def test_cast_bool_True(self):
        result = tagcast( (290, '1') )
        self.assertEqual( (290, 1), result)

    def test_cast_bool_False(self):
        result = tagcast( (290, '0') )
        self.assertEqual( (290, 0), result)

if __name__=='__main__':
    unittest.main()