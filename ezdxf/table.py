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
        self.dxfname = tags[1].value
        self.name = tablename(self.dxfname)
        self.drawing = drawing
        self._tableentries = OrderedDict()
        self._build_tableentries(tags)

    def __len__(self):
        return len(self._tableentries)

    def _build_tableentries(self, tags):
        groups = TagGroups(tags)
        assert groups.getname(0) == 'TABLE'
        assert groups.getname(-1) == 'ENDTAB'

        self._prologuetags = Tags(groups[0][1:])
        for entrytags in groups[1:-1]:
            entry = GenericTableEntry(entrytags, self.drawing)
            self.add(entry)

    @property
    def entitydb(self):
        return self.drawing.entitydb

    def __iter__(self):
        for handle in self._tableentries.values():
            yield self.entitydb[handle]

    def add(self, table_entry):
        self.entitydb[table_entry.handle] = table_entry
        self._tableentries[table_entry.name] = table_entry.handle

    def get(self, name):
        handle = self.get_handle(name)
        return self.entitydb[handle]

    def remove(self, name):
        handle = self.get_handle(name)
        del self._tableentries[name]
        del self.entitydb[handle]

    def get_handle(self, name):
        return self._tableentries[name]

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

class GenericTableEntry(DefaultChunk):
    def __init__(self, tags, drawing):
        super(GenericTableEntry, self).__init__(tags, drawing)
        self.handle = tags.gethandle(drawing.handles)
        self._name = tags[tags.findfirst(2)].value

    @property
    def name(self):
        return self._name
