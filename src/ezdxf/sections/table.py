# Copyright (c) 2011-2021, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, Iterator, Optional, List
from collections import OrderedDict

from ezdxf.lldxf import const
from ezdxf.entities.table import TableHead
from ezdxf.entities import factory

if TYPE_CHECKING:
    from ezdxf.eztypes import (
        TagWriter, EntityDB, Drawing, DXFEntity, Layer, LineType,
    )

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


def table_key(name: str) -> str:
    """ Unified table entry key. """
    # see also comments for ezdxf.lldxf.validator.is_valid_table_name()
    if not isinstance(name, str):
        raise TypeError('Name has to be a string.')
    return name.lower()  # table key is lower case


class Table:
    def __init__(self, doc: 'Drawing' = None,
                 entities: Iterable['DXFEntity'] = None):
        self.doc = doc
        self.entries = OrderedDict()
        self._head = None
        if entities is not None:
            self.load(iter(entities))

    def load(self, entities: Iterator['DXFEntity']) -> None:
        """ Loading interface. (internal API)"""
        self._head = next(entities)
        if self._head.dxftype() != 'TABLE':
            raise const.DXFStructureError(
                "Critical structure error in TABLES section.")
        for table_entry in entities:
            self._append(table_entry)

    @classmethod
    def new_table(cls, name: str, handle: str, doc: 'Drawing') -> 'Table':
        """ Create new table. (internal API)"""
        table = cls(doc)
        table._set_head(name, handle)
        return table

    def _set_head(self, name: str, handle: str = None) -> None:
        self._head = TableHead.new(
            handle, owner='0', dxfattribs={'name': name}, doc=self.doc)

    @property
    def head(self):
        """ Returns table head entry. """
        return self._head

    @staticmethod
    def key(name: str) -> str:
        """ Unified table entry key. """
        return table_key(name)

    @property
    def name(self) -> str:
        """ Table name like ``layers``. """
        return tablename(self._head.dxf.name)

    def has_entry(self, name: str) -> bool:
        """ Returns ``True`` if an table entry `name` exist. """
        return self.key(name) in self.entries

    __contains__ = has_entry

    def __len__(self) -> int:
        """ Count of table entries. """
        return len(self.entries)

    def __iter__(self) -> Iterable['DXFEntity']:
        """ Iterable of all table entries. """
        for e in self.entries.values():
            if e.is_alive:
                yield e

    def new(self, name: str, dxfattribs: dict = None) -> 'DXFEntity':
        """ Create a new table entry `name`.

        Args:
            name: name of table entry, case insensitive
            dxfattribs: additional DXF attributes for table entry

        """
        if self.has_entry(name):
            raise const.DXFTableEntryError(
                f'{self._head.dxf.name} {name} already exists!')
        dxfattribs = dxfattribs or {}
        dxfattribs['name'] = name
        dxfattribs['owner'] = self._head.dxf.handle
        return self.new_entry(dxfattribs)

    def get(self, name: str) -> 'DXFEntity':
        """ Get table entry `name` (case insensitive).
        Raises :class:`DXFValueError` if table entry does not exist.
        """
        key = self.key(name)
        entry = self.entries.get(key, None)
        if entry:
            return entry
        else:
            raise const.DXFTableEntryError(name)

    def remove(self, name: str) -> None:
        """ Removes table entry `name`. Raises :class:`DXFValueError`
        if table-entry does not exist.
        """
        key = self.key(name)
        entry = self.get(name)
        self.entitydb.delete_entity(entry)
        self.discard(key)

    def duplicate_entry(self, name: str, new_name: str) -> 'DXFEntity':
        """ Returns a new table entry `new_name` as copy of `name`,
        replaces entry `new_name` if already exist.

        Raises:
             DXFValueError: `name` does not exist

        """
        entry = self.get(name)
        entitydb = self.entitydb
        if entitydb:
            new_entry = entitydb.duplicate_entity(entry)
        else:  # only for testing!
            new_entry = entry.copy()
        new_entry.dxf.name = new_name
        self._append(new_entry)
        return new_entry

    def discard(self, name: str) -> None:
        """ Remove table entry without destroying object. (internal API) """
        del self.entries[self.key(name)]

    def replace(self, name: str, entry: 'DXFEntity') -> None:
        """ Replace table entry `name` by new `entry`. (internal API) """
        self.discard(name)
        self._append(entry)

    @property
    def entitydb(self) -> 'EntityDB':
        return self.doc.entitydb

    def new_entry(self, dxfattribs: dict) -> 'DXFEntity':
        """ Create new table-entry of type 'self._dxfname', and add new entry
        to table.

        Does not check if an entry dxfattribs['name'] already exists!
        Duplicate entries are possible for Viewports.
        """
        entry = factory.create_db_entry(self._head.dxf.name, dxfattribs,
                                        self.doc)
        self._append(entry)
        return entry

    def _append(self, entry: 'DXFEntity') -> None:
        """ Add a table entry, replaces existing entries with same name.
        (internal API).
        """
        self.entries[self.key(entry.dxf.name)] = entry

    def add_entry(self, entry: 'DXFEntity') -> None:
        """ Add a table `entry`, created by other object than this table.
        (internal API)
        """
        if entry.dxftype() != self._head.dxf.name:
            raise const.DXFTypeError(
                f'Invalid table entry type {entry.dxftype()} '
                f'for table {self.name}')
        name = entry.dxf.name
        if self.has_entry(name):
            raise const.DXFTableEntryError(
                f'{self._head.dxf.name} {name} already exists!')
        entry.doc = self.doc
        entry.owner = self._head.dxf.handle
        self._append(entry)

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        """ Export DXF representation. (internal API) """

        def prologue():
            self.update_owner_handles()
            # The table head itself has no owner and is therefore always '0':
            self._head.dxf.owner = '0'
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

    def update_owner_handles(self) -> None:
        owner_handle = self._head.dxf.handle
        for entry in self.entries.values():
            entry.dxf.owner = owner_handle

    def set_handle(self, handle: str):
        """ Set new `handle` for table, updates also :attr:`owner` tag of table
        entries. (internal API)
        """
        if self._head.dxf.handle is None:
            self._head.dxf.handle = handle
            self.update_owner_handles()


