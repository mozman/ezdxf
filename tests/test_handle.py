#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test handle
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import unittest

from ezdxf.handle import HandleGenerator


class TestHandleGenerator(unittest.TestCase):
    def test_next(self):
        handles = HandleGenerator('100')
        self.assertEqual('100', handles.next())

    def test_next_function(self):
        handles = HandleGenerator('100')
        self.assertEqual('100', next(handles))

    def test_seed(self):
        handles = HandleGenerator('200')
        handles.next()
        self.assertEqual('201', str(handles))

    def test_reset(self):
        handles = HandleGenerator('200')
        handles.reset('300')
        self.assertEqual('300', str(handles))


if __name__ == '__main__':
    unittest.main()