#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: sections module
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from collections import OrderedDict
from .tags import TAG_STRING_FORMAT, DXFTag

from .header import HeaderSection

class Sections:
    def __init__(self, drawing, tagreader):
        self._drawing = drawing
        self.tagreader = tagreader
        self._sections = OrderedDict()
        self._setup_sections()
        del self.tagreader

    def __getitem__(self, key):
        return self._sections[key]

    def __contains__(self, key):
        return key in self._sections

    def __getattr__(self, key):
        try:
            return self._sections[key]
        except KeyError:
            raise AttributeError(key)

    def _setup_sections(self):
        def name(section):
            return section[1].value

        for section in iter_sections(self.tagreader):
            section_class = get_section_class(name(section))
            new_section = section_class(section, self._drawing)
            self._sections[new_section.name] = new_section

    def write(self, stream):
        def write_eof():
            stream.write('  0\nEOF\n')

        for section in self._sections.values():
            section.write(stream)
        write_eof()

def iter_sections(tagreader):
    while True:
        tag = next(tagreader)
        if tag == (0, 'EOF'):
            return
        assert tag == (0, 'SECTION')
        tags = [tag]
        while tag != (0, 'ENDSEC'):
            tag = next(tagreader)
            tags.append(tag)
        yield tags

class DefaultSection:
    def __init__(self, tags, drawing):
        self.tags = tags
        self.drawing = drawing

    @property
    def dxfengine(self):
        return self.drawing.dxfengine

    @property
    def name(self):
        return self.tags[1].value.lower()

    def write(self, stream):
        for tag in self.tags:
            stream.write(TAG_STRING_FORMAT % tag)

SECTIONMAP = {
    'HEADER': HeaderSection,
}

def get_section_class(name):
    return SECTIONMAP.get(name, DefaultSection)