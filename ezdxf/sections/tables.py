# Purpose: tables section
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from ezdxf.lldxf.defaultchunk import iter_chunks
from .table import GenericTable, Table, ViewportTable
from ..lldxf.tags import DXFStructureError, Tags
from ..options import options

MIN_TABLE_SECTION = """  0
SECTION
  2
TABLES
  0
ENDSEC
"""

MIN_TABLE = """  0
TABLE
  2
DUMMY
 70
0
  0
ENDTAB
"""


class TablesSection(object):
    name = 'tables'

    def __init__(self, tags, drawing):
        self._drawing = drawing
        self._tables = {}
        if tags is None:
            tags = Tags.from_text(MIN_TABLE_SECTION)
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
        for table_tags in iter_chunks(tags_iterator, stoptag='ENDSEC', endofchunk='ENDTAB'):
            self._new_table(name(table_tags), table_tags)

        self._create_required_tables()

    def _new_table(self, name, tags):
            table_class = get_table_class(name)
            new_table = table_class(tags, self._drawing)
            self._tables[new_table.name] = new_table

    def _create_required_tables(self):
        def setup_table(name):
            tags = Tags.from_text(MIN_TABLE.replace('DUMMY', name))
            self._new_table(name, tags)

        if 'layers' not in self._tables:
            setup_table('LAYER')
        if 'linetypes' not in self._tables:
            setup_table('LTYPE')
        if 'styles' not in self._tables:
            setup_table('STYLE')
        if 'dimstyles' not in self._tables:
            setup_table('DIMSTYLE')

    def __contains__(self, item):
        return item in self._tables

    def __getattr__(self, key):
        try:
            return self._tables[key]
        except KeyError:
            raise AttributeError(key)

    def __getitem__(self, key):
        return self._tables[key]

    def __delitem__(self, key):
        del self._tables[key]

    def write(self, stream):
        stream.write('  0\nSECTION\n  2\nTABLES\n')
        for table_name in TABLE_ORDER:
            table = self._tables.get(table_name)
            if table is not None:
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

# The order of the tables may change, but the LTYPE table always precedes the LAYER table.
TABLE_ORDER = ('viewports', 'linetypes', 'layers', 'styles', 'views', 'ucs', 'appids', 'dimstyles', 'block_records')


def get_table_class(name):
    return TABLESMAP.get(name, GenericTable)