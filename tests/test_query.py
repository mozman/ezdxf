# encoding: utf-8
# Copyright (C) 2013, Manfred Moitzi
# License: MIT-License

import unittest

import ezdxf

from ezdxf.query import EntityQuery, name_query


def make_test_drawing(version):
    dwg = ezdxf.new(version)
    modelspace = dwg.modelspace()
    modelspace.add_line((0, 0), (10, 0), {'layer': 'lay_lines', 'color': 7})
    modelspace.add_polyline2d([(0, 0), (3, 1), (7, 4), (10, 0)], {'layer': 'lay_lines', 'color': 6})
    modelspace.add_text("TEST", dxfattribs={'layer': 'lay_text', 'color': 6})
    # just 3 entities: LINE, TEXT, POLYLINE - VERTEX & SEQEND now linked to the POLYLINE entity, and do not appear
    # in any entity space
    return dwg


class TestEntityQuery_AC1009(unittest.TestCase):
    VERSION = 'AC1009'
    dwg = make_test_drawing(VERSION)

    def test_select_all(self):
        modelspace = self.dwg.modelspace()
        result = EntityQuery(modelspace, '*')
        # 1xLINE, 1xPOLYLINE, 0xVERTEX, 0xSEQEND, 1x TEXT
        self.assertEqual(3, len(result.entities))
        self.assertEqual(3, len(result))

    def test_new_query_select_all(self):
        modelspace = self.dwg.modelspace()
        result = ezdxf.query.new(modelspace, '*')
        # 1xLINE, 1xPOLYLINE, 0xVERTEX, 0xSEQEND, 1x TEXT
        self.assertEqual(3, len(result.entities))
        self.assertEqual(3, len(result))

    def test_new_empty_query(self):
        result = ezdxf.query.new()
        self.assertEqual(0, len(result.entities))
        self.assertEqual(0, len(result))

    def test_select_line(self):
        modelspace = self.dwg.modelspace()
        result = EntityQuery(modelspace, 'LINE')
        # 1xLINE
        self.assertEqual(1, len(result))

    def test_select_layer_1(self):
        modelspace = self.dwg.modelspace()
        result = EntityQuery(modelspace, '*[layer=="lay_lines"]')
        # 1xLINE 1xPOLYLINE
        self.assertEqual(2, len(result))

    def test_match_regex(self):
        modelspace = self.dwg.modelspace()
        result = EntityQuery(modelspace, '*[layer ? "lay_.*"]')
        self.assertEqual(3, len(result))

    def test_match_whole_string(self):
        # re just compares the start of a string, check for an
        # implicit '$' at the end of the search string.
        modelspace = self.dwg.modelspace()
        result = EntityQuery(modelspace, '*[layer=="lay"]')
        self.assertEqual(0, len(result))

    def test_not_supported_attribute(self):
        modelspace = self.dwg.modelspace()
        result = EntityQuery(modelspace, '*[mozman!="TEST"]')
        self.assertEqual(0, len(result))

    def test_bool_select(self):
        modelspace = self.dwg.modelspace()
        result = EntityQuery(modelspace, '*[layer=="lay_lines" & color==7]')
        # 1xLINE
        self.assertEqual(1, len(result))

    def test_bool_select_2(self):
        modelspace = self.dwg.modelspace()
        result = EntityQuery(modelspace, '*[layer=="lay_lines" & color==7 | color==6]')
        # 1xLINE(layer=="lay_lines" & color==7) 1xPOLYLINE(color==6) 1xTEXT(color==6)
        self.assertEqual(3, len(result))

    def test_bool_select_3(self):
        modelspace = self.dwg.modelspace()
        result = EntityQuery(modelspace, '*[layer=="lay_lines" & (color==7 | color==6)]')
        # 1xLINE(layer=="lay_lines" & color==7) 1xPOLYLINE(layer=="lay_lines" & color==6)
        self.assertEqual(2, len(result))

    def test_bool_select_4(self):
        modelspace = self.dwg.modelspace()
        result = EntityQuery(modelspace, '*[(layer=="lay_lines" | layer=="lay_text") & !color==7]')
        # 1xPOLYLINE(layer=="lay_lines" & color==6) 1xTEXT(layer=="lay_text" & color==6)
        self.assertEqual(2, len(result))

    def test_ignore_case(self):
        modelspace = self.dwg.modelspace()
        result = EntityQuery(modelspace, '*[layer=="LAY_lines"]i')
        # 1xLINE 1xPOLYLINE
        self.assertEqual(2, len(result))

    def test_ignore_case_for_num_values(self):
        modelspace = self.dwg.modelspace()
        result = EntityQuery(modelspace, '*[color==6]i')
        # 1xPOLYLINE 1xTEXT
        self.assertEqual(2, len(result))

    def test_ignore_case_match_regex(self):
        modelspace = self.dwg.modelspace()
        result = EntityQuery(modelspace, '*[layer ? "LaY_.*"]i')
        self.assertEqual(3, len(result))

    def test_extend_query(self):
        modelspace = self.dwg.modelspace()
        result = EntityQuery(modelspace, '*')
        length = len(result)
        result.extend(result, unique=True)
        self.assertEqual(length, len(result))


class TestEntityQuery_AC1015(TestEntityQuery_AC1009):
    VERSION = 'AC1015'


class TestNameQuery(unittest.TestCase):
    def test_all_names(self):
        names = "ONE TWO THREE"
        result = " ".join(name_query(names.split(), '*'))
        self.assertEqual(names, result)

    def test_match_one_string(self):
        names = "ONE TWO THREE"
        result = list(name_query(names.split(), 'ONE'))
        self.assertEqual("ONE", result[0])

    def test_match_full_string(self):
        names = "ONEONE TWO THREE"
        result = list(name_query(names.split(), 'ONE'))
        self.assertFalse(result)

    def test_match_more_strings(self):
        names = "ONE_1 ONE_2 THREE"
        result = list(name_query(names.split(), 'ONE_.*'))
        self.assertEqual("ONE_1", result[0])
        self.assertEqual("ONE_2", result[1])
        self.assertEqual(2, len(result))


if __name__ == '__main__':
    unittest.main()
