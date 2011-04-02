#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: AC1009 layout manager
# Created: 21.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from .gbuilder import AC1009GraphicBuilder, BuilderConnector
from ..entityspace import EntitySpace

class AC1009Layouts:
    def __init__(self, drawing):
        entityspace = drawing.sections.entities.get_entityspace()
        self._modelspace = AC1009Layout(entityspace, drawing.dxffactory, 0)
        self._paperspace = AC1009Layout(entityspace, drawing.dxffactory, 1)

    def modelspace(self):
        return self._modelspace

    def get(self, name):
        # AC1009 supports only one paperspace/layout
        return self._paperspace

    def names(self):
        return []

class AC1009Layout(AC1009GraphicBuilder, BuilderConnector):
    """ Layout representation

    provides: IBuilderConnector
    provides: IGraphicBuilder
    """
    def __init__(self, entityspace, dxffactory, paperspace=0):
        self._entityspace = entityspace # where all the entities go ...
        self._dxffactory = dxffactory
        self._paperspace = paperspace

    # start of public interface

    def __iter__(self):
        for entity in self._iter_all_entities():
            if entity.getdxfattr('paperspace', 0) == self._paperspace:
                yield entity

    def __contains__(self, entity):
        if isinstance(entity, str): # handle
            entity = self._dxffactory.wrap_handle(entity)
        if entity.getdxfattr('paperspace', 0) == self._paperspace:
            return True
        else:
            return False

    # end of public interface

    def _iter_all_entities(self):
        for handle in self._entityspace:
            yield self._dxffactory.wrap_handle(handle)

    def _set_paperspace(self, entity):
        # part of IBuilderConnector
        entity.paperspace = self._paperspace

class AC1009BlockLayout(AC1009GraphicBuilder, BuilderConnector):
    """ BlockLayout has the same factory-function as Layout, but is managed
    in the BlocksSection() class. It represents a DXF Block definition.

    _head db handle to BLOCK entiy
    _tail db handle to ENDBLK entiy
    _entityspace is the block content

    implements: IBuilderConnector

    """
    def __init__(self, entitydb, dxffactory):
        self._entityspace = EntitySpace(entitydb)
        self._dxffactory = dxffactory
        self._head = None
        self._tail = None

    # start of public interface

    def __iter__(self):
        for handle in self._entityspace:
            yield self._dxffactory.wrap_handle(handle)

    @property
    def name(self):
        block = self._dxffactory.wrap_handle(self._head)
        return block.name

    # end of public interface

    def _set_paperspace(self, entity):
        pass

    def set_head(self, handle):
        self._head = handle

    def set_tail(self, handle):
        self._tail = handle

    def add_entity(self, entity):
        self._entityspace.add(entity)

    def write(self, stream):
        def write_tags(handle):
            wrapper = self._dxffactory.wrap_handle(handle)
            wrapper.tags.write(stream)

        write_tags(self._head)
        self._entityspace.write(stream)
        write_tags(self._tail)

