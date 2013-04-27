# encoding: utf-8
# Purpose: Query language and manipulation object for DXF entities
# Created: 27.04.13
# Copyright (C) 2013, Manfred Moitzi
# License: MIT License

class EntityQuery(object):
    # Important: order of entities has to be preserved (POLYLINE, VERTEX, ..., SEQEND)
    def __init__(self, entities, query='*'):
        match = build_query_matcher(query)
        self.entities = [entity for entity in entities if match(entity)]

    def __iter__(self):
        return iter(self.entities)

    def extend(self, entities, query='*'):
        match = build_query_matcher(query)
        self.entities.extend(entity for entity in entities if match(entity))
        self.entities = list(unique_entities(entities))

    def remove(self, query='*'):
        match = build_query_matcher(query)
        self.entities = [entity for entity in self.entities if not match(entity)]

    def filter(self, query='*'):
        return EntityQuery(self.entities, query)

class SimpleNameMatcher(object):
    def __init__(self, name):
        self.name = name
        self.match_until_seqend = False

    def __call__(self, entity):
        if self.match_until_seqend:
            if entity.dxftype() == 'SEQEND':
                self.match_until_seqend = False
            return True
        if self.name == entity.dxftype():
            if entity.dxftype() in ('POLYLINE', 'INSERT'):
                self.match_until_seqend = True
            return True
        return False

def build_query_matcher(query):
    query = query.upper().strip()
    if query == '*':
        return lambda e: True
    return SimpleNameMatcher(query)

def unique_entities(entities):
    handles = set()
    for entity in entities:
        handle = entity.handle()
        if handle not in handles:
            handles.add(handle)
            yield entity
