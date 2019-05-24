# Purpose: Import data from another DXF drawing
# Created: 27.04.13
# Copyright (c) 2013-2019, Manfred Moitzi
# License: MIT License
"""
Importer add-on
---------------

This add-on is meant to import graphical entities from another DXF drawing and their required table entries like LAYER,
LTYPE or STYLE.

Because of complex extensibility of the DXF format and the lack of a good documentation, I decided to remove most of the
possible source drawing dependencies from source entities at import, therefore imported entities may not look the same
as the original entities in the source drawing, but the least geometry should be the same and the DXF file does not
break.

Removed data which could contain source drawing dependencies: Extension Dictionaries, AppData and XDATA.

The new CarefulImporter() supports following data import:

  - entities which are really safe to import, see const IMPORT_ENTITIES.
  - table and table entry import is restricted to LAYER, LTYPE and STYLE
  - import of BLOCK definitions is supported

Import of DXF objects from the OBJECTS section is not supported.

"""

from typing import TYPE_CHECKING, Iterable, Set, cast, Union, List, Dict
import logging
from ezdxf.lldxf.const import DXFKeyError

if TYPE_CHECKING:
    from ezdxf.eztypes import Drawing, DXFEntity, BaseLayout, DXFGraphic, BlockLayout

logger = logging.getLogger('ezdxf')

IMPORT_TABLES = ['linetypes', 'layers', 'styles']
IMPORT_ENTITIES = {
    'LINE', 'POINT', 'CIRCLE', 'ARC', 'TEXT', 'SOLID', 'TRACE', '3DFACE', 'SHAPE', 'POLYLINE', 'ATTRIB', 'ATTDEF',
    'ELLIPSE', 'MTEXT', 'LWPOLYLINE', 'SPLINE', 'HATCH', 'MESH', 'XLINE', 'RAY'
}


