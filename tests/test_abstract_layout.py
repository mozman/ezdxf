# Created: 28.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License

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


def test_build_entity():
    host = Host(range(10))
    entity = host.build_entity('TEST', {})
    assert 'TEST' == entity.dxf.handle
    assert host.paperspace == 1
