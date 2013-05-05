# encoding: utf-8
# Purpose: Query language and manipulation object for DXF entities
# Created: 27.04.13
# Copyright (C) 2013, Manfred Moitzi
# License: MIT License
# Python2/3 support should be done here

import re
import operator

from .queryparser import EntityQueryParser

class EntityQuery(object):
    def __init__(self, entities, query='*'):
        match = entity_matcher(query)
        self.entities = [entity for entity in entities if match(entity)]

    def __len__(self):
        return len(self.entities)

    def __iter__(self):
        return iter(self.entities)

    def extend(self, entities, query='*'):
        match = entity_matcher(query)
        self.entities.extend(entity for entity in entities if match(entity))
        self.entities = list(unique_entities(entities))

    def remove(self, query='*'):
        match = entity_matcher(query)
        self.entities = [entity for entity in self.entities if not match(entity)]

    def filter(self, query='*'):
        return EntityQuery(self.entities, query)

def entity_matcher(query):
    query_args = EntityQueryParser.parseString(query, parseAll=True)
    entity_matcher = build_entity_name_matcher(query_args.EntityNames)
    attrib_matcher = build_entity_attributes_matcher(query_args.Attributes)
    def matcher(entity):
        return entity_matcher(entity) and attrib_matcher(entity)
    return matcher

def build_entity_name_matcher(names):
    entity_names = set(names)
    def match_one_name(entity):
        if entity.dxftype() in entity_names:
            return True
        else:
            return False

    if names[0] == '*':
        return lambda x: True
    else:
        return match_one_name

def build_entity_attributes_matcher(attribs):
    def build_compare(relation, value):
        relation_operator = operator.eq if relation == '==' else operator.ne
        def build_regexp_compare():
            # always match until end of string
            regexp = re.compile(value + '$')
            def compare(v):
                return relation_operator(regexp.match(v) is not None, True)
            return compare

        if isinstance(value, (int, float)): # just compare values
            return lambda v: relation_operator(v, value)
        else: # for strings use regular expressions
            return build_regexp_compare()

    if not len(attribs):
        return lambda x: True

    attributes = [ (name, build_compare(relation, value)) for name, relation, value in attribs ]
    def match_all_attributes(entity):
        def match(name, compare):
            try:
                return compare(entity.get_dxf_attrib(name))
            except AttributeError:  # entity does not support this attribute
                return False
            except ValueError: # entity support this attribute, but has no value for it
                return False
        return all(match(name, compare) for name, compare in attributes)
    return match_all_attributes

def unique_entities(entities):
    handles = set()
    for entity in entities:
        handle = entity.handle()
        if handle not in handles:
            handles.add(handle)
            yield entity
