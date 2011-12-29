#!/usr/bin/env python
#coding:utf-8
# Purpose: sections module
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from collections import OrderedDict
from .tags import TAG_STRING_FORMAT, DXFTag

from .defaultchunk import DefaultChunk, iterchunks
from .headersection import HeaderSection
from .tablessection import TablesSection
from .blockssection import BlocksSection
from .entitysection import EntitySection, ClassesSection, ObjectsSection

class Sections(object):
    def __init__(self, tagreader, drawing):
        self._sections = OrderedDict()
        self._setup_sections(tagreader, drawing)

    def _setup_sections(self, tagreader, drawing):
        def name(section):
            return section[1].value

        bootstrap = True
        for section in iterchunks(tagreader, stoptag='EOF', endofchunk='ENDSEC'):
            if bootstrap:
                new_section = HeaderSection(section)
                drawing._bootstraphook(new_section)
                new_section.set_headervar_factory(drawing.dxffactory.headervar_factory)
                bootstrap = False
            else:
                section_class = get_section_class(name(section))
                new_section = section_class(section, drawing)
            self._sections[new_section.name] = new_section

    def __getattr__(self, key):
        try:
            return self._sections[key]
        except KeyError:
            raise AttributeError(key)

    def write(self, stream):
        def write_eof():
            stream.write('  0\nEOF\n')

        for section in self._sections.values():
            section.write(stream)
        write_eof()

SECTIONMAP = {
    'CLASSES': ClassesSection,
    'TABLES': TablesSection,
    'BLOCKS': BlocksSection,
    'ENTITIES': EntitySection,
    'OBJECTS': ObjectsSection,
}

def get_section_class(name):
    return SECTIONMAP.get(name, DefaultChunk)