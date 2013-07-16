#!/usr/bin/env python
#coding:utf-8
# Author:  mozman --<mozman@gmx.at>
# Purpose: test LWPolyline 
# Created: 2011-05-01
from __future__ import unicode_literals

import unittest

import ezdxf


class TestLWPolyline(unittest.TestCase):
    def setUp(self):
        self.dwg = ezdxf.new('AC1015')
        self.layout = self.dwg.modelspace()

    def test_new_line(self):
        points = [(1, 1), (2, 2), (3, 3)]
        line = self.layout.add_lwpolyline(points)
        self.assertEqual(points, list(line.points()))
        self.assertEqual(3, len(line))

    def test_getitem_first(self):
        points = [(1, 1), (2, 2), (3, 3)]
        line = self.layout.add_lwpolyline(points)
        self.assertEqual((1, 1), line[0])

    def test_getitem_last(self):
        points = [(1, 1), (2, 2), (3, 3)]
        line = self.layout.add_lwpolyline(points)
        self.assertEqual((3, 3), line[-1])

    def test_getitem_error(self):
        points = [(1, 1), (2, 2), (3, 3)]
        line = self.layout.add_lwpolyline(points)
        with self.assertRaises(IndexError):
            line[3]


if __name__ == '__main__':
    unittest.main()