#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: sections module
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from collections import OrderedDict
from .tags import TAG_STRING_FORMAT, DXFTag

from .defaultchunk import DefaultChunk, iterchunks
from .header import HeaderSection
from .tables import TablesSection

class Sections:
    def __init__(self, tagreader, drawing):
        self.drawing = drawing
        self._sections = OrderedDict()
        self._setup_sections(tagreader)

    def _setup_sections(self, tagreader):
        def name(section):
            return section[1].value

        for section in iterchunks(tagreader, stoptag='EOF', endofchunk='ENDSEC'):
            section_class = get_section_class(name(section))
            new_section = section_class(section, self.drawing)
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
    'HEADER': HeaderSection,
    'TABLES': TablesSection,
}

def get_section_class(name):
    return SECTIONMAP.get(name, DefaultChunk)