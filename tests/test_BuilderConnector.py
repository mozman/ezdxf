#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test BuilderConnector
# Created: 28.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import sys
import unittest

from ezdxf.ac1009.gbuilder import BuilderConnector

class Entity:
    def __init__(self, handle):
        self.handle = handle

    def setbuilder(self, builder):
        pass

class DXFFactory:
    def wrap_handle(self, handle):
        return Entity(handle)

    def create_db_entry(self, name, attribs):
        return Entity(name)

class Host(BuilderConnector):
    def __init__(self, iterable):
        self._entityspace = list(iterable)
        self._dxffactory = DXFFactory()

    def _set_paperspace(self, entity):
        self.paperspace = True

    def _get_entity_by_handle(self, handle):
        entity = self._dxffactory.wrap_handle(handle)
        entity.setbuilder(self)
        return entity

class TestBuilderConnector(unittest.TestCase):
    def setUp(self):
        self.host = Host(range(10))

    def test_append_entity(self):
        self.host._append_entity(Entity(4711))
        self.assertEqual(4711, self.host._entityspace[-1])

    def test_insert_entities_begin(self):
        handles = [20, 21, 22, 23, 24]
        entities = [Entity(handle) for handle in handles]
        self.host._insert_entities(0, entities)
        self.assertEqual(handles, self.host._entityspace[:5])

    def test_insert_entities_mid(self):
        handles = [20, 21, 22, 23, 24]
        entities = [Entity(handle) for handle in handles]
        self.host._insert_entities(5, entities)
        self.assertEqual(handles, self.host._entityspace[5:10])

    def test_insert_entities_end(self):
        handles = [20, 21, 22, 23, 24]
        entities = [Entity(handle) for handle in handles]
        self.host._insert_entities(15, entities)
        self.assertEqual(handles, self.host._entityspace[-5:])

    def test_get_position(self):
        pos = self.host._get_index(Entity(5))
        self.assertEqual(5, pos)

    def test_remove_entities_begin(self):
        self.host._remove_entities(0, 3)
        self.assertEqual([3, 4, 5, 6, 7, 8, 9], self.host._entityspace)

    def test_remove_entities_mid(self):
        self.host._remove_entities(5, 3)
        self.assertEqual([0, 1, 2, 3, 4, 8, 9], self.host._entityspace)

    def test_remove_entities_end(self):
        self.host._remove_entities(8, 3)
        self.assertEqual([0, 1, 2, 3, 4, 5, 6, 7], self.host._entityspace)

    def test_get_entity(self):
        entity = self.host._get_entity_at_index(7)
        self.assertEqual(7, entity.handle)

    def test_build_entity(self):
        entity = self.host._build_entity('TEST', {})
        self.assertEqual('TEST', entity.handle)
        self.assertTrue(self.host.paperspace)

if __name__=='__main__':
    unittest.main()