# Purpose: drawing module
# Created: 11.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from datetime import datetime
import io

from . import database
from .lldxf.tags import TagIterator, DXFTag
from .lldxf.const import DXFVersionError
from .dxffactory import dxffactory
from .templates import TemplateLoader
from .options import options
from .tools.codepage import tocodepage, toencoding
from .sections import Sections
from .tools.juliandate import juliandate


class Drawing(object):
    """ The Central Data Object
    """
    def __init__(self, tagreader):
        """ Create a new drawing. """

        def get_rootdict():
            roothandle = self.sections.objects.roothandle()
            return self.dxffactory.wrap_entity(self.entitydb[roothandle])
        self._is_binary_data_compressed = False
        self.dxffactory = None  # readonly - set by _bootstraphook()
        self.dxfversion = 'AC1009'  # readonly - set by _bootstraphook()
        self.encoding = 'cp1252'  # read/write - set by _bootstraphook()
        self.filename = None  # read/write
        self.entitydb = database.factory(debug=options.debug)
        self.sections = Sections(tagreader, self)
        self._groups = None
        if self.dxfversion > 'AC1009':
            self.rootdict = get_rootdict()
            self._groups = self.dxffactory.get_groups()
        else:
            if self.dxfversion < 'AC1009':  # legacy DXF version
                self._upgrade_to_ac1009()  # convert to DXF format AC1009 (DXF R12)
            self._enable_handles()
        self.layouts = self.dxffactory.get_layouts()

        if self.dxfversion > 'AC1009':
            # for ProE, which writes entities without owner tags (330)
            self.entities.repair_model_space(self.modelspace().layout_key)
            self.layouts.link_block_entities_into_layouts()

        if options.compress_binary_data:
            self.compress_binary_data()

    def compress_binary_data(self):
        if self.dxfversion > 'AC1009' and not self.is_binary_data_compressed:
            self.entitydb.compress_binary_data()
            self._is_binary_data_compressed = True

    @property
    def _handles(self):
        return self.entitydb.handles

    def _bootstraphook(self, header):
        # called from HeaderSection() object to update important dxf properties
        # before processing sections, which depends from this properties.
        self.dxfversion = header.get('$ACADVER', 'AC1009')
        seed = header.get('$HANDSEED', str(self._handles))
        self._handles.reset(seed)
        codepage = header.get('$DWGCODEPAGE', 'ANSI_1252')
        self.encoding = toencoding(codepage)
        self.dxffactory = dxffactory(self)

    @property
    def is_binary_data_compressed(self):
        return self._is_binary_data_compressed

    @property
    def header(self):
        return self.sections.header

    @property
    def layers(self):
        return self.sections.tables.layers

    @property
    def linetypes(self):
        return self.sections.tables.linetypes

    @property
    def styles(self):
        return self.sections.tables.styles

    @property
    def dimstyles(self):
        return self.sections.tables.dimstyles

    @property
    def ucs(self):
        return self.sections.tables.ucs

    @property
    def appids(self):
        return self.sections.tables.appids

    @property
    def views(self):
        return self.sections.tables.views

    @property
    def block_records(self):
        return self.sections.tables.block_records

    @property
    def viewports(self):
        return self.sections.tables.viewports

    @property
    def blocks(self):
        return self.sections.blocks

    @property
    def groups(self):
        if self._groups is not None:
            return self._groups
        else:
            raise Warning('Not supported for DXF version AC1009.')

    def modelspace(self):
        return self.layouts.modelspace()

    def layout(self, name=None):
        return self.layouts.get(name)

    def layout_names(self):
        return list(self.layouts.names())

    def delete_layout(self, name):
        if self.dxfversion > 'AC1009':
            if name not in self.layouts:
                raise ValueError("Layout '{}' does not exist.".format(name))
            else:
                self.layouts.delete(name)
        else:
            raise Warning('Not supported for DXF version AC1009.')

    def create_layout(self, name, dxfattribs=None):
        if self.dxfversion > 'AC1009':
            if name in self.layouts:
                raise ValueError("Layout '{}' already exists.".format(name))
            else:
                return self.layouts.create(name, dxfattribs)
        else:
            raise Warning('Not supported for DXF version AC1009.')

    def get_active_layout_key(self):
        if self.dxfversion > 'AC1009':
            try:
                active_layout_block_record = self.block_records.get('*Paper_Space')  # fixed name for the active layout
                return active_layout_block_record.dxf.handle
            except ValueError:
                return None
        else:
            return self.layout().layout_key  # AC1009 supports just one layout and this is the active one

    def get_active_entity_space_layout_keys(self):
        layout_keys = [self.modelspace().layout_key]
        active_layout_key = self.get_active_layout_key()
        if active_layout_key is not None:
            layout_keys.append(active_layout_key)
        return layout_keys

    @property
    def entities(self):
        return self.sections.entities

    @property
    def objects(self):
        return self.sections.objects

    def get_dxf_entity(self, handle):
        """ Get entity by *handle* from entity database.

        Low level access to DXF entities database. Raises *KeyError* if handle don't exists.
        Returns DXFEntity() or inherited.

        If you just need the raw DXF tags use::

            tags = Drawing.entitydb[handle]  # raises KeyError, if handle don't exist
            tags = Drawing.entitydb.get(handle)  # returns a default value, if handle don't exist (None by default)

        type of tags: ClassifiedTags()
        """
        return self.dxffactory.wrap_handle(handle)

    def _get_encoding(self):
        codepage = self.header.get('$DWGCODEPAGE', 'ANSI_1252')
        return toencoding(codepage)

    @staticmethod
    def new(dxfversion='AC1009'):
        finder = TemplateLoader(options.template_dir)
        stream = finder.getstream(dxfversion.upper())
        try:
            dwg = Drawing.read(stream)
        finally:
            stream.close()
        dwg._setup_metadata()
        return dwg

    def _setup_metadata(self):
        self.header['$TDCREATE'] = juliandate(datetime.now())

    @staticmethod
    def read(stream):
        """ Open an existing drawing. """
        tagreader = TagIterator(stream)
        return Drawing(tagreader)

    def saveas(self, filename):
        self.filename = filename
        self.save()

    def save(self):
        # noinspection PyArgumentList
        with io.open(self.filename, mode='wt', encoding=self.encoding) as fp:
            self.write(fp)

    def write(self, stream):
        self._create_appids()
        self._update_metadata()
        self.sections.write(stream)

    def cleanup(self, groups=True):
        """
        Cleanup drawing. Call it before saving the drawing but only if necessary, the process could take a while.

        :param groups: removes deleted and invalid entities from groups
        """
        if groups and self.groups is not None:
            self.groups.cleanup()

    def _update_metadata(self):
        self.header['$TDUPDATE'] = juliandate(datetime.now())
        self.header['$HANDSEED'] = str(self._handles)
        self.header['$DWGCODEPAGE'] = tocodepage(self.encoding)

    def _create_appids(self):
        def create_appid_if_not_exist(name, flags=0):
            if name not in self.appids:
                self.appids.create(name, {'flags': flags})

        if self.dxfversion > 'AC1009':
            create_appid_if_not_exist('HATCHBACKGROUNDCOLOR', 0)

    def _enable_handles(self):
        """ Enable 'handles' for DXF R12 to be consistent with later DXF versions.

        Write entitydb-handles into entity-tags.
        """
        def has_handle(tags, handle_code):
            for tag in tags.noclass:
                if tag.code == handle_code:
                    return True
            return False

        def put_handles_into_entity_tags():
            for handle, tags in self.entitydb.items():
                is_not_dimstyle = tags.noclass[0] != (0, 'DIMSTYLE')
                handle_code = 5 if is_not_dimstyle else 105  # legacy shit!!!
                if not has_handle(tags, handle_code):
                    tags.noclass.insert(1, DXFTag(handle_code, handle))  # handle should be the 2. tag

        if self.dxfversion > 'AC1009':
            return
        put_handles_into_entity_tags()
        self.header['$HANDLING'] = 1

    def _upgrade_to_ac1009(self):
        self.dxfversion = 'AC1009'
        self.header['$ACADVER'] = 'AC1009'
        # as far I know, nothing else to do
