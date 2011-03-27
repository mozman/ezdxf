#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: AC1009 layout manager
# Created: 21.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from .gbuilder import AC1009GraphicBuilder

class AC1009Layouts:
    def __init__(self, drawing):
        workspace = drawing.sections.entities.workspace
        self._modelspace = AC1009ModelSpaceLayout(workspace, drawing.dxffactory)
        self._paperspace = AC1009PaperSpaceLayout(workspace, drawing.dxffactory)

    def modelspace(self):
        return self._modelspace

    def get(self, name):
        # AC1009 supports only one paperspace/layout
        return self._paperspace

    def names(self):
        return []

class AC1009ModelSpaceLayout(AC1009GraphicBuilder):
    def __init__(self, workspace, dxffactory):
        self._workspace = workspace # where all the entities go ...
        self._dxffactory = dxffactory

    def _set_paper_space(self, attribs):
        pass

    # start of interface for GraphicBuilder

    def _build_entity(self, type_, attribs):
        self._set_paper_space(attribs)
        return self._dxffactory.create_db_entry(type_, attribs)

    def _append_entity(self, entity):
        self._workspace.add(entity)

    def _get_position(self, entity):
        return self._workspace.index(entity.handle)

    def _get_entity(self, pos):
        handle = self._workspace[pos]
        return self._dxffactory.wrap_handle(handle)

    def _insert_entity(self, pos, entity):
        self._workspace.insert(pos, entity.handle)

    def _remove_entity(self, entity):
        self._workspace.remove(entity.handle)

    # end of interface for GraphicBuilder

class AC1009PaperSpaceLayout(AC1009ModelSpaceLayout):
    def _set_paper_space(self, attribs):
        attribs['paperspace'] = 1

