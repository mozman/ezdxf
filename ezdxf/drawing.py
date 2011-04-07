#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: drawing module
# Created: 11.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3
from datetime import datetime

from . import database
from .handle import HandleGenerator
from .tags import TagIterator, dxfinfo, DXFTag
from .dxffactory import dxffactory
from .templates import TemplateFinder
from .options import options
from .codepage import tocodepage, toencoding
from .sections import Sections
from .juliandate import juliandate

class Drawing:
    def __init__(self, tagreader):
        """ Create a new drawing. """
        def get_rootdict():
            roothandle = self.sections.objects.roothandle()
            return self.dxffactory.wrap_entity(self.entitydb[roothandle])

        self._dxfversion = 'AC1009' # readonly
        self.encoding = 'cp1252' # read/write
        self.filename = None # read/write
        self.entitydb = database.factory(debug=options.get('DEBUG', False))
        self.sections = Sections(tagreader, self)

        if self._dxfversion > 'AC1009':
            self.rootdict = get_rootdict()
        else:
            self._enable_handles()
        self.layouts = self.dxffactory.get_layouts()

    @property
    def _handles(self):
        return self.entitydb.handles

    def _bootstraphook(self, header):
        # called from HeaderSection() object to update important dxf properties
        # before processing sections, which depends from this properties.
        self._dxfversion = header['$ACADVER']
        seed = header.get('$HANDSEED', self._handles.seed)
        self._handles.reset(seed)
        codepage = header.get('$DWGCODEPAGE', 'ANSI_1252')
        self.encoding = toencoding(codepage)
        self.dxffactory = dxffactory(self._dxfversion, self)

    @property
    def dxfversion(self):
        return self._dxfversion

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
    def viewports(self):
        return self.sections.tables.viewports

    @property
    def blocks(self):
        return self.sections.blocks

    def modelspace(self):
        return self.layouts.modelspace()

    def layout(self, name=None):
        return self.layouts.get(name)

    def layoutnames(self):
        return list(self.layouts.names())

    @property
    def entities(self):
        return self.sections.entities

    def _get_encoding(self):
        codepage = self.header.get('$DWGCODEPAGE', 'ANSI_1252')
        return toencoding(codepage)

    @staticmethod
    def new(dxfversion='AC1009'):
        finder = TemplateFinder(options['templatedir'])
        try:
            stream = finder.getstream(dxfversion)
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
        with open(self.filename, 'wt', encoding=self.encoding) as fp:
            self.write(fp)

    def write(self, stream):
        self._update_metadata()
        self.sections.write(stream)

    def _update_metadata(self):
        self.header['$TDUPDATE'] = juliandate(datetime.now())
        self.header['$HANDSEED'] = self._handles.seed

    def _enable_handles(self):
        """ Enable 'handles' for DXF R12 to be consistent with later DXF versions.

        Write entitydb-handles into entits-tags.
        """
        def has_handle(entity):
            for tag in entity:
                if tag.code in (5, 105):
                    return True
            return False

        def put_handles_into_entity_tags():
            for handle, entity in self.entitydb.items():
                if not has_handle(entity):
                    code = 5 if entity[0].value != 'DIMSTYLE' else 105 # legacy shit!!!
                    # handle should be the second tag
                    entity.insert(1, DXFTag(code, handle))

        if self._dxfversion != 'AC1009':
            return
        put_handles_into_entity_tags()
        self.header['$HANDLING'] = 1
