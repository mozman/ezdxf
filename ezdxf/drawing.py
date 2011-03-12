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
from .codepage import tocodepage
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
        self._dxfversion = self._get_dxfversion()
        self.encoding = self._get_encoding()
        self.dxfengine = dxfengine(self._dxfversion)

    @property
    def dxfversion(self):
        return self._dxfversion

    def _get_dxfversion(self):
        return 'AC1009' # self.sections.header['$ACADVER']

    def _get_encoding(self):
        return 'cp1252' # toencoding(self.sections.header['$DWGCODEPAGE'])

    @staticmethod
    def new(self, dxfversion='AC1009', encoding='cp1252'):
        if template is None:
            finder = TemplateFinder(options['templatedir'])
            template = finder.filepath(dxfversion)
        with open(template, encoding=encoding):
            return self.open(fp)

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


