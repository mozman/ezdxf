# Purpose: tables section
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from collections import OrderedDict

from .defaultchunk import iterchunks
from .table import GenericTable, Table, ViewportTable


class TablesSection(object):
    name = 'tables'

    def __init__(self, tags, drawing):
        self._drawing = drawing
        self._tables = OrderedDict()
        self._setup_tables(tags)

    def __iter__(self):
        return iter(self._tables.values())

    def _setup_tables(self, tags):
        def name(table):
            return table[1].value

        def skiptags(tags, count):
            for i in range(count):
                next(tags)
            return tags

        itertags = skiptags(iter(tags), 2)  # (0, 'SECTION'), (2, 'TABLES')
        for table in iterchunks(itertags, stoptag='ENDSEC', endofchunk='ENDTAB'):
            table_class = get_table_class(name(table))
            new_table = table_class(table, self._drawing)
            self._tables[new_table.name] = new_table

    def __contains__(self, item):
        return item in self._tables

    def __getattr__(self, key):
        try:
            return self._tables[key]
        except KeyError:
            raise AttributeError(key)

    def __getitem__(self, key):
        return self._tables[key]


    def write(self, stream):
        stream.write('  0\nSECTION\n  2\nTABLES\n')
        for table in self._tables.values():
            table.write(stream)
        stream.write('  0\nENDSEC\n')

TABLESMAP = {
    'LAYER': Table,
    'LTYPE': Table,
    'STYLE': Table,
    'DIMSTYLE': Table,
    'VPORT': ViewportTable,
    'VIEW': Table,
    'UCS': Table,
    'APPID': Table,
    'BLOCK_RECORD': Table,
}


def get_table_class(name):
    return TABLESMAP.get(name, GenericTable)