class CarefulImporter:
    def __init__(self, source: 'Drawing', target: 'Drawing'):
        self.source = source  # type: Drawing
        self.target = target  # type: Drawing
        self.used_layers = set()  # type: Set[str]  # layer names as string
        self.used_linetypes = set()  # type: Set[str]  # line type names as string, requires a TABLE entry
        self.used_styles = set()  # type: Set[str]  # text style name as string, requires a TABLE entry
        self.imported_inserts = list()  # type: List[DXFEntity]  # imported inserts
        self.imported_blocks = dict()  # type: Dict[str, str]  # imported blocks, (old_name, new_name)

    def add_used_resources(self, entity: 'DXFEntity') -> None:
        self.used_layers.add(entity.get_dxf_attrib('layer', '0'))
        self.used_linetypes.add(entity.get_dxf_attrib('linetype', 'BYLAYER'))

        dxftype = entity.dxftype()
        if dxftype in {'TEXT', 'MTEXT'}:
            self.used_styles.add(entity.get_dxf_attrib('style', 'Standard'))

    def import_tables(self, table_names: Union[str, Iterable[str]] = "*", conflict: str = "discard") -> None:
        """ Import DXF tables.

        Args:
            table_names: names of tables to import, "*" for all
            conflict: discard|replace, default is discard
        """
        if isinstance(table_names, str):
            if table_names == "*":  # import all supported tables
                table_names = IMPORT_TABLES
            else:  # import one specific table
                table_names = (table_names,)
        for table_name in table_names:
            self.import_table(table_name, entries="*", conflict=conflict)

    def import_table(self, name: str, entries: Union[str, Iterable[str]] = "*", conflict: str = "discard") -> None:
        """
        Import specific table entries from a DXF table.

        Args:
            name: valid table names are 'layers', 'linetypes', 'appids', 'dimstyles', 'styles', 'ucs', 'views', 'viewports'
            entries: Iterable of table names, or a single table name, or "*" for all table entries
            conflict: discard|replace, default is discard

        """
        if conflict not in ('replace', 'discard'):
            raise ValueError('Invalid value "{}" for argument conflict.'.format(conflict))
        if name not in IMPORT_TABLES:
            raise ValueError('Table "{}" import not supported.'.format(name))
        try:
            source_table = getattr(self.source.tables, name)
        except AttributeError:
            raise ValueError('Source table "{}" not found.'.format(name))
        try:
            target_table = getattr(self.target.tables, name)
        except AttributeError:
            raise ValueError('Target table "{}" not found.'.format(name))

        if isinstance(entries, str):
            if entries == "*":  # import all table entries
                entries = (entry.dxf.name for entry in source_table)
            else:  # import just one table entry
                entries = (entries,)
        for entry_name in entries:
            table_entry = source_table.get(entry_name)
            entry_name = table_entry.dxf.name
            if entry_name in target_table:
                if conflict == 'discard':
                    logger.debug('Discarding already existing entry "{}" of {} table.'.format(entry_name, name))
                    continue
                else:  # replace existing entry
                    logger.debug('Replacing already existing entry "{}" of {} table.'.format(entry_name, name))
                    target_table.remove(table_entry.dxf.name)

            # duplicate table entry
            new_table_entry = new_clean_entity(table_entry)
            new_table_entry.doc = self.target
            # create a new handle and add entity to target entity database
            self.target.entitydb.add(new_table_entry)
            # add new table entry to target table and set owner attributes
            target_table.add_entry(new_table_entry)

    def import_entity(self, entity: 'DXFEntity', target_layout: 'BaseLayout' = None):
        if target_layout is None:
            target_layout = self.target.modelspace()

        dxftype = entity.dxftype()
        if dxftype not in IMPORT_ENTITIES:
            logger.debug('Import of {} not supported'.format(str(entity)))
            return
        self.add_used_resources(entity)
        new_entity = cast('DXFGraphic', entity.copy())
        new_entity.doc = self.target
        self.target.entitydb.add(new_entity)
        target_layout.add_entity(new_entity)

        if dxftype == 'INSERT':
            self.imported_inserts.append(new_entity)

    def import_entities(self, entities: Iterable['DXFEntity'], target_layout: 'BaseLayout' = None):
        """
        Import all `entities` into `target_layout` or the modelspace of the target drawing, if `target_layout` is None.

        Args:
            entities: Iterable of DXF entities
            target_layout: any layout (modelspace, paperspace or block)

        """
        for entity in entities:
            self.import_entity(entity, target_layout)

    def import_blocks(self, block_names: Iterable[str], conflict: str = "discard") -> None:
        """ Import block definitions.

        Args:
            block_names: names of blocks to import
            conflict: discard|rename

        """
        for block_name in block_names:
            if (block_name in self.target.blocks) and conflict == 'discard':
                continue
            self.import_block(block_name)

    def import_block(self, block_name: str) -> str:
        """ Import one block definition. Block will be renamed if block name already exist in the target drawing.

        Args:
            block_name: name of block to import

        Returns: block name (renamed)

        """
        def get_new_block_name() -> str:
            num = 0
            name = block_name
            while name in target_blocks:
                name = block_name + str(num)
                num += 1
            return name

        try:  # already imported block?
            return self.imported_blocks[block_name]
        except KeyError:
            pass

        try:
            source_block = self.source.blocks[block_name]
        except DXFKeyError:
            raise ValueError('Source block "{}" not found.'.format(block_name))

        target_blocks = self.target.blocks
        new_block_name = get_new_block_name()
        target_block = target_blocks.new(new_block_name, base_point=source_block.dxf.base_point, dxfattribs={
            'description': source_block.dxf.description,
            'flags': source_block.dxf.flags,
            'xref_path': source_block.dxf.xref_path,
        })
        self.import_entities(source_block, target_layout=target_block)
        self.imported_blocks[block_name] = new_block_name
        return new_block_name

    def resolve_inserts(self) -> None:
        inserts = list(self.imported_inserts)
        # clear imported inserts, block import may append additional inserts
        self.imported_inserts = []
        for insert in inserts:
            block_name = self.import_block(insert.dxf.name)
            insert.dxf.name = block_name

        # additional inserts added by block imports?
        if len(self.imported_inserts):
            self.resolve_inserts()

    def import_required_table_entries(self):
        if len(self.used_layers):
            self.import_table('layers', self.used_layers)
        if len(self.used_linetypes):
            self.import_table('linetypes', self.used_linetypes)
        if len(self.used_styles):
            self.import_table('styles', self.used_styles)


def new_clean_entity(entity: 'DXFEntity', xdata: bool = False) -> 'DXFEntity':
    """
    Copy entity and remove all external dependencies.

    Args:
        entity: DXF entity
        xdata: remove xdata flag

    """
    new_entity = entity.copy()
    # clear drawing link
    new_entity.doc = None
    new_entity.appdata = None
    new_entity.reactors = None
    new_entity.extension_dict = None
    if not xdata:
        new_entity.xdata = None
    return new_entity
