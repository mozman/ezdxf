# Purpose: sections module
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .defaultchunk import DefaultChunk, iter_chunks
from .headersection import HeaderSection
from .tablessection import TablesSection
from .blockssection import BlocksSection
from .entitysection import EntitySection, ClassesSection, ObjectsSection
from .options import options


class Sections(object):
    def __init__(self, tagreader, drawing):
        self._sections = {}
        self._setup_sections(tagreader, drawing)

    def __iter__(self):
        return iter(self._sections.values())

    def _setup_sections(self, tagreader, drawing):
        def name(section):
            return section[1].value

        bootstrap = True
        for section in iter_chunks(tagreader, stoptag='EOF', endofchunk='ENDSEC'):
            if bootstrap:
                new_section = HeaderSection(section)
                drawing._bootstraphook(new_section)
                new_section.set_headervar_factory(drawing.dxffactory.headervar_factory)
                bootstrap = False
            else:
                section_class = get_section_class(name(section))
                new_section = section_class(section, drawing)
            self._sections[new_section.name] = new_section

        self._create_required_sections(drawing)

    def _create_required_sections(self, drawing):
        if 'blocks' not in self:
            self._sections['blocks'] = BlocksSection(tags=None, drawing=drawing)

    def __contains__(self, item):
        return item in self._sections

    def __getattr__(self, key):
        try:
            return self._sections[key]
        except KeyError:
            raise AttributeError(key)

    def write(self, stream):
        def write_eof():
            stream.write('  0\nEOF\n')

        write_order = list(KNOWN_SECTIONS)

        unknown_sections = frozenset(self._sections.keys()) - frozenset(KNOWN_SECTIONS)
        if unknown_sections:
            write_order.extend(unknown_sections)
            options.logger.warning("Drawing contains unknown sections: {}".format(unknown_sections))

        written_sections = []
        for section_name in KNOWN_SECTIONS:
            section = self._sections.get(section_name, None)
            if section is not None:
                section.write(stream)
                written_sections.append(section.name)

        options.logger.debug("sections written: {}".format(written_sections))
        write_eof()

SECTION_MAP = {
    'CLASSES': ClassesSection,
    'TABLES': TablesSection,
    'BLOCKS': BlocksSection,
    'ENTITIES': EntitySection,
    'OBJECTS': ObjectsSection,
}

KNOWN_SECTIONS = ('header', 'classes', 'tables', 'blocks', 'entities', 'objects', 'thumbnailimage', 'acdsdata')

def get_section_class(name):
    return SECTION_MAP.get(name, DefaultChunk)