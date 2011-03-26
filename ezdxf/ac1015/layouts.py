#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: AC1009 layout manager
# Created: 21.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

# The ModelSpace is a special Layout called '$MODEL_SPACE'

from .graphics import AC1015GraphicsBuilder

class AC1015Layouts:
    def __init__(self, drawing):
        self._layouts = {}
        self._layout_table = None
        self._setup(drawing)

    def _setup(self, drawing):
        dxffactory = drawing.dxffactory
        layout_table_handle = drawing.rootdict['ACAD_LAYOUT']
        self._layout_table = dxffactory.wrap_handle(layout_table_handle)
        for name, handle in self._layout_table.items():
            self._layouts[name] = AC1015Layout(drawing, handle)

    def __contains__(self, name):
        return name in self._layouts

    def modelspace(self):
        return self.get('Model')

    def names(self):
        return self._layouts.keys()

    def get(self, name):
        if name is None:
            return self.names_in_taborder()[1]
        else:
            return self._layouts[name]

    def names_in_taborder(self):
        names = []
        for name, layout in self._layouts.items():
            names.append( (layout.taborder, name) )
        return [name for order, name in sorted(names)]


class AC1015Layout(AC1015GraphicsBuilder):
    def __init__(self, drawing, layout_handle):
        self._layout_handle = layout_handle
        self._dxffactory = drawing.dxffactory
        self._block_record = self.dxflayout.get_block_record()
        self._paperspace = 0 if self.name == 'Model' else 1
        self._workspace = drawing.sections.entities

    @property
    def dxflayout(self):
        return self._dxffactory.wrap_handle(self._layout_handle)

    @property
    def name(self):
        return self.dxflayout.name

    @property
    def taborder(self):
        return self.dxflayout.taborder

    def _build_entity(self, type_, attribs):
        return self._dxffactory.create_db_entry(type_, attribs)

    def _add_entity(self, entity):
        self._workspace.add(entity)

    def _set_paper_space(self, attribs):
        attribs['paperspace'] = self._paperspace
        attribs['block_record'] = self._block_record
