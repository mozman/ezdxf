# Purpose: tables contained in tables sections
# Created: 13.03.2011
# Copyright (c) 2011-2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, Iterator, Union, Optional, List
from collections import OrderedDict

from ezdxf.lldxf.const import DXFTableEntryError, DXFStructureError
from ezdxf.clone import clone
from ezdxf.entities.table import TableHead

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFFactoryType, EntityDB, TagWriter
    from ezdxf.drawing2 import Drawing
    from ezdxf.entities import DXFEntity

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
    name = TABLENAMES.get(name, name + 'S')
    return name


class Table:
    def __init__(self, doc: 'Drawing' = None, entities: Iterable['DXFEntity'] = None):
        self.doc = doc
        self.entries = OrderedDict()
        self._head = None
        if entities is not None:
            self.load(iter(entities))

    def load(self, entities: Iterator['DXFEntity']) -> None:
        self._head = next(entities)
        if self._head.dxftype() != 'TABLE':
            raise DXFStructureError("Critical structure error in TABLES section.")
        for table_entry in entities:
            self._append(table_entry)

    @classmethod
    def new_table(cls, name: str, handle: str, doc: 'Drawing') -> 'Table':
        table = cls(doc)
        table.set_head(name, handle)
        return table

    def set_head(self, name: str, handle: str = None) -> None:
        self._head = TableHead.new(handle, owner='0', dxfattribs={'name': name}, doc=self.doc)

    # start public interface

    @staticmethod
    def key(entity: Union[str, 'DXFEntity']) -> str:
        if not isinstance(entity, str):
            entity = entity.dxf.name
        return entity.lower()  # table key is lower case

    @property
    def name(self) -> str:
        return tablename(self._head.dxf.name)

    def has_entry(self, name: str) -> bool:
        """ Check if an table-entry 'name' exists. """
        return self.key(name) in self.entries

    __contains__ = has_entry

    def new(self, name: str, dxfattribs: dict = None) -> 'DXFEntity':
        if self.has_entry(name):
            raise DXFTableEntryError('%s %s already exists!' % (self._head.dxf.name, name))
        dxfattribs = dxfattribs or {}
        dxfattribs['name'] = name
        return self.new_entry(dxfattribs)

    def get(self, name: str) -> 'DXFEntity':
        """ Get table-entry by name as WrapperClass(). """
        key = self.key(name)
        entry = self.entries.get(key, None)
        if entry:
            return entry
        else:
            raise DXFTableEntryError(name)

    def remove(self, name: str) -> None:
        """ Remove table-entry from table and entitydb by name. """
        key = self.key(name)
        entry = self.get(name)
        self.entitydb.delete_entity(entry)
        del self.entries[key]

    def __len__(self) -> int:
        return len(self.entries)

    def __iter__(self) -> Iterable['DXFEntity']:
        return iter(self.entries.values())

    # end public interface

    @property
    def entitydb(self) -> 'EntityDB':
        return self.doc.entitydb

    @property
    def dxffactory(self) -> 'DXFFactoryType':
        return self.doc.dxffactory

    def new_entry(self, dxfattribs: dict) -> 'DXFEntity':
        """ Create new table-entry of type 'self._dxfname', and add new entry
        to table.

        Does not check if an entry dxfattribs['name'] already exists!
        Duplicate entries are possible for Viewports.
        """
        entry = self.dxffactory.create_db_entry(self._head.dxf.name, dxfattribs)
        self._append(entry)
        return entry

    def duplicate_entry(self, name: str, new_name: str) -> 'DXFEntity':
        entry = self.get(name)
        new_entry = clone(entry)
        new_entry.dxf.name = new_name
        self._append(new_entry)
        return new_entry

    def _append(self, entry: 'DXFEntity') -> None:
        self.entries[self.key(entry.dxf.name)] = entry

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        """ Write DXF representation to stream, stream opened with mode='wt'. """

        def prologue():
            self._update_owner_handles()
            self._head.dxf.count = len(self)
            self._head.export_dxf(tagwriter)

        def content():
            for entry in self.entries.values():
                # VPORT
                if isinstance(entry, list):
                    for e in entry:
                        e.export_dxf(tagwriter)
                else:
                    entry.export_dxf(tagwriter)

        def epilogue():
            tagwriter.write_tag2(0, 'ENDTAB')

        prologue()
        content()
        epilogue()

    def _update_owner_handles(self) -> None:
        owner_handle = self._head.dxf.handle
        for entry in self.entries.values():
            entry.dxf.owner = owner_handle


class LayerTable(Table):
    def new_entry(self, dxfattribs: dict) -> 'DXFEntity':
        if self.doc:
            if 'material' not in dxfattribs:
                dxfattribs['material_handle'] = self.doc.materials['Global'].dxf.handle
            if 'plot_style_name' not in dxfattribs:
                dxfattribs['plotstyle_handle'] = self.doc.plotstyles['Normal'].dxf.handle
        return super().new_entry(dxfattribs)


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
    # each table entry is a list of VPORT entries

    def new(self, name: str, dxfattribs: dict = None) -> 'DXFEntity':
        dxfattribs = dxfattribs or {}
        dxfattribs['name'] = name
        return self.new_entry(dxfattribs)

    def remove(self, name: str) -> None:
        """ Remove table-entry from table and entitydb by name. """
        key = self.key(name)
        entries = self.get(name)  # type: List[DXFEntity]
        for entry in entries:
            self.entitydb.delete_entity(entry)
        del self.entries[key]

    def __iter__(self) -> Iterable['DXFEntity']:
        for entries in self.entries.values():
            yield from iter(entries)

    def _flatten(self):
        for entries in self.entries.values():
            yield from iter(entries)

    def __len__(self):
        # calling __iter__() invokes recursion!
        return len(list(self._flatten()))

    def new_entry(self, dxfattribs: dict) -> 'DXFEntity':
        """ Create new table-entry of type 'self._dxfname', and add new entry
        to table.

        Does not check if an entry dxfattribs['name'] already exists!
        Duplicate entries are possible for Viewports.
        """
        entry = self.dxffactory.create_db_entry(self._head.dxf.name, dxfattribs)
        self._append(entry)
        return entry

    def duplicate_entry(self, name: str, new_name: str) -> 'DXFEntity':
        raise NotImplementedError()

    def _append(self, entry: 'DXFEntity') -> None:
        key = self.key(entry)
        if key in self.entries:
            self.entries[key].append(entry)  # type: List[DXFEntity]
        else:
            self.entries[key] = [entry]  # store list of VPORT

    def _update_owner_handles(self) -> None:
        owner_handle = self._head.dxf.handle
        for entries in self.entries.values():
            for entry in entries:
                entry.dxf.owner = owner_handle

    def get_config(self, name: str) -> List['DXFEntity']:
        return self.entries[self.key(name)]

    def delete_config(self, name: str) -> None:
        self.remove(name)
