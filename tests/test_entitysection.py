#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test entity section
# Created: 13.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import unittest
from io import StringIO

import ezdxf
from ezdxf.testtools import DrawingProxy, normlines, Tags
from ezdxf.entitysection import EntitySection


def make_test_drawing(version):
    dwg = ezdxf.new(version)
    modelspace = dwg.modelspace()
    modelspace.add_line((0, 0), (10, 0), {'layer': 'lay_line'})
    modelspace.add_text("TEST", dxfattribs={'layer': 'lay_line'})
    modelspace.add_polyline2d([(0, 0), (3, 1), (7, 4), (10, 0)], {'layer': 'lay_polyline'})
    # just 3 entities: LINE, TEXT, POLYLINE - VERTEX & SEQEND now linked to the POLYLINE entity, and do not appear
    # in any entity space
    return dwg


class TestEntitySection(unittest.TestCase):
    def setUp(self):
        self.dwg = DrawingProxy('AC1009')
        self.section = EntitySection(Tags.from_text(TESTENTITIES), self.dwg)

    def test_write(self):
        stream = StringIO()
        self.section.write(stream)
        result = stream.getvalue()
        stream.close()
        self.assertEqual(normlines(TESTENTITIES), normlines(result))

    def test_empty_section(self):
        section = EntitySection(Tags.from_text(EMPTYSEC), self.dwg)
        stream = StringIO()
        section.write(stream)
        result = stream.getvalue()
        stream.close()
        self.assertEqual(EMPTYSEC, result)

    def test_iteration_with_layout_DXF12(self):
        dwg = ezdxf.new('AC1009')
        m = dwg.modelspace()
        m.add_line((0, 0), (1, 1))
        entity = list(dwg.entities)[-1]
        self.assertEqual(dwg, entity.drawing)  # check drawing attribute

    def test_iteration_with_layout_DXF2000(self):
        dwg = ezdxf.new('AC1015')
        m = dwg.modelspace()
        m.add_line((0, 0), (1, 1))
        entity = list(dwg.entities)[-1]
        self.assertEqual(dwg, entity.drawing)  # check drawing attribute

    def test_delete_all_entities_DXF12(self):
        dwg = ezdxf.new('AC1009')
        m = dwg.modelspace()
        for _ in range(5):
            m.add_line((0, 0), (1, 1))
        self.assertEqual(5, len(dwg.entities))

        dwg.entities.delete_all_entities()
        self.assertEqual(0, len(dwg.entities))


class TestEntityQueryAC1009(unittest.TestCase):
    dwg = make_test_drawing('AC1009')

    def test_query_all_entities(self):
        # independent from layout (modelspace or paperspace)
        entities = self.dwg.entities.query('*')
        self.assertEqual(3, len(entities))

    def test_query_polyline(self):
        entities = self.dwg.entities.query('POLYLINE')
        self.assertEqual(1, len(entities))

    def test_query_line_and_polyline(self):
        entities = self.dwg.entities.query('POLYLINE LINE')
        self.assertEqual(2, len(entities))

    def test_query_vertices(self):
        # VERTEX entnties are no more in any entity space, they are lined to the POLYLINE entity
        entities = self.dwg.entities.query('VERTEX') #
        self.assertEqual(0, len(entities))

    def test_query_layer_line(self):
        entities = self.dwg.entities.query('*[layer=="lay_line"]')
        self.assertEqual(2, len(entities))

    def test_query_layer_polyline(self):
        entities = self.dwg.entities.query('*[layer=="lay_polyline"]')
        self.assertEqual(1, len(entities))

    def test_query_layer_by_regex(self):
        entities = self.dwg.entities.query('*[layer ? "lay_.*"]')
        self.assertEqual(3, len(entities))


class TestEntityQueryAC1018(TestEntityQueryAC1009):
    dwg = make_test_drawing('AC1018')


EMPTYSEC = """  0
SECTION
  2
ENTITIES
  0
ENDSEC
"""

TESTENTITIES = """  0
SECTION
  2
ENTITIES
  0
VIEWPORT
  5
28B
 67
     1
  8
0
 10
4.7994580606
 20
4.0218994936
 30
0.0
 40
17.880612775
 41
8.9929997457
 68
     1
 69
     1
1001
ACAD
1000
MVIEW
1002
{
1070
    16
1010
0.0
1020
0.0
1030
0.0
1010
0.0
1020
0.0
1030
1.0
1040
0.0
1040
8.99299974
1040
4.79945806
1040
4.02189949
1040
50.0
1040
0.0
1040
0.0
1070
     0
1070
  1000
1070
     1
1070
     1
1070
     0
1070
     0
1070
     0
1070
     0
1040
0.0
1040
0.0
1040
0.0
1040
0.5
1040
0.5
1040
0.5
1040
0.5
1070
     0
1002
{
1002
}
1002
}
  0
VIEWPORT
  5
290
 67
     1
  8
VIEW_PORT
 10
4.8288665
 20
3.9999997
 30
0.0
 40
8.3999996
 41
6.3999996
 68
     2
 69
     2
1001
ACAD
1000
MVIEW
1002
{
1070
    16
1010
0.0
1020
0.0
1030
0.0
1010
0.0
1020
0.0
1030
1.0
1040
0.0
1040
6.399999
1040
6.0
1040
4.5
1040
50.0
1040
0.0
1040
0.0
1070
     0
1070
  1000
1070
     1
1070
     3
1070
     0
1070
     0
1070
     0
1070
     0
1040
0.0
1040
0.0
1040
0.0
1040
0.5
1040
0.5
1040
0.5
1040
0.5
1070
     0
1002
{
1002
}
1002
}
  0
ENDSEC
"""


if __name__ == '__main__':
    unittest.main()