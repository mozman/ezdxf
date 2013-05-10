# encoding: utf-8
# Purpose: Query language and manipulation object for DXF entities
# Created: 27.04.13
# Copyright (C) 2013, Manfred Moitzi
# License: MIT License

import re
import operator

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

#TODO: boolean operation parser, see pyparsing example: simpleBool.py

CMP_OPERATOR = {
    '==': operator.eq,
    '!=': operator.ne,
    '<': operator.lt,
    '<=': operator.le,
    '>': operator.gt,
    '>=': operator.ge,
    '?': lambda e, regex: regex.match(e) is not None,
    '!?': lambda e, regex: regex.match(e) is None,
}

def entity_matcher(query):
    query_args = EntityQueryParser.parseString(query, parseAll=True)
    entity_matcher = build_entity_name_matcher(query_args.EntityNames)
    attrib_matcher = build_entity_attributes_matcher(query_args.Attributes)
    def matcher(entity):
        return entity_matcher(entity) and attrib_matcher(entity)
    return matcher

def build_entity_name_matcher(names):
    entity_names = set(names)
    if names[0] == '*':
        return lambda e: True
    else:
        return lambda e: e.dxftype() in entity_names

def build_entity_attributes_matcher(attribs):
    def build_compare(relation, value):
        if '?' in relation :
            value =  re.compile(value + '$')
        return lambda v: CMP_OPERATOR[relation](v, value)

    if not len(attribs):
        return lambda x: True

    attributes = [ (name, build_compare(relation, value)) for name, relation, value in attribs ]
    def match_all_attributes(entity):
        def match(name, compare):
            try:
                return compare(entity.get_dxf_attrib(name))
            except AttributeError:  # entity does not support this attribute
                return False
            except ValueError: # entity supports this attribute, but has no value for it
                return False
        return all(match(name, compare) for name, compare in attributes)
    return match_all_attributes

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

