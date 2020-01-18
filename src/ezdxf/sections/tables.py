# Purpose: tables section
# Created: 12.03.2011
# Copyright (c) 2011-2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, List
import logging
from ezdxf.lldxf.const import DXFStructureError, DXF12
from .table import Table, ViewportTable, StyleTable, LayerTable

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, Drawing, DXFEntity, DXFTagStorage, DimStyle

logger = logging.getLogger('ezdxf')

TABLENAMES = {
    'LAYER': 'layers',
    'LTYPE': 'linetypes',
    'APPID': 'appids',
    'DIMSTYLE': 'dimstyles',
    'STYLE': 'styles',
    'UCS': 'ucs',
    'VIEW': 'views',
    'VPORT': 'viewports',
    'BLOCK_RECORD': 'block_records',
}

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


class TablesSection:
    def __init__(self, doc: 'Drawing', entities: List['DXFEntity'] = None):
        assert doc is not None
        self.doc = doc
        self.layers = None
        self.linetypes = None
        self.appids = None
        self.dimstyles = None
        self.styles = None
        self.ucs = None
        self.views = None
        self.viewports = None
        self.block_records = None

        if entities is not None:
            self._load(entities)
        self._create_missing_tables()

    def _load(self, entities: List['DXFEntity']) -> None:
        section_head = entities[0]  # type: DXFTagStorage
        if section_head.dxftype() != 'SECTION' or section_head.base_class[1] != (2, 'TABLES'):
            raise DXFStructureError("Critical structure error in TABLES section.")
        del entities[0]  # delete first entity (0, SECTION)

        table_records = []
        table_name = None
        for entity in entities:
            if entity.dxftype() == 'TABLE':
                if len(table_records):
                    # TABLE entity without preceding ENDTAB entity, should we care?
                    logger.debug('Ignore missing ENDTAB entity in table "{}".'.format(table_name))
                    self._load_table(table_name, table_records)
                table_name = entity.dxf.name
                table_records = [entity]  # collect table head
            elif entity.dxftype() == 'ENDTAB':  # do not collect (0, 'ENDTAB')
                self._load_table(table_name, table_records)
                table_records = []  # collect entities outside of tables, but ignore it
            else:  # collect table entries
                table_records.append(entity)

        if len(table_records):
            # last ENDTAB entity is missing, should we care?
            logger.debug('Ignore missing ENDTAB entity in table "{}".'.format(table_name))
            self._load_table(table_name, table_records)

    def _load_table(self, name: str, table_entities: Iterable['DXFEntity']) -> None:
        """
        Load table from tags.

        Args:
            name: table name e.g. VPORT
            table_entities: iterable of table records

        """
        table_class = TABLESMAP[name]
        new_table = table_class(self.doc, table_entities)
        setattr(self, TABLENAMES[name], new_table)

    def _create_missing_tables(self) -> None:
        for record_name, table_name in TABLENAMES.items():
            if getattr(self, table_name) is None:
                self._create_new_table(record_name, table_name)

    def _create_new_table(self, record_name: str, table_name: str) -> None:
        """
        Setup new empty table.

        Args:
            record_name: table name e.g. VPORT
            table_name: TableSection attribute name e.g. viewports

        """
        handle = self.doc.entitydb.next_handle()
        table_class = TABLESMAP[record_name]
        table = table_class.new_table(record_name, handle, self.doc)
        setattr(self, table_name, table)

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        tagwriter.write_str('  0\nSECTION\n  2\nTABLES\n')
        version = tagwriter.dxfversion
        self.viewports.export_dxf(tagwriter)
        self.linetypes.export_dxf(tagwriter)
        self.layers.export_dxf(tagwriter)
        self.styles.export_dxf(tagwriter)
        self.views.export_dxf(tagwriter)
        self.ucs.export_dxf(tagwriter)
        self.appids.export_dxf(tagwriter)
        self.dimstyles.export_dxf(tagwriter)
        if version > DXF12:
            self.block_records.export_dxf(tagwriter)
        tagwriter.write_tag2(0, 'ENDSEC')

    def create_table_handles(self):
        # TABLE requires in DXF12 no handle and has no owner tag, but DXF R2000+, requires a TABLE with handle
        # and each table entry has an owner tag, pointing to the TABLE entry
        for name in TABLENAMES.values():
            table = getattr(self, name.lower())
            handle = self.doc.entitydb.next_handle()
            table.set_handle(handle)

    def resolve_dimstyle_names(self):
        # Handles can't be resolved to names at loading stage.
        db = self.doc.entitydb
        for dimstyle in self.dimstyles:  # type: DimStyle
            for attrib_name in ('dimblk', 'dimblk1', 'dimblk2', 'dimldrblk'):
                if dimstyle.dxf.hasattr(attrib_name):
                    continue
                blkrec_handle = dimstyle.dxf.get(attrib_name + '_handle')
                if blkrec_handle and blkrec_handle != '0':
                    try:
                        name = db[blkrec_handle].dxf.name
                    except KeyError:
                        logger.info('Replacing non existing block referenced by handle #{}, by default arrow.'.format(blkrec_handle))
                        name = ''
                else:
                    name = ''  # default arrow
                dimstyle.dxf.set(attrib_name, name)

            style_handle = dimstyle.dxf.get('dimtxsty', None)
            if style_handle and style_handle != '0':
                try:
                    dimstyle.dxf.dimtxsty = db[style_handle].dxf.name
                except KeyError:
                    logger.info('Ignoring non existing text style referenced by handle #{}.'.format(style_handle))

            for attrib_name in ('dimltype', 'dimltex1', 'dimltex2'):
                lt_handle = dimstyle.dxf.get(attrib_name + '_handle', None)
                if lt_handle and lt_handle != '0':
                    try:
                        name = db[lt_handle].dxf.name
                    except KeyError:
                        logger.info('Ignoring non existing line type referenced by handle #{}.'.format(lt_handle))
                    else:
                        dimstyle.dxf.set(attrib_name, name)

            # remove all handles, to be sure setting handles for actual names at export
            dimstyle.discard_handles()