class LayerTable(Table):
    def new_entry(self, dxfattribs: dict) -> 'DXFEntity':
        layer: 'Layer' = super().new_entry(dxfattribs)
        if self.doc:
            layer.set_required_attributes()
        return layer


class LineTypeTable(Table):
    def new_entry(self, dxfattribs: dict) -> 'DXFEntity':
        pattern = dxfattribs.pop('pattern', [0.0])
        length = dxfattribs.pop('length', 0)  # required for complex types
        ltype: 'LineType' = super().new_entry(dxfattribs)
        ltype.setup_pattern(pattern, length)
        return ltype


class StyleTable(Table):
    def get_shx(self, shxname: str) -> 'DXFEntity':
        """ Get existing shx entry, or create a new entry.

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
        """ Find .shx shape file table entry, by a case insensitive search.

        A .shx shape file table entry has no name, so you have to search by the
        font attribute.

        Args:
            shxname: .shx shape file name

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
        """ Creat a new table entry. """
        dxfattribs = dxfattribs or {}
        dxfattribs['name'] = name
        return self.new_entry(dxfattribs)

    def remove(self, name: str) -> None:
        """ Remove table-entry from table and entitydb by name. """
        key = self.key(name)
        entries: List['DXFEntity'] = self.get(name)
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
        entry = factory.create_db_entry(self._head.dxf.name, dxfattribs,
                                        self.doc)
        self._append(entry)
        return entry

    def duplicate_entry(self, name: str, new_name: str) -> 'DXFEntity':
        raise NotImplementedError()

    def _append(self, entry: 'DXFEntity') -> None:
        key = self.key(entry.dxf.name)
        if key in self.entries:
            self.entries[key].append(entry)
        else:
            self.entries[key] = [entry]  # store list of VPORT

    def update_owner_handles(self) -> None:
        owner_handle = self._head.dxf.handle
        for entries in self.entries.values():
            for entry in entries:
                entry.dxf.owner = owner_handle

    def get_config(self, name: str) -> List['DXFEntity']:
        """ Returns a list of :class:`~ezdxf.entities.Viewport` objects, for
        the multi-viewport configuration `name`.
        """
        try:
            return self.entries[self.key(name)]
        except KeyError:
            raise const.DXFTableEntryError(name)

    def delete_config(self, name: str) -> None:
        """ Delete all :class:`~ezdxf.entities.Viewport` objects of the
        multi-viewport configuration `name`.
        """
        self.remove(name)
