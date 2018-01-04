# Purpose: Query language and manipulation object for DXF entities
# Created: 27.04.13
# Copyright (C) 2013, Manfred Moitzi
# License: MIT License

import re
import operator

from .tools.c23 import isstring, Sequence
from .queryparser import EntityQueryParser
from .groupby import groupby


class EntityQuery(Sequence):
    """EntityQuery is a result container, which is filled with dxf entities matching the query string.
    It is possible to add entities to the container (extend), remove entities from the container and
    to filter the container.

    Query String
    ============

    QueryString := EntityQuery ("[" AttribQuery "]")*

    The query string is the combination of two queries, first the required entity query and second the
    optional attribute query, enclosed in square brackets.

    Entity Query
    ------------

    The entity query is a whitespace separated list of DXF entity names or the special name ``*``.
    Where ``*`` means all DXF entities, all other DXF names have to be uppercase.

    Attribute Query
    ---------------

    The attribute query is used to select DXF entities by its DXF attributes. The attribute query is an addition to the
    entity query and matches only if the entity already match the entity query.
    The attribute query is a boolean expression, supported operators are:
      - not: !term is true, if term is false
      - and: term & term is true, if both terms are true
      - or: term | term is true, if one term is true
      - and arbitrary nested round brackets

    Attribute selection is a term: "name comparator value", where name is a DXF entity attribute in lowercase,
    value is a integer, float or double quoted string, valid comparators are:
      - "==" equal "value"
      - "!=" not equal "value"
      - "<" lower than "value"
      - "<=" lower or equal than "value"
      - ">" greater than "value"
      - ">=" greater or equal than "value"
      - "?" match regular expression "value"
      - "!?" does not match regular expression "value"

    Query Result
    ------------

    The EntityQuery() class based on the abstract Sequence() class, contains all DXF entities of the source collection,
    which matches one name of the entity query AND the whole attribute query.
    If a DXF entity does not have or support a required attribute, the corresponding attribute search term is false.
    example: 'LINE[text ? ".*"]' is always empty, because the LINE entity has no text attribute.

    examples:
        'LINE CIRCLE[layer=="construction"]' => all LINE and CIRCLE entities on layer "construction"
        '*[!(layer=="construction" & color<7)]' => all entities except those on layer == "construction" and color < 7
    """

    def __init__(self, entities, query='*'):
        """
        Setup container with entities matching the initial query.

        Args:
            entities: sequence of wrapped DXF entities (at least GraphicEntity class)
            query: query string, see class documentation
        """
        if query == '*':
            self.entities = list(entities)
        else:
            match = entity_matcher(query)
            self.entities = [entity for entity in entities if match(entity)]

    def __len__(self):
        """
        Count of result entities.
        """
        return len(self.entities)

    def __getitem__(self, item):
        return self.entities.__getitem__(item)

    def extend(self, entities, query='*', unique=True):
        """
        Extent the query container by entities matching a additional query.
        """
        self.entities.extend(EntityQuery(entities, query))
        if unique:
            self.entities = list(unique_entities(self.entities))
        return self

    def remove(self, query='*'):
        """
        Remove all entities from result container matching this additional query.
        """
        handles_of_entities_to_remove = frozenset(entity.dxf.handle for entity in self.query(query))
        self.entities = [entity for entity in self.entities if entity.dxf.handle not in handles_of_entities_to_remove]

    def query(self, query='*'):
        """
        Returns a new result container with all entities matching this additional query.

        raises: ParseException (pyparsing.py)
        """
        return EntityQuery(self.entities, query)

    def groupby(self, dxfattrib='', key=None):
        """
        Returns a dict of entity lists, where entities are grouped by a dxfattrib or a key function.

        Args:
            dxfattrib: grouping DXF attribute like 'layer'
            key: key function, which accepts a DXFEntity as argument, returns grouping key of this entity or None for
            ignore this object. Reason for ignoring: a queried DXF attribute is not supported by this entity

        Returns:
            dict
        """
        return groupby(self.entities, dxfattrib, key)


