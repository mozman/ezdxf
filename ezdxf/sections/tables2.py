# Purpose: tables section
# Created: 12.03.2011
# Copyright (c) 2011-2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, List
import logging
from ezdxf.lldxf.const import DXFAttributeError, DXFStructureError, DXF12
from .table2 import Table, ViewportTable, StyleTable, LayerTable, tablename

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter
    from ezdxf.drawing2 import Drawing
    from ezdxf.entities.dxfentity import DXFEntity, DXFTagStorage


logger = logging.getLogger('ezdxf')


class TablesSection:
    name = 'TABLES'

    def __init__(self, doc: 'Drawing' = None, entities: List['DXFEntity'] = None):
        self.doc = doc
        self.tables = {}
        if entities is not None:
            self.load(entities)
        self._create_missing_tables()

    def __iter__(self) -> Iterable[Table]:
        return iter(self.tables.values())

    @staticmethod
    def key(name: str) -> str:
        return name.upper()

    def load(self, entities: List['DXFEntity']) -> None:
        section_head = entities[0]  # type: DXFTagStorage
        if section_head.dxftype() != 'SECTION' or section_head.base_class[1] != (2, 'TABLES'):
            raise DXFStructureError("Critical structure error in TABLES section.")

        table_entities = []
        table_name = None
        del entities[0]  # delete first entity (0, SECTION)
        for entity in entities:
            if entity.dxftype() == 'TABLE':
                if len(table_entities):
                    # TABLE entity without preceding ENDTAB entity, should we care?
                    logger.debug('Ignore missing ENDTAB entity in table "{}".'.format(table_name))
                    self._load_table(table_name, table_entities)
                table_name = entity.dxf.name
                table_entities = [entity]  # collect table head
            elif entity.dxftype() == 'ENDTAB':  # do not collect (0, 'ENDTAB')
                self._load_table(table_name, table_entities)
                table_entities = []  # collect entities outside of tables, but ignore it
            else:  # collect table entries
                table_entities.append(entity)

        if len(table_entities):
            # last ENDTAB entity is missing
            # TABLE entity without preceding ENDTAB entity, should we care?
            logger.debug('Ignore missing ENDTAB entity in table "{}".'.format(table_name))
            self._load_table(table_name, table_entities)

    def _load_table(self, name: str, table_entities: Iterable['DXFEntity']) -> None:
        table_class = TABLESMAP[name]
        new_table = table_class(self.doc, table_entities)
        self.tables[tablename(self.key(name))] = new_table

    def _setup_table(self, name):
        """
        Setup new empty table.

        Args:
            name: real table name like 'VPORT' for viewports

        """
        name = self.key(name)
        if self.doc is not None:
            handle = self.doc.entitydb.next_handle()
        else:  # test environment without Drawing() object
            handle = '0'
        table_class = TABLESMAP[name]
        table = table_class.new_table(name, handle, self.doc)
        self.tables[tablename(name)] = table

    def _create_missing_tables(self) -> None:
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
        if 'VIEWS' not in self:
            self._setup_table('VIEW')
        if 'APPIDS' not in self:
            self._setup_table('APPID')
        if 'UCS' not in self:
            self._setup_table('UCS')
        if 'BLOCK_RECORDS' not in self:
            self._setup_table('BLOCK_RECORD')

    def __contains__(self, item: str) -> bool:
        return self.key(item) in self.tables

    def __getattr__(self, key: str) -> Table:
        key = self.key(key)
        try:
            return self.tables[key]
        except KeyError:  # internal exception
            raise DXFAttributeError(key)

    def __getitem__(self, key: str) -> Table:
        return self.tables[self.key(key)]

    def __delitem__(self, key: str) -> None:
        del self.tables[self.key(key)]

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        tagwriter.write_str('  0\nSECTION\n  2\nTABLES\n')
        version = tagwriter.dxfversion
        self.tables['VIEWPORTS'].export_dxf(tagwriter)
        self.tables['LINETYPES'].export_dxf(tagwriter)
        self.tables['LAYERS'].export_dxf(tagwriter)
        self.tables['STYLES'].export_dxf(tagwriter)
        self.tables['VIEWS'].export_dxf(tagwriter)
        self.tables['UCS'].export_dxf(tagwriter)
        self.tables['APPIDS'].export_dxf(tagwriter)
        self.tables['DIMSTYLES'].export_dxf(tagwriter)
        if version > DXF12:
            self.tables['BLOCK_RECORDS'].export_dxf(tagwriter)
        tagwriter.write_tag2(0, 'ENDSEC')

    def create_table_handles(self):
        # TABLE requires in DXF12 no handle and has no owner tag, but DXF R2000+, requires a TABLE with handle
        # and each table entry has an owner tag, pointing to the TABLE entry
        # todo: assign each TABLE entity a handle, which is only now possible, when all used handles in the DXF file are known
        # todo: assign all TABLE entries the new handle of TABLE as new owner tag.
        for table in self:
            handle = self.doc.entitydb.next_handle()
            table.set_handle(handle)


TABLESMAP = {
    'LAYER': LayerTable,
    'LTYPE': Table,
    'STYLE': StyleTable,
    'DIMSTYLE': Table,
    'VPORT': ViewportTable,
    'VIEW': Table,
    'UCS': Table,
    'APPID': Table,
    'BLOCK_RECORD': Table,
}
