#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: tables contained in tables sections
# Created: 13.03.2011
# Copyright (C) , Manfred Moitzi
# License: GPLv3

from collections import OrderedDict

from .defaultchunk import DefaultChunk
from .tags import Tags, DXFTag, TagGroups

TABLENAMES = {
    'layer': 'layers',
    'ltype': 'linetypes',
    'appid': 'appids',
    'dimstyle': 'dimstyles',
    'style': 'styles',
    'ucs': 'ucs',
    'view': 'views',
    'vport': 'viewports',
    'block_record': 'blockrecords',
}

def tablename(dxfname):
    name = dxfname.lower()
    return TABLENAMES.get(name, name+'s')

class GenericTable(DefaultChunk):
    @property
    def name(self):
        return tablename(self.tags[1].value)

class Table:
    def __init__(self, tags, drawing):
        self._dxfname = tags[1].value
        self.name = tablename(self._dxfname)
        self._drawing = drawing
        self._tableentries = list()
        self._build_tableentries(tags)

    def __len__(self):
        return len(self._tableentries)

    def _build_tableentries(self, tags):
        groups = TagGroups(tags)
        assert groups.getname(0) == 'TABLE'
        assert groups.getname(-1) == 'ENDTAB'

        self._prologuetags = Tags(groups[0][1:])
        for entrytags in groups[1:-1]:
            self.add(entrytags)

    @property
    def entitydb(self):
        return self._drawing.entitydb

    @property
    def handles(self):
        return self._drawing.handles

    @property
    def dxfengine(self):
        return self._drawing.dxfengine

    def __iter__(self):
        for handle in self._tableentries:
            yield self.entitydb[handle]

    def add(self, entry):
        if isinstance(entry, Tags):
            handle = entry.gethandle(self.handles)
            self.entitydb[handle] = entry
        else:
            handle = entry.handle
        self._tableentries.append(handle)

    def get(self, name):
        handle = self.get_handle(name)
        tags = self.entitydb[handle]
        return self.dxfengine.table_entry_wrapper(tags, handle)

    def remove(self, name):
        handle = self.get_handle(name)
        self._tableentries.remove(handle)
        del self.entitydb[handle]

    def get_handle(self, name):
        def tablename(tags):
            return tags[tags.findfirst(2)].value

        for handle in self._tableentries:
            entry = self.entitydb[handle]
            if tablename(entry) == name:
                return handle
        raise ValueError(name)

    def write(self, stream):
        def prologue():
            stream.write('  0\nTABLE\n')
            self._update_entrycount()
            self._prologuetags.write(stream)

        def content():
            for entry in self:
                entry.write(stream)

        def epilogue():
            stream.write('  0\nENDTAB\n')

        prologue()
        content()
        epilogue()

    def _update_entrycount(self):
        self._prologuetags.settag(70, len(self))
