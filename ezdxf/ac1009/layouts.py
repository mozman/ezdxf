#!/usr/bin/env python
#coding:utf-8
# Purpose: AC1009 layout manager
# Created: 21.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .gbuilder import AC1009GraphicBuilder
from ..entityspace import EntitySpace


class AC1009Layouts(object):
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


class AC1009Layout(AC1009GraphicBuilder):
    """ Layout representation

    provides: IBuilderConnector
    provides: IGraphicBuilder
    """
    def __init__(self, entityspace, dxffactory, paperspace=0):
        self._entityspace = entityspace  # where all the entities go ...
        self._dxffactory = dxffactory
        self._paperspace = paperspace

    # start of public interface

    def __iter__(self):
        for entity in self._iter_all_entities():
            if entity.get_dxf_attrib('paperspace', 0) == self._paperspace:
                yield entity

    def __contains__(self, entity):
        if isinstance(entity, str):  # handle
            entity = self._dxffactory.wrap_handle(entity)
        if entity.get_dxf_attrib('paperspace', 0) == self._paperspace:
            return True
        else:
            return False

    # end of public interface

    def _iter_all_entities(self):
        for handle in self._entityspace:
            yield self._get_entity_by_handle(handle)

    def _get_entity_by_handle(self, handle):
        entity = self._dxffactory.wrap_handle(handle)
        entity.set_builder(self)
        return entity

    def _set_paperspace(self, entity):
        entity.dxf.paperspace = self._paperspace


class AC1009BlockLayout(AC1009GraphicBuilder):
    """ BlockLayout has the same factory-function as Layout, but is managed
    in the BlocksSection() class. It represents a DXF Block definition.

    _head db handle to BLOCK entiy
    _tail db handle to ENDBLK entiy
    _entityspace is the block content

    implements: IBuilderConnector

    """
    def __init__(self, entitydb, dxffactory, block_handle, endblk_handle):
        self._entityspace = EntitySpace(entitydb)
        self._dxffactory = dxffactory
        self._block_handle = block_handle
        self._endblk_handle = endblk_handle

    # start of public interface

    def __iter__(self):
        for handle in self._entityspace:
            yield self._dxffactory.wrap_handle(handle)

    def __contains__(self, entity):
        try:
            handle = entity.handle
        except AttributeError:
            handle = entity
        try:
            index = self._entityspace.index(handle)
            return True
        except IndexError:
            return False

    @property
    def block(self):
        return self._dxffactory.wrap_handle(self._block_handle)

    @property
    def name(self):
        return self.block.dxf.name

    def add_attdef(self, tag, insert, dxfattribs={}):
        dxfattribs['tag'] = tag
        dxfattribs['insert'] = insert
        return self._create('ATTDEF', dxfattribs)

    # end of public interface

    def _set_paperspace(self, entity):
        pass

    def _get_entity_by_handle(self, handle):
        entity = self._dxffactory.wrap_handle(handle)
        entity.set_builder(self)
        return entity

    def add_entity(self, entity):
        self._entityspace.add(entity)

    def write(self, stream):
        def write_tags(handle):
            wrapper = self._dxffactory.wrap_handle(handle)
            wrapper.tags.write(stream)

        write_tags(self._block_handle)
        self._entityspace.write(stream)
        write_tags(self._endblk_handle)

    def attdefs(self):
        for entity in self:
            if entity.dxftype() == 'ATTDEF':
                yield entity
