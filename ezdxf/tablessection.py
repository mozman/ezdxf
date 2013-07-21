# Purpose: tables section
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .defaultchunk import iter_chunks
from .table import GenericTable, Table, ViewportTable
from .tags import DXFStructureError
from .options import options

class TablesSection(object):
    name = 'tables'

    def __init__(self, tags, drawing):
        self._drawing = drawing
        self._tables = {}
        self._setup_tables(tags)

    def __iter__(self):
        return iter(self._tables.values())

    def _setup_tables(self, tags):
        def name(table):
            return table[1].value

        def skip_tags(tags, count):
            for i in range(count):
                next(tags)
            return tags

        if tags[0] != (0, 'SECTION') or \
            tags[1] != (2, 'TABLES') or \
            tags[-1] != (0, 'ENDSEC'):
            raise DXFStructureError("Critical structure error in TABLES section.")

        tags_iterator = skip_tags(iter(tags), 2)  # (0, 'SECTION'), (2, 'TABLES')
        for table in iter_chunks(tags_iterator, stoptag='ENDSEC', endofchunk='ENDTAB'):
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
        for table_name in TABLE_ORDER:
            table = self._tables.get(table_name)
            if table is None:
                options.logger.debug('{} table does not exist.'.format(table_name.upper()))
            else:
                options.logger.debug('writing table: {}'.format(table_name.upper()))
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

TABLE_ORDER = ('viewports', 'linetypes', 'layers', 'styles', 'views', 'ucs', 'appids', 'dimstyles', 'block_records')

def get_table_class(name):
    return TABLESMAP.get(name, GenericTable)