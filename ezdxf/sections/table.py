# Purpose: tables contained in tables sections
# Created: 13.03.2011
# Copyright (C) , Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from ..tools.c23 import isstring
from ..lldxf.extendedtags import ExtendedTags
from ..lldxf.const import DXFTableEntryError, DXFStructureError, DXFAttributeError, Error

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


def tablename(dxfname):
    """ Translate DXF-table-name to attribute-name. ('LAYER' -> 'LAYERS') """
    name = dxfname.upper()
    return TABLENAMES.get(name, name + 'S')


class Table(object):
    def __init__(self, entities, drawing):
        self._table_header = None
        self._dxfname = None
        self._drawing = drawing
        self._table_entries = []
        self._build_table_entries(iter(entities))

    # start public interface

    @staticmethod
    def key(entity):
        if not isstring(entity):
            entity = entity.dxf.name
        return entity.lower()  # table key is lower case

    @property
    def name(self):
        return tablename(self._dxfname)

    def has_entry(self, name):
        """ Check if an table-entry 'name' exists. """
        key = self.key(name)
        return any(self.key(entry) == key for entry in self)

    __contains__ = has_entry

    def new(self, name, dxfattribs=None):
        if self.has_entry(name):
            raise DXFTableEntryError('%s %s already exists!' % (self._dxfname, name))
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['name'] = name
        return self.new_entry(dxfattribs)

    def get(self, name):
        """ Get table-entry by name as WrapperClass(). """
        key = self.key(name)
        for entry in iter(self):
            if self.key(entry) == key:
                return entry
        raise DXFTableEntryError(name)

    def remove(self, name):
        """ Remove table-entry from table and entitydb by name. """
        entry = self.get(name)
        handle = entry.dxf.handle
        self.remove_handle(handle)

    def __len__(self):
        return len(self._table_entries)

    def __iter__(self):
        for handle in self._table_entries:
            yield self.get_table_entry_wrapper(handle)

    # end public interface

    def _build_table_entries(self, entities):
        table_head = next(entities)
        if table_head[0].value != 'TABLE':
            raise DXFStructureError("Critical structure error in TABLES section.")
        self._dxfname = table_head[1].value
        self._table_header = ExtendedTags(table_head)  # do not store the table head in the entity database
        for table_entry in entities:
            self._append_entry_handle(table_entry.get_handle())


    @property
    def entitydb(self):
        return self._drawing.entitydb

    @property
    def handles(self):
        return self._drawing.entitydb.handles

    @property
    def dxffactory(self):
        return self._drawing.dxffactory

    def _iter_table_entries_as_tags(self):
        """ Iterate over table-entries as Tags(). """
        return (self.entitydb[handle] for handle in self._table_entries)

    def new_entry(self, dxfattribs):
        """ Create new table-entry of type 'self._dxfname', and add new entry
        to table.

        Does not check if an entry dxfattribs['name'] already exists!
        Duplicate entries are possible for Viewports.
        """
        handle = self.handles.next()
        entry = self.dxffactory.new_entity(self._dxfname, handle, dxfattribs)
        self._add_entry(entry)
        return entry

    def _add_entry(self, entry):
        """ Add table-entry to table and entitydb. """
        if isinstance(entry, ExtendedTags):
            tags = entry
        else:
            tags = entry.tags
        handle = self.entitydb.add_tags(tags)
        self._append_entry_handle(handle)

    def _append_entry_handle(self, handle):
        if handle not in self._table_entries:
            self._table_entries.append(handle)

    def get_table_entry_wrapper(self, handle):
        tags = self.entitydb[handle]
        return self.dxffactory.wrap_entity(tags)

    def write(self, tagwriter):
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

    def _update_owner_handles(self):
        if self._drawing.dxfversion <= 'AC1009':
            return  # no owner handles
        owner_handle = self._table_header.get_handle()
        for entry in iter(self):
            if not entry.supports_dxf_attrib('owner'):
                raise DXFAttributeError(repr(entry))
            entry.dxf.owner = owner_handle

    def _update_meta_data(self):
        count = len(self)
        if self._drawing.dxfversion > 'AC1009':
            subclass = self._table_header.get_subclass('AcDbSymbolTable')
        else:
            subclass = self._table_header.noclass
        subclass.set_first(70, count)

    def remove_handle(self, handle):
        """ Remove table-entry from table and entitydb by handle. """
        self._table_entries.remove(handle)
        del self.entitydb[handle]

    def audit(self, auditor):
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
    def get_shx(self, shxname):
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

    def find_shx(self, shxname):
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
    def new(self, name, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['name'] = name
        return self.new_entry(dxfattribs)

    def get_config(self, name):
        key_func = self.key
        search_key = key_func(name)
        return [entry for entry in self if search_key == key_func(entry)]

    def delete_config(self, name):
        for entry in self.get_config(name):
            self.remove_handle(entry.dxf.handle)

