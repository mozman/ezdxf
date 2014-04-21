# encoding: utf-8
# Copyright (C) 2013, Manfred Moitzi
# License: MIT-License

import unittest

from ezdxf.queryparser import EntityQueryParser, ParseException, InfixBoolQuery


class TestEntityQueryParserWithoutAttributes(unittest.TestCase):
    def test_without_wildcards(self):
        result = EntityQueryParser.parseString("LINE", parseAll=True)
        name = result.EntityQuery[0]
        self.assertEqual("LINE", name)

    def test_two_entity_names(self):
        result = EntityQueryParser.parseString("LINE CIRCLE", parseAll=True)
        self.assertEqual("LINE", result.EntityQuery[0])
        self.assertEqual("CIRCLE", result.EntityQuery[1])

    def test_star_wildcard(self):
        result = EntityQueryParser.parseString("*", parseAll=True)
        name = result.EntityQuery[0]
        self.assertEqual("*", name)

    def test_wrong_star_wildcard(self):
        with self.assertRaises(ParseException):
            EntityQueryParser.parseString("LIN*[]", parseAll=True)

    def test_wrong_star_wildcard_2(self):
        with self.assertRaises(ParseException):
            EntityQueryParser.parseString("* LINE[]", parseAll=True)

    def test_wrong_star_wildcard_3(self):
        with self.assertRaises(ParseException):
            EntityQueryParser.parseString("LINE *[]", parseAll=True)


class TestEntityQueryParserWithAttributes(unittest.TestCase):
    def test_empty_attribute_list_not_allowed(self):
        with self.assertRaises(ParseException):
            EntityQueryParser.parseString("LINE[]", parseAll=True)

    def test_one_attribute(self):
        result = EntityQueryParser.parseString('LINE[layer=="0"]', parseAll=True)
        self.assertEqual("LINE", result.EntityQuery[0])
        self.assertEqual(('layer', '==', '0'), tuple(result.AttribQuery))

    def test_star_with_one_attribute(self):
        result = EntityQueryParser.parseString('*[layer=="0"]', parseAll=True)
        self.assertEqual("*", result.EntityQuery[0])
        self.assertEqual(3, len(result.AttribQuery))
        self.assertEqual(('layer', '==', '0'), tuple(result.AttribQuery))

    def test_relation_lt(self):
        result = EntityQueryParser.parseString('*[layer<"0"]', parseAll=True)
        self.assertEqual(('layer', '<', '0'), tuple(result.AttribQuery))

    def test_relation_le(self):
        result = EntityQueryParser.parseString('*[layer<="0"]', parseAll=True)
        self.assertEqual(('layer', '<=', '0'), tuple(result.AttribQuery))

    def test_relation_eq(self):
        result = EntityQueryParser.parseString('*[layer=="0"]', parseAll=True)
        self.assertEqual(('layer', '==', '0'), tuple(result.AttribQuery))

    def test_relation_ne(self):
        result = EntityQueryParser.parseString('*[layer!="0"]', parseAll=True)
        self.assertEqual(('layer', '!=', '0'), tuple(result.AttribQuery))

    def test_relation_ge(self):
        result = EntityQueryParser.parseString('*[layer>="0"]', parseAll=True)
        self.assertEqual(('layer', '>=', '0'), tuple(result.AttribQuery))

    def test_relation_gt(self):
        result = EntityQueryParser.parseString('*[layer>="0"]', parseAll=True)
        self.assertEqual(('layer', '>=', '0'), tuple(result.AttribQuery))

    def test_regex_match(self):
        result = EntityQueryParser.parseString('*[layer?"0"]', parseAll=True)
        self.assertEqual(('layer', '?', '0'), tuple(result.AttribQuery))

    def test_not_regex_match(self):
        result = EntityQueryParser.parseString('*[layer!?"0"]', parseAll=True)
        self.assertEqual(('layer', '!?', '0'), tuple(result.AttribQuery))

class TestInfixBoolQuery(unittest.TestCase):
    def test_not_operation(self):
        result = InfixBoolQuery.parseString('!a!=1', parseAll=True)
        op, relation = result.AttribQuery
        self.assertEqual('!', op)
        self.assertEqual(('a', '!=', 1), tuple(relation))

    def test_and_operation(self):
        result = InfixBoolQuery.parseString('a != 1 & b != 2', parseAll=True)
        rel1, op, rel2 = result.AttribQuery
        self.assertEqual(('a', '!=', 1), tuple(rel1))
        self.assertEqual('&', op)
        self.assertEqual(('b', '!=', 2), tuple(rel2))

    def test_or_operation(self):
        result = InfixBoolQuery.parseString('a != 1 | b != 2', parseAll=True)
        rel1, op, rel2 = result.AttribQuery
        self.assertEqual(('a', '!=', 1), tuple(rel1))
        self.assertEqual('|', op)
        self.assertEqual(('b', '!=', 2), tuple(rel2))

    def test_not_operation_with_brackets(self):
        result = InfixBoolQuery.parseString('!(a!=1)', parseAll=True)
        op, relation = result.AttribQuery
        self.assertEqual('!', op)
        self.assertEqual(('a', '!=', 1), tuple(relation))

    def test_operation_with_brackets(self):
        result = InfixBoolQuery.parseString('(a != 1) & (b != 2)', parseAll=True)
        rel1, op, rel2 = result.AttribQuery
        self.assertEqual(('a', '!=', 1), tuple(rel1))
        self.assertEqual('&', op)
        self.assertEqual(('b', '!=', 2), tuple(rel2))

    def test_operation_with_nested_brackets(self):
        result = InfixBoolQuery.parseString('((a != 1) & (b != 2))', parseAll=True)
        rel1, op, rel2 = result.AttribQuery
        self.assertEqual(('a', '!=', 1), tuple(rel1))
        self.assertEqual('&', op)
        self.assertEqual(('b', '!=', 2), tuple(rel2))


if __name__ == '__main__':
    unittest.main()
