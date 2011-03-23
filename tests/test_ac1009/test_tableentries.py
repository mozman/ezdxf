#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test ac1009/tableentries
# Created: 16.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import sys
import unittest

from ezdxf.tags import Tags

from ezdxf.ac1009.tableentries import Layer

class TestNewLayer(unittest.TestCase):
    def setUp(self):
        self.layer = Layer.new('FFFF')

    def test_new_layer(self):
        self.assertEqual(6, len(self.layer.tags))

    def test_get_handle(self):
        self.assertEqual('FFFF', self.layer.handle)

    def test_get_name(self):
        self.assertEqual('LAYERNAME', self.layer.name)

    def test_get_flags(self):
        self.assertEqual(0, self.layer.flags)

    def test_get_color(self):
        self.assertEqual(7, self.layer.color)

    def test_get_linetype(self):
        self.assertEqual('CONTINUOUS', self.layer.linetype)

    def test_set_name(self):
        self.layer.name = 'MOZMAN'
        self.assertEqual('MOZMAN', self.layer.name)

    def test_set_color(self):
        self.layer.color = '1'
        self.assertEqual(1, self.layer.color)


if __name__=='__main__':
    unittest.main()