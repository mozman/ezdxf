# encoding: utf-8
# Purpose: Query language and manipulation object for DXF entities
# Created: 27.04.13
# Copyright (C) 2013, Manfred Moitzi
# License: MIT License

import re
import operator
import sys

from .queryparser import EntityQueryParser

class EntityQuery(object):
    def __init__(self, entities, query='*'):
        match = entity_matcher(query)
        self.entities = [entity for entity in entities if match(entity)]

    def __len__(self):
        """ Count of result entities.
        """
        return len(self.entities)

    def __iter__(self):
        """ Iterate over all entities matching the init-query, returns a GraphicEntity() class or inherited.
        """
        return iter(self.entities)

    def extend(self, entities, query='*', unique=True):
        """ Extent query result by entities matching query.
        """
        self.entities.extend(EntityQuery(entities, query))
        if unique:
            self.entities = list(unique_entities(self.entities))
        return self

    def remove(self, query='*'):
        """ Remove entities matching this additional query from previous query result.
        """
        self.entities = self.filter(query).entities

    def filter(self, query='*'):
        """ Returns a new query result with all entities matching previous query AND this additional query.
        """
        return EntityQuery(self.entities, query)


def entity_matcher(query):
    query_args = EntityQueryParser.parseString(query, parseAll=True)
    entity_matcher = build_entity_name_matcher(query_args.EntityQuery)
    attrib_matcher = build_entity_attributes_matcher(query_args.AttribQuery)
    def matcher(entity):
        return entity_matcher(entity) and attrib_matcher(entity)
    return matcher

def build_entity_name_matcher(names):
    entity_names = set(names)
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

    def __init__(self, relation):
        name, op, value = relation
        self.dxf_attrib = name
        self.compare = Relation.CMP_OPERATORS[op]
        if '?' in op:
            self.value = re.compile(value + '$') # always match whole pattern
        else:
            self.value = value

    def evaluate(self, entity):
        try:
            return self.compare(entity.get_dxf_attrib(self.dxf_attrib), self.value)
        except AttributeError:  # entity does not support this attribute
            return False
        except ValueError:  # entity supports this attribute, but has no value for it
            return False


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

        values = []  # as stack
        operators = []  # as queue
        for token in self.tokens:
            if hasattr(token, 'evaluate'):
                values.append(token.evaluate(entity))
            else:  # bool operator
                operators.append(token)
        values.reverse()  # revert stack -> so pop() and append() operates at the beginning of the list
        for op in operators:  # as queue -> empty list from start to end
            if op == '!':
                value = not values.pop()
            else:
                value = BoolExpression.OPERATORS[op](values.pop(), values.pop())
            values.append(value)
        return values.pop()

if sys.version_info.major > 2:
    basestring = str

def _build_tokens(tokens):
    def is_relation(tokens):
        return len(tokens) == 3 and tokens[1] in Relation.VALID_CMP_OPERATORS

    if isinstance(tokens, basestring):  # bool operator as string
        return tokens

    tokens = tuple(tokens)
    if is_relation(tokens):
        return Relation(tokens)
    else:
        return BoolExpression([_build_tokens(token) for token in tokens])

def build_entity_attributes_matcher(parsed_tokens):
    if not len(parsed_tokens):
        return lambda x: True

    expr = BoolExpression(_build_tokens(parsed_tokens))
    def match_bool_expr(entity):
        return expr.evaluate(entity)
    return match_bool_expr

def unique_entities(entities):
    """ Yield all unique entities, order of all entities will be preserved, because of these entities:
    POLYLINE, VERTEX, ..., VERTEX, SEQEND.
    INSERT, ATTRIB, ..., ATTRIB, SEQEND.
    """
    handles = set()
    for entity in entities:
        handle = entity.handle()
        if handle not in handles:
            handles.add(handle)
            yield entity

def name_query(names, query="*"):
    def build_regexp_matcher():
        def get_match_func():
            # always match until end of string
            matcher = re.compile(query + '$')
            def match(name):
                return matcher.match(name) is not None
            return match
        if query == "*":
            return lambda n: True
        else:
            return get_match_func()
    match = build_regexp_matcher()
    return (name for name in names if match(name))
