#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: AC1009 layout manager
# Created: 21.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

# The ModelSpace is a special Layout called '$MODEL_SPACE'

from ..entity import GenericWrapper

class AC1009Layouts:
    def __init__(self, drawing):
        self._layouts = {}
        self._drawing = drawing
        self._setup()

    def _setup(self):
        workspace = self._drawing.sections.entities
        factory = self._drawing.dxffactory
        self._layouts['$MODEL_SPACE'] = AC1009ModelSpaceLayout(workspace, factory)
        self._layouts['$PAPER_SPACE'] = AC1009PaperSpaceLayout(workspace, factory)

    def __contains__(self, name):
        return name in self._layouts

    def create(self, name):
        raise NotImplementedError('DXF AC1009 (R12) allows only one paperspace')

    def get(self, name):
        return self._layouts[name]

    def rename(self, oldname, newname):
        raise NotImplementedError('DXF AC1009 (R12) layouts cannot renamed.')

    def remove(self, name):
        raise NotImplementedError('DXF AC1009 (R12) layouts cannot removed.')

class AC1009ModelSpaceLayout:
    def __init__(self, workspace, dxffactory):
        self._workspace = workspace
        self._dxffactory = dxffactory

    def add_line(self, start, end, attribs={}):
        def update_attribs():
            self._set_paper_space(attribs)
            attribs['start'] = start
            attribs['end'] = end

        update_attribs()
        entity = self._build_entity('LINE', attribs)
        self._add_entity(entity)
        return entity

    def _build_entity(self, type_, attribs):
        return self._dxffactory.create_db_entry(type_, attribs)

    def _add_entity(self, entity):
        self._workspace.add(entity)

    def _set_paper_space(self, attribs):
        # entities are in modelspace by default
        pass


class AC1009PaperSpaceLayout(AC1009ModelSpaceLayout):
    def _set_paper_space(self, attribs):
        attribs['paperspace'] = 1

