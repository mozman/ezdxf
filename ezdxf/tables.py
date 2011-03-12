#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: tables
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from collections import OrderedDict

from .defaultchunk import DefaultChunk, iterchunks

class TablesSection:
    name = 'tables'
    def __init__(self, tags, drawing):
        self.drawing = drawing
        self._tables = OrderedDict()
        self._setup_tables(tags)

    def _setup_tables(self, tags):
        def name(table):
            return table[1].value

        def skiptags(tags, count):
            for i in range(count):
                next(tags)
            return tags

        itertags = skiptags(iter(tags), 2) # (0, 'SECTION'), (2, 'TABELS')
        for table in iterchunks(itertags, stoptag='ENDSEC', endofchunk='ENDTAB'):
            table_class = get_table_class(name(table))
            new_table = table_class(table, self.drawing)
            self._tables[new_table.name] = new_table

    def __getattr__(self, key):
        try:
            return self._tables[key]
        except KeyError:
            raise AttributeError(key)

    @property
    def dxfengine(self):
        return self.drawing.dxfengine

    def write(self, stream):
        stream.write('  0\nSECTION\n  2\nTABLES\n')
        for table in self._tables.values():
            table.write(stream)
        stream.write('  0\nENDSEC\n')

TABLESMAP = {
}

def get_table_class(name):
    return TABLESMAP.get(name, DefaultChunk)