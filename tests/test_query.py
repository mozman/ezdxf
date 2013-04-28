# encoding: utf-8
# Copyright (C) 2013, Manfred Moitzi
# License: MIT-License

import unittest

import ezdxf

from ezdxf.query import EntityQuery

def make_test_drawing(version):
    dwg = ezdxf.new(version)
    modelspace = dwg.modelspace()
    modelspace.add_line((0, 0), (10, 0), {'layer': 'lay_lines'})
    modelspace.add_polyline2d([(0, 0), (3, 1), (7, 4), (10, 0)], {'layer': 'lay_lines'})
    return dwg

class TestEntityQuery_AC1009(unittest.TestCase):
    VERSION = 'AC1009'
    dwg = make_test_drawing(VERSION)
    def test_select_all(self):
        modelspace = self.dwg.modelspace()
        result = EntityQuery(modelspace, '*')
        # 1xLINE, 1xPOLYLINE, 4xVERTEX, 1xSEQEND
        self.assertEqual(len(result.entities), 7)

class TestEntityQuery_AC1015(TestEntityQuery_AC1009):
    VERSION = 'AC1015'

if __name__ == '__main__':
    unittest.main()
