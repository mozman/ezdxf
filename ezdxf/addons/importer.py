# Purpose: Import data from another DXF drawing
# Created: 27.04.13
# Copyright (c) 2013-2018, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Dict, Iterable, List, cast
from ezdxf.query import name_query

if TYPE_CHECKING:
    from ezdxf.eztypes import Drawing, DXFEntity, Insert, BlockRecord, Layout

IMPORT_TABLE_NAMES = ['linetypes', 'layers', 'styles', 'dimstyles', 'appids', 'ucs', 'views', 'viewports']


class Importer:
    def __init__(self, source: 'Drawing', target: 'Drawing', strict_mode: bool = True):
        self.source = source  # type: Drawing
        self.target = target  # type: Drawing
        self._handle_translation_table = {}  # type: Dict[str, str]
        self._requires_data_from_objects_section = []  # type: List[DXFEntity]
        if strict_mode and not self.is_compatible():
            raise TypeError("DXF drawings are not compatible. Source version {}; Target version {}".format(
                source.dxfversion, target.dxfversion))

    def is_compatible(self) -> bool:
        if self.source.dxfversion == self.target.dxfversion:
            return True
        # The basic DXF structure has been changed with version AC1012 (AutoCAD R13)
        # It is not possible to copy from R12 to a newer version and
        # it is not possible to copy from R13 or a newer version to R12.
        if self.source.dxfversion == 'AC1009' or self.target.dxfversion == 'AC1009':
            return False
        # It is always possible to copy from older to newer versions (except R12).
        if self.target.dxfversion > self.source.dxfversion:
            return True
        # It is possible to copy an entity from a newer to an older versions, if the entity is defined for both versions
        # (like LINE, CIRCLE, ...), but this can not be granted by default. Enable this feature by
        # Importer(s, t, strict_mode=False).
        return False

    def import_all(self, table_conflict: str = "discard", block_conflict: str = "discard") -> None:
        self.import_tables(conflict=table_conflict)
        self.import_blocks(conflict=block_conflict)
        self.import_modelspace_entities()

    def import_modelspace_entities(self, query: str = "*") -> None:  # TODO
        pass

    def import_blocks(self, query: str = "*", conflict: str = "discard") -> None:  # TODO
        """ Import block definitions.

        Args:
            query: names of blocks to import, "*" for all
            conflict: discard|replace

        """
        pass

    def import_tables(self, query: str = "*", conflict: str = "discard") -> None:
        """ Import DXF tables.

        Args:
            query: names of tables to import, "*" for all
            conflict: discard|replace
        """
        for table_name in name_query(IMPORT_TABLE_NAMES, query):
            self.import_table(table_name, query="*", conflict=conflict)

    def import_table(self, name: str, query: str = "*", conflict: str = "discard") -> None:
        """
        Import specific entries from a DXF table.

        Args:
            name: valid table names are 'layers', 'linetypes', 'appids', 'dimstyles', 'styles', 'ucs', 'views', 'viewports'
            query: table name query, "*" for all
            conflict: discard|replace

        """
        if conflict not in ('replace', 'discard'):
            raise ValueError('Invalid value "{}" for argument conflict.'.format(conflict))
        if name == 'block_records':
            raise ValueError("Can not import BLOCK_RECORD table.")
        try:
            source_table = getattr(self.source.tables, name)
        except AttributeError:
            raise ValueError('Source table "{}" not found.'.format(name))
        try:
            target_table = getattr(self.target.tables, name)
        except AttributeError:
            raise ValueError('Target table "{}" not found.'.format(name))

        source_entry_names = (entry.dxf.name for entry in source_table)
        for entry_name in name_query(source_entry_names, query):
            table_entry = source_table.get(entry_name)
            if table_entry.dxf.name in target_table:
                if conflict == 'discard':
                    continue
                else:  # replace existing entry
                    target_table.remove(table_entry.dxf.name)

            # duplicate table entry
            new_table_entry = new_clean_entity(table_entry)
            # add new table entry to target table and set doc and owner attributes
            target_table.import_entry(new_table_entry)
            # create a new handle and add entity to target entity database
            self.target.entitydb.add(new_table_entry)


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
