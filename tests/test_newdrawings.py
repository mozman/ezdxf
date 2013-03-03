#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test open all templates
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import unittest

import ezdxf


class TestNewDrawings(unittest.TestCase):
    def test_new_AC1009(self):
        dwg = ezdxf.new('AC1009')
        self.assertEqual('AC1009', dwg.dxfversion)

    def test_new_AC1015(self):
        dwg = ezdxf.new('AC1015')
        self.assertEqual('AC1015', dwg.dxfversion)

    def test_new_AC1018(self):
        dwg = ezdxf.new('AC1018')
        self.assertEqual('AC1018', dwg.dxfversion)

    def test_new_AC1021(self):
        dwg = ezdxf.new('AC1021')
        self.assertEqual('AC1021', dwg.dxfversion)

    def test_new_AC1024(self):
        dwg = ezdxf.new('AC1024')
        self.assertEqual('AC1024', dwg.dxfversion)


if __name__ == '__main__':
    unittest.main()