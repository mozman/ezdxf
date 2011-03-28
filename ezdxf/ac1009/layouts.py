#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: AC1009 layout manager
# Created: 21.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from .gbuilder import AC1009GraphicBuilder, BuilderConnector

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
