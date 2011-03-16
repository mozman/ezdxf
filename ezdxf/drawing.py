#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: drawing module
# Created: 11.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from . import database
from .handle import HandleGenerator
from .tags import TagIterator, dxfinfo
from .dxffactory import dxffactory
from .templates import TemplateFinder
from .options import options
from .codepage import tocodepage, toencoding
from .sections import Sections

class Drawing:
    def __init__(self, tagreader):
        """ Create a new drawing. """
        self._dxfversion = 'AC1009' # readonly
        self.encoding = 'cp1252' # read/write
        self.filename = None # read/write

        self.entitydb = database.factory(debug=options.get('DEBUG', False))
        self.handles = HandleGenerator()
        self.sections = Sections(tagreader, self)
        self.dxffactory = dxffactory(self._dxfversion, self)

    def read_header_vars(self, header):
        # called from HeaderSection() object to update important dxf properties
        # before processing sections, which depends from this properties.
        self._dxfversion = header['$ACADVER']
        seed = header.get('$HANDSEED', self.handles.seed)
        self.handles.reset(seed)
        codepage = header.get('$DWGCODEPAGE', 'ANSI_1252')
        self.encoding = toencoding(codepage)

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
    def blocks(self):
        return self.sections.tables.blocks

    @property
    def modelspace(self):
        return self.sections.entities

    def _get_encoding(self):
        codepage = self.header.get('$DWGCODEPAGE', 'ANSI_1252')
        return toencoding(codepage)

    @staticmethod
    def new(dxfversion='AC1009'):
        finder = TemplateFinder(options['templatedir'])
        try:
            stream = finder.getstream(dxfversion)
            return Drawing.read(stream)
        finally:
            stream.close()

    @staticmethod
    def read(stream):
        """ Open an existing drawing. """
        tagreader = TagIterator(stream)
        return Drawing(tagreader)

    def saveas(self, filename, encoding=None):
        if encoding is not None:
            self.encoding = encoding
        self.filename = filename
        self.save()

    def save(self):
        with open(self.filename, 'wt', encoding=self.encoding) as fp:
            self.write(fp)

    def write(self, stream):
        self._check_handling()
        self._update_handle_seed()
        self.sections.write(stream)

    def _check_handling(self):
        """ Only for DXF R12, if usage of handles is disabled, remove all entity
        handles.

        This is only possible if the drawing was created with another application
        (or my dxfwrite-package ;-), which doesn't use handles, but this package
        creates always new entities with handles, so we have to remove all
        handle-tags (code== 5|105) from new created entities.

        """
        if self.dxfversion == 'AC1009':
            try:
                if self.header['$HANDLING'] == 0:
                    self._remove_handles()
            except KeyError:
                self._remove_handles()

    def _remove_handles(self):
        """ Remove all handle-tags (code == 5|105) from entities and
        table-entries.
        """
        def remove_handle(entity):
            def remove(code):
                try:
                    index = entity.findfirst(code)
                    entity.pop(index)
                except ValueError:
                    pass

            if entity[0] == (2, 'DIMSTYLE'):
                remove(105)
            else:
                remove(5)

        try:
            del self.header['$HANDSEED']
        except KeyError:
            pass
        for entity in self.entitydb.values():
            remove_handle(entity)

    def _update_handle_seed(self):
        if '$HANDSEED' in self.header:
            self.header['$HANDSEED'] = self.handles.seed

