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
        self.assertEqual(points, list(line.get_points()))
        self.assertEqual(3, len(line))
        self.assertFalse(line.closed, "Polyline should be open by default.")

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

    def test_append_points(self):
        points = [(1, 1), (2, 2), (3, 3)]
        line = self.layout.add_lwpolyline(points)
        line.append_points([(4, 4), (5, 5)])
        self.assertEqual((4, 4), line[-2])

    def test_context_manager(self):
        points = [(1, 1), (2, 2), (3, 3)]
        line = self.layout.add_lwpolyline(points)
        with line.points() as p:
            p.extend([(4, 4), (5, 5)])
        self.assertEqual((4, 4), line[-2])

    def test_discard_points(self):
        points = [(1, 1), (2, 2), (3, 3)]
        line = self.layout.add_lwpolyline(points, {'closed': True})
        self.assertTrue(line.closed, "Polyline should be closed")
        line.discard_points()
        self.assertEqual(0, len(line), "Polyline count should be 0.")
        self.assertFalse(list(line.get_points()), "Polyline should not have any points.")
        self.assertTrue(line.closed, "Polyline should be closed")

    def test_delete_const_width(self):
        points = [(1, 1), (2, 2), (3, 3)]
        line = self.layout.add_lwpolyline(points)
        line.dxf.const_width = 0.1
        self.assertEqual(0.1, line.dxf.const_width)
        del line.dxf.const_width
        self.assertFalse(line.AcDbPolyline.has_tag(43))


if __name__ == '__main__':
    unittest.main()