# Purpose: tables section
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .table import Table, ViewportTable, StyleTable
from ..lldxf.tags import DXFTag
from ..lldxf.extendedtags import ExtendedTags
from ..lldxf.const import DXFAttributeError, DXFStructureError


class TablesSection(object):
    name = 'TABLES'

    def __init__(self, entities, drawing):
        self._drawing = drawing
        self._tables = {}
        if entities is None:
            section_head = [DXFTag(0, 'SECTION'), DXFTag(2, 'TABLES')]
            entities = [section_head]
        self._setup_tables(iter(entities))

    def __iter__(self):
        return iter(self._tables.values())

    @staticmethod
    def key(name):
        return name.upper()

    def _setup_tables(self, entities):
        section_head = next(entities)
        if section_head[0] != (0, 'SECTION') or section_head[1] != (2, 'TABLES'):
            raise DXFStructureError("Critical structure error in TABLES section.")

        table_entities = []
        table_name = None
        for entity in entities:
            if isinstance(entity, ExtendedTags):
                entity = entity.noclass
            if entity[0] == (0, 'TABLE'):
                table_entities = [entity]  # collect table head!
                if len(entity) < 2 or entity[1].code != 2:
                    raise DXFStructureError(
                        'DXFStructureError: missing required table name tag (2, name) at start of table.')
                table_name = entity[1].value
            elif entity[0] == (0, 'ENDTAB'):  # do not collect (0, 'ENDTAB')
                self._new_table(table_name, table_entities)
                table_entities = []  # collect entities outside of tables, but ignore it
                table_name = None
            else:  # collect table entries
                table_entities.append(entity)

        self._create_missing_tables()

    def _new_table(self, name, table_entities):
            table_class = TABLESMAP[name]
            new_table = table_class(table_entities, self._drawing)
            self._tables[self.key(new_table.name)] = new_table

    def _setup_table(self, name):
        """
        Setup new empty table.

        Args:
            name: real table name like 'VPORT' for viewports

        """
        name = self.key(name)
        if self._drawing is not None:
            dxfversion = self._drawing.dxfversion
            handle = self._drawing.entitydb.get_unique_handle()
        else:  # test environment without Drawing() object
            dxfversion = 'AC1009'  # DXF R12
            handle = '0'

        if dxfversion <= 'AC1009':
            table_entities = [[
                DXFTag(0, 'TABLE'),
                DXFTag(2, name),
                DXFTag(70, 0)
            ]]
        else:
            table_entities = [[
                DXFTag(0, 'TABLE'),
                DXFTag(2, name),
                DXFTag(5, handle),
                DXFTag(330, '0'),
                DXFTag(100, 'AcDbSymbolTable'),
                DXFTag(70, 0)
            ]]
        self._new_table(name, table_entities)

    def _create_missing_tables(self):
        if 'LAYERS' not in self:
            self._setup_table('LAYER')
        if 'LINETYPES' not in self:
            self._setup_table('LTYPE')
        if 'STYLES' not in self:
            self._setup_table('STYLE')
        if 'DIMSTYLES' not in self:
            self._setup_table('DIMSTYLE')
        if 'VIEWPORTS' not in self:
            self._setup_table('VPORT')
        if 'APPIDS' not in self:
            self._setup_table('APPID')
        if 'UCS' not in self:
            self._setup_table('UCS')

    def __contains__(self, item):
        return self.key(item) in self._tables

    def __getattr__(self, key):
        key = self.key(key)
        try:
            return self._tables[key]
        except KeyError:  # internal exception
            raise DXFAttributeError(key)

    def __getitem__(self, key):
        return self._tables[self.key(key)]

    def __delitem__(self, key):
        del self._tables[self.key(key)]

    def write(self, tagwriter):
        tagwriter.write_str('  0\nSECTION\n  2\nTABLES\n')
        for table_name in TABLE_ORDER:
            table = self._tables.get(table_name)
            if table is not None:
                table.write(tagwriter)
        tagwriter.write_tag2(0, 'ENDSEC')


TABLESMAP = {
    'LAYER': Table,
    'LTYPE': Table,
    'STYLE': StyleTable,
    'DIMSTYLE': Table,
    'VPORT': ViewportTable,
    'VIEW': Table,
    'UCS': Table,
    'APPID': Table,
    'BLOCK_RECORD': Table,
}

# The order of the tables may change, but the LTYPE table always precedes the LAYER table.
TABLE_ORDER = ('VIEWPORTS', 'LINETYPES', 'LAYERS', 'STYLES', 'VIEWS', 'UCS', 'APPIDS', 'DIMSTYLES', 'BLOCK_RECORDS')
