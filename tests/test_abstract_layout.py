#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test BuilderConnector
# Created: 28.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License

from __future__ import unicode_literals

import unittest

from ezdxf.legacy.layouts import BaseLayout


class DXFNameSpace:
    def __init__(self, handle):
        self.handle = handle


class Entity:
    def __init__(self, handle):
        self.dxf = DXFNameSpace(handle)
        self._handle = handle

    def set_builder(self, builder):
        pass


class DXFFactory:
    def wrap_handle(self, handle):
        return Entity(handle)

    def create_db_entry(self, name, dxfattribs):
        return Entity(name)


class Host(BaseLayout):
    def __init__(self, iterable):
        self._entityspace = list(iterable)
        self._dxffactory = DXFFactory()

    def _set_paperspace(self, entity):
        self.paperspace = True

    def get_entity_by_handle(self, handle):
        entity = self._dxffactory.wrap_handle(handle)
        entity.set_builder(self)
        return entity


class TestAbstractLayout(unittest.TestCase):
    def setUp(self):
        self.host = Host(range(10))

    def test_build_entity(self):
        entity = self.host.build_entity('TEST', {})
        self.assertEqual('TEST', entity.dxf.handle)
        self.assertTrue(self.host.paperspace)


if __name__ == '__main__':
    unittest.main()