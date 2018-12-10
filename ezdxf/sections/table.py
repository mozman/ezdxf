# Purpose: tables contained in tables sections
# Created: 13.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, Iterator, Union, Optional, Sequence

from ezdxf.lldxf.types import DXFTag
from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.lldxf.const import DXFTableEntryError, DXFStructureError, DXFAttributeError, Error

if TYPE_CHECKING:
    from ezdxf.drawing import Drawing
    from ezdxf.dxfentity import DXFEntity
    from ezdxf.dxffactory import DXFFactory
    from ezdxf.database import EntityDB
    from ezdxf.tools.handle import HandleGenerator
    from ezdxf.lldxf.tagwriter import TagWriter

TABLENAMES = {
    'LAYER': 'LAYERS',
    'LTYPE': 'LINETYPES',
    'APPID': 'APPIDS',
    'DIMSTYLE': 'DIMSTYLES',
    'STYLE': 'STYLES',
    'UCS': 'UCS',
    'VIEW': 'VIEWS',
    'VPORT': 'VIEWPORTS',
    'BLOCK_RECORD': 'BLOCK_RECORDS',
}


def tablename(dxfname: str) -> str:
    """ Translate DXF-table-name to attribute-name. ('LAYER' -> 'LAYERS') """
    name = dxfname.upper()
    return TABLENAMES.get(name, name + 'S')


class Table:
    def __init__(self, entities: Iterable[Tags], drawing: 'Drawing'):
        self._table_header = None
        self._dxfname = None
        self._drawing = drawing
        self._table_entries = []
        self._build_table_entries(iter(entities))

    # start public interface

    @staticmethod
    def key(entity: Union[str, 'DXFEntity']) -> str:
        if not isinstance(entity, str):
            entity = entity.dxf.name
        return entity.lower()  # table key is lower case

    @property
    def name(self) -> str:
        return tablename(self._dxfname)

    def has_entry(self, name: str) -> bool:
        """ Check if an table-entry 'name' exists. """
        key = self.key(name)
        return any(self.key(entry) == key for entry in self)

    __contains__ = has_entry

    def new(self, name: str, dxfattribs: dict = None) -> 'DXFEntity':
        if self.has_entry(name):
            raise DXFTableEntryError('%s %s already exists!' % (self._dxfname, name))
        dxfattribs = dxfattribs or {}
        dxfattribs['name'] = name
        return self.new_entry(dxfattribs)

    def get(self, name: str) -> 'DXFEntity':
        """ Get table-entry by name as WrapperClass(). """
        key = self.key(name)
        for entry in iter(self):
            if self.key(entry) == key:
                return entry
        raise DXFTableEntryError(name)

    def remove(self, name: str) -> None:
        """ Remove table-entry from table and entitydb by name. """
        entry = self.get(name)
        handle = entry.dxf.handle
        self.remove_handle(handle)

    def __len__(self) -> int:
        return len(self._table_entries)

    def __iter__(self) -> Iterable['DXFEntity']:
        for handle in self._table_entries:
            yield self.get_table_entry_wrapper(handle)

    # end public interface

    def _build_table_entries(self, entities: Iterator[Tags]) -> None:
        table_head = next(entities)
        if table_head[0].value != 'TABLE':
            raise DXFStructureError("Critical structure error in TABLES section.")
        self._dxfname = table_head[1].value
        self._table_header = ExtendedTags(table_head)  # do not store the table head in the entity database
        for table_entry in entities:
            self._append_entry_handle(table_entry.get_handle())

    @property
    def entitydb(self) -> 'EntityDB':
        return self._drawing.entitydb

    @property
    def handles(self) -> 'HandleGenerator':
        return self._drawing.entitydb.handles

    @property
    def dxffactory(self) -> 'DXFFactory':
        return self._drawing.dxffactory

    def _iter_table_entries_as_tags(self) -> Iterable[ExtendedTags]:
        """ Iterate over table-entries as Tags(). """
        return (self.entitydb[handle] for handle in self._table_entries)

    def new_entry(self, dxfattribs: dict) -> 'DXFEntity':
        """ Create new table-entry of type 'self._dxfname', and add new entry
        to table.

        Does not check if an entry dxfattribs['name'] already exists!
        Duplicate entries are possible for Viewports.
        """
        handle = self.handles.next()
        entry = self.dxffactory.new_entity(self._dxfname, handle, dxfattribs)
        self._add_entry(entry)
        return entry

    def _add_entry(self, entry: Union[ExtendedTags, 'DXFEntity']) -> None:
        """ Add table-entry to table and entitydb. """
        if isinstance(entry, ExtendedTags):
            tags = entry
        else:
            tags = entry.tags
        handle = self.entitydb.add_tags(tags)
        self._append_entry_handle(handle)

    def _append_entry_handle(self, handle: str) -> None:
        if handle not in self._table_entries:
            self._table_entries.append(handle)

    def get_table_entry_wrapper(self, handle: str) -> 'DXFEntity':
        tags = self.entitydb[handle]
        return self.dxffactory.wrap_entity(tags)

    def write(self, tagwriter: 'TagWriter') -> None:
        """ Write DXF representation to stream, stream opened with mode='wt'. """

        def prologue():
            self._update_owner_handles()
            self._update_meta_data()
            tagwriter.write_tags(self._table_header)

        def content():
            for tags in self._iter_table_entries_as_tags():
                tagwriter.write_tags(tags)

        def epilogue():
            tagwriter.write_tag2(0, 'ENDTAB')

        prologue()
        content()
        epilogue()

    def _update_owner_handles(self) -> None:
        if self._drawing.dxfversion <= 'AC1009':
            return  # no owner handles
        owner_handle = self._table_header.get_handle()
        for entry in iter(self):
            if not entry.supports_dxf_attrib('owner'):
                raise DXFAttributeError(repr(entry))
            entry.dxf.owner = owner_handle

    def _update_meta_data(self) -> None:
        count = len(self)
        if self._drawing.dxfversion > 'AC1009':
            subclass = self._table_header.get_subclass('AcDbSymbolTable')
        else:
            subclass = self._table_header.noclass
        subclass.set_first(DXFTag(70, count))

    def remove_handle(self, handle: str) -> None:
        """ Remove table-entry from table and entitydb by handle. """
        self._table_entries.remove(handle)
        del self.entitydb[handle]

    def audit(self, auditor) -> None:
        """
        Checks for table entries with same key.
        """
        entries = sorted(self._table_entries, key=lambda e: self.key(e))
        prev_key = None
        for entry in entries:
            key = self.key(entry)
            if key == prev_key:
                auditor.add_error(
                    code=Error.DUPLICATE_TABLE_ENTRY_NAME,
                    message="Duplicate table entry name '{1}' in table {0}".format(self.name, entry.dxf.name),
                    dxf_entity=self,
                    data=key,
                )
            prev_key = key


