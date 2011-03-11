#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: drawing module
# Created: 11.03.2011
# Copyright (C) , Manfred Moitzi
# License: GPLv3

from .database import EntityDB
from .handle import HandleGenerator
from .dxfengine import dxfengine
from .templates import TemplateFinder
from .options import options

class Drawing:
    def __init__(self, dxfversion='AC1009', encoding='cp1252', template=None):
        """ Create a new drawing. """
        self.dxfversion = dxfversion
        self._handlegenerator = HandleGenerator()
        self.entitydb = EntityDB()
        self._setup(dxfversion, template)
        self.dxfengine = dxfengine(self.dxfversion)
        self.set_encoding(encoding)

    def _setup(self, dxfversion, templatefile):
        """ Init by importing a template drawing. """
        if templatefile is None:
            templatefile = self._get_template(dxfversion)

    def _get_template(self, dxfversion):
        finder = TemplateFinder(options['templatedir'])
        return finder.template_filepath(dxfversion)

    @staticmethod
    def open(stream):
        """ Open an existing drawing. """
        pass

