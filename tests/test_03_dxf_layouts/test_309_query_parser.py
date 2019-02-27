# Copyright (c) 2013-2019, Manfred Moitzi
# License: MIT-License
import pytest

from ezdxf.queryparser import EntityQueryParser, ParseException, InfixBoolQuery


class TestEntityQueryParserWithoutAttributes:
    def test_without_wildcards(self):
        result = EntityQueryParser.parseString("LINE", parseAll=True)
        name = result.EntityQuery[0]
        assert "LINE" == name

    def test_two_entity_names(self):
        result = EntityQueryParser.parseString("LINE CIRCLE", parseAll=True)
        assert "LINE" == result.EntityQuery[0]
        assert "CIRCLE" == result.EntityQuery[1]

    def test_star_wildcard(self):
        result = EntityQueryParser.parseString("*", parseAll=True)
        name = result.EntityQuery[0]
        assert "*" == name

    def test_wrong_star_wildcard(self):
        with pytest.raises(ParseException):
            EntityQueryParser.parseString("LIN*[]", parseAll=True)

    def test_wrong_star_wildcard_2(self):
        with pytest.raises(ParseException):
            EntityQueryParser.parseString("* LINE[]", parseAll=True)

    def test_wrong_star_wildcard_3(self):
        with pytest.raises(ParseException):
            EntityQueryParser.parseString("LINE *[]", parseAll=True)


class TestEntityQueryParserWithAttributes:
    def test_empty_attribute_list_not_allowed(self):
        with pytest.raises(ParseException):
            EntityQueryParser.parseString("LINE[]", parseAll=True)

    def test_one_attribute(self):
        result = EntityQueryParser.parseString('LINE[layer=="0"]', parseAll=True)
        assert "LINE" == result.EntityQuery[0]
        assert ('layer', '==', '0') == tuple(result.AttribQuery)

    def test_double_quoted_attributes(self):
        result = EntityQueryParser.parseString('LINE[layer=="0"]', parseAll=True)
        assert "LINE" == result.EntityQuery[0]
        assert ('layer', '==', '0') == tuple(result.AttribQuery)

    def test_single_quoted_attributes(self):
        result = EntityQueryParser.parseString("LINE[layer=='0']", parseAll=True)
        assert "LINE" == result.EntityQuery[0]
        assert ('layer', '==', '0') == tuple(result.AttribQuery)

    def test_attribute_name_with_underscore(self):
        result = EntityQueryParser.parseString('HATCH[solid_fill==0]', parseAll=True)
        assert "HATCH" == result.EntityQuery[0]
        assert ('solid_fill', '==', 0) == tuple(result.AttribQuery)

    def test_star_with_one_attribute(self):
        result = EntityQueryParser.parseString('*[layer=="0"]', parseAll=True)
        assert "*" == result.EntityQuery[0]
        assert 3 == len(result.AttribQuery)
        assert ('layer', '==', '0') == tuple(result.AttribQuery)

    def test_relation_lt(self):
        result = EntityQueryParser.parseString('*[layer<"0"]', parseAll=True)
        assert ('layer', '<', '0') == tuple(result.AttribQuery)

    def test_relation_le(self):
        result = EntityQueryParser.parseString('*[layer<="0"]', parseAll=True)
        assert ('layer', '<=', '0') == tuple(result.AttribQuery)

    def test_relation_eq(self):
        result = EntityQueryParser.parseString('*[layer=="0"]', parseAll=True)
        assert ('layer', '==', '0') == tuple(result.AttribQuery)

    def test_relation_ne(self):
        result = EntityQueryParser.parseString('*[layer!="0"]', parseAll=True)
        assert ('layer', '!=', '0') == tuple(result.AttribQuery)

    def test_relation_ge(self):
        result = EntityQueryParser.parseString('*[layer>="0"]', parseAll=True)
        assert ('layer', '>=', '0') == tuple(result.AttribQuery)

    def test_relation_gt(self):
        result = EntityQueryParser.parseString('*[layer>="0"]', parseAll=True)
        assert ('layer', '>=', '0') == tuple(result.AttribQuery)

    def test_regex_match(self):
        result = EntityQueryParser.parseString('*[layer?"0"]', parseAll=True)
        assert ('layer', '?', '0') == tuple(result.AttribQuery)

    def test_not_regex_match(self):
        result = EntityQueryParser.parseString('*[layer!?"0"]', parseAll=True)
        assert ('layer', '!?', '0') == tuple(result.AttribQuery)

    def test_appended_ignore_case_option(self):
        result = EntityQueryParser.parseString('*[layer=="IgnoreCase"]i', parseAll=True)
        assert "i" == result.AttribQueryOptions


class TestInfixBoolQuery:
    def test_not_operation(self):
        result = InfixBoolQuery.parseString('!a!=1', parseAll=True)
        op, relation = result.AttribQuery
        assert '!' == op
        assert ('a', '!=', 1) == tuple(relation)

    def test_and_operation(self):
        result = InfixBoolQuery.parseString('a != 1 & b != 2', parseAll=True)
        rel1, op, rel2 = result.AttribQuery
        assert ('a', '!=', 1) == tuple(rel1)
        assert '&' == op
        assert ('b', '!=', 2) == tuple(rel2)

    def test_or_operation(self):
        result = InfixBoolQuery.parseString('a != 1 | b != 2', parseAll=True)
        rel1, op, rel2 = result.AttribQuery
        assert ('a', '!=', 1) == tuple(rel1)
        assert '|' == op
        assert ('b', '!=', 2) == tuple(rel2)

    def test_not_operation_with_brackets(self):
        result = InfixBoolQuery.parseString('!(a!=1)', parseAll=True)
        op, relation = result.AttribQuery
        assert '!' == op
        assert ('a', '!=', 1) == tuple(relation)

    def test_operation_with_brackets(self):
        result = InfixBoolQuery.parseString('(a != 1) & (b != 2)', parseAll=True)
        rel1, op, rel2 = result.AttribQuery
        assert ('a', '!=', 1) == tuple(rel1)
        assert '&' == op
        assert ('b', '!=', 2) == tuple(rel2)

    def test_operation_with_nested_brackets(self):
        result = InfixBoolQuery.parseString('((a != 1) & (b != 2))', parseAll=True)
        rel1, op, rel2 = result.AttribQuery
        assert ('a', '!=', 1) == tuple(rel1)
        assert '&' == op
        assert ('b', '!=', 2) == tuple(rel2)