def entity_matcher(query):
    query_args = EntityQueryParser.parseString(query, parseAll=True)
    entity_matcher_ = build_entity_name_matcher(query_args.EntityQuery)
    attrib_matcher = build_entity_attributes_matcher(query_args.AttribQuery, query_args.AttribQueryOptions)

    def matcher(entity):
        return entity_matcher_(entity) and attrib_matcher(entity)

    return matcher


def build_entity_name_matcher(names):
    entity_names = frozenset(names)
    if names[0] == '*':
        return lambda e: True
    else:
        return lambda e: e.dxftype() in entity_names


class Relation:
    CMP_OPERATORS = {
        '==': operator.eq,
        '!=': operator.ne,
        '<': operator.lt,
        '<=': operator.le,
        '>': operator.gt,
        '>=': operator.ge,
        '?': lambda e, regex: regex.match(e) is not None,
        '!?': lambda e, regex: regex.match(e) is None,
    }
    VALID_CMP_OPERATORS = frozenset(CMP_OPERATORS.keys())

    def __init__(self, relation, ignore_case):
        name, op, value = relation
        self.dxf_attrib = name
        self.compare = Relation.CMP_OPERATORS[op]
        self.convert_case = to_lower if ignore_case else lambda x: x

        re_flags = re.IGNORECASE if ignore_case else 0
        if '?' in op:
            self.value = re.compile(value + '$', flags=re_flags)  # always match whole pattern
        else:
            self.value = self.convert_case(value)

    def evaluate(self, entity):
        try:
            value = self.convert_case(entity.get_dxf_attrib(self.dxf_attrib))
            return self.compare(value, self.value)
        except AttributeError:  # entity does not support this attribute
            return False
        except ValueError:  # entity supports this attribute, but has no value for it
            return False


def to_lower(value):
    return value.lower() if hasattr(value, 'lower') else value


class BoolExpression:
    OPERATORS = {
        '&': operator.and_,
        '|': operator.or_,
    }

    def __init__(self, tokens):
        self.tokens = tokens

    def __iter__(self):
        return iter(self.tokens)

    def evaluate(self, entity):
        if isinstance(self.tokens, Relation):  # expression is just one relation, no bool operations
            return self.tokens.evaluate(entity)

        values = []  # first in, first out
        operators = []  # first in, first out
        for token in self.tokens:
            if hasattr(token, 'evaluate'):
                values.append(token.evaluate(entity))
            else:  # bool operator
                operators.append(token)
        values.reverse()  # revert values -> pop() == pop(0) & append(value) == insert(0, value)
        for op in operators:  # as queue -> first in, first out
            if op == '!':
                value = not values.pop()
            else:
                value = BoolExpression.OPERATORS[op](values.pop(), values.pop())
            values.append(value)
        return values.pop()


def _compile_tokens(tokens, ignore_case):
    def is_relation(tokens):
        return len(tokens) == 3 and tokens[1] in Relation.VALID_CMP_OPERATORS

    if isstring(tokens):  # bool operator as string
        return tokens

    tokens = tuple(tokens)
    if is_relation(tokens):
        return Relation(tokens, ignore_case)
    else:
        return BoolExpression([_compile_tokens(token, ignore_case) for token in tokens])


def build_entity_attributes_matcher(tokens, options):
    if not len(tokens):
        return lambda x: True
    ignore_case = 'i' == options  # at this time just one option is supported
    expr = BoolExpression(_compile_tokens(tokens, ignore_case))

    def match_bool_expr(entity):
        return expr.evaluate(entity)

    return match_bool_expr


def unique_entities(entities):
    """
    Yield all unique entities, order of all entities will be preserved.
    """
    handles = set()
    for entity in entities:
        handle = entity.dxf.handle
        if handle not in handles:
            handles.add(handle)
            yield entity


def name_query(names, query="*"):
    def build_regexp_matcher():
        if query == "*":
            return lambda n: True
        else:
            # always match until end of string
            matcher = re.compile(query + '$')
            return lambda n: matcher.match(n) is not None

    match = build_regexp_matcher()
    return (name for name in names if match(name))


def new(entities=None, query='*'):
    if entities is None:
        entities = []
    return EntityQuery(entities, query)
