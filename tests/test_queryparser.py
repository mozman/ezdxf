# encoding: utf-8
# Copyright (C) 2013, Manfred Moitzi
# License: MIT-License

import unittest

from ezdxf.queryparser import EntityQueryParser, ParseException

class TestEntityQueryParserWithoutAttributes(unittest.TestCase):
    def test_without_wildcards(self):
        result = EntityQueryParser.parseString("LINE", parseAll=True)
        self.assertEqual("LINE", result.EntityName)

    def test_star_wildcard(self):
        result = EntityQueryParser.parseString("*", parseAll=True)
        self.assertEqual("*", result.EntityName)

    def test_wrong_star_wildcard(self):
        with self.assertRaises(ParseException):
            EntityQueryParser.parseString("LIN*[]", parseAll=True)

class TestEntityQueryParserWithAttributes(unittest.TestCase):
    def test_empty_attribute_list_not_allowed(self):
        with self.assertRaises(ParseException):
            EntityQueryParser.parseString("LINE[]", parseAll=True)

    def test_one_attribute(self):
        result = EntityQueryParser.parseString('LINE[layer=="0"]', parseAll=True)
        self.assertEqual("LINE", result.EntityName)
        self.assertEqual(1, len(result.Attributes))
        name, relation, value = result.Attributes[0]
        self.assertEqual('layer', name)
        self.assertEqual('==', relation)
        self.assertEqual('0', value)

    def test_star_with_one_attribute(self):
        result = EntityQueryParser.parseString('*[layer=="0"]', parseAll=True)
        self.assertEqual("*", result.EntityName)
        self.assertEqual(1, len(result.Attributes))
        name, relation, value = result.Attributes[0]
        self.assertEqual('layer', name)
        self.assertEqual('==', relation)
        self.assertEqual('0', value)

    def test_second_attribute(self):
        result = EntityQueryParser.parseString('LINE[layer=="0" color!=7]', parseAll=True)
        name, relation, value = result.Attributes[1]
        self.assertEqual('color', name)
        self.assertEqual('!=', relation)
        self.assertEqual(7, value)

if __name__ == '__main__':
    unittest.main()