class StyleTable(Table):
    def get_shx(self, shxname: str) -> 'DXFEntity':
        """
        Get existing shx entry, or create a new entry.

        Args:
            shxname: shape file name like 'ltypeshp.lin'

        """
        shape_file = self.find_shx(shxname)
        if shape_file is None:
            dxfattribs = {
                'font': shxname,
                'flags': 1,
                'name': '',  # shape file entry has no name
                'last_height': 2.5,  # just if this is required by AutoCAD
            }
            return self.new_entry(dxfattribs)
        else:
            return shape_file

    def find_shx(self, shxname: str) -> Optional['DXFEntity']:
        """
        Find .shx shape file table entry, by a case insensitive search.

        A .shx shape file table entry has no name, so you have to search by the font attribute.

        Args:
            shxname: .shx shape file name

        Returns:
            table entry or None if not found
        """
        lower_name = shxname.lower()
        for entry in iter(self):
            if entry.dxf.font.lower() == lower_name:
                return entry
        return None


class ViewportTable(Table):
    # Viewport-Table can have multiple entries with same name
    def new(self, name: str, dxfattribs: dict = None):
        dxfattribs = dxfattribs or {}
        dxfattribs['name'] = name
        return self.new_entry(dxfattribs)

    def get_config(self, name: str) -> Sequence['DXFEntity']:
        key_func = self.key
        search_key = key_func(name)
        return [entry for entry in self if search_key == key_func(entry)]

    def delete_config(self, name: str) -> None:
        for entry in self.get_config(name):
            self.remove_handle(entry.dxf.handle)
