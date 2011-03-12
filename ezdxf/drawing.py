#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: drawing module
# Created: 11.03.2011
# Copyright (C) , Manfred Moitzi
# License: GPLv3

from .database import EntityDB
from .handle import HandleGenerator
from .tags import TagIterator, dxfinfo
from .dxfengine import dxfengine
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
        self._handlegenerator = HandleGenerator()
        self.entitydb = EntityDB()
        self.sections = Sections(self, tagreader)
        self._dxfversion = self.header['$ACADVER']
        self.encoding = self._get_encoding()
        self.dxfengine = dxfengine(self._dxfversion)

    @property
    def header(self):
        return self.sections.header

    @property
    def dxfversion(self):
        return self._dxfversion

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
        self.sections.write(stream)


