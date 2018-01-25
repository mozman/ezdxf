# Purpose: sections module
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"
import logging
from .header import HeaderSection
from .tables import TablesSection
from .blocks import BlocksSection
from .classes import ClassesSection
from .objects import ObjectsSection
from .entities import EntitySection
from .unsupported import UnsupportedSection
from ..lldxf.const import DXFStructureError

logger = logging.getLogger('ezdxf')
KNOWN_SECTIONS = ('HEADER', 'CLASSES', 'TABLES', 'BLOCKS', 'ENTITIES', 'OBJECTS', 'THUMBNAILIMAGE', 'ACDSDATA')


class Sections(object):
    def __init__(self, sections, drawing, header=None):
        self._sections = {'HEADER': header if header is not None else HeaderSection(tags=None)}
        self._setup_sections(sections, drawing)

    def __iter__(self):
        return iter(self._sections.values())

    @staticmethod
    def key(name):
        return name.upper()

    def _setup_sections(self, sections, drawing):
        # required sections
        self._sections['TABLES'] = TablesSection(sections.get('TABLES', None), drawing)
        self._sections['BLOCKS'] = BlocksSection(sections.get('BLOCKS', None), drawing)
        self._sections['ENTITIES'] = EntitySection(sections.get('ENTITIES', None), drawing)
        if drawing.dxfversion > 'AC1009':
            # required sections
            self._sections['CLASSES'] = ClassesSection(sections.get('CLASSES', None), drawing)
            self._sections['OBJECTS'] = ObjectsSection(sections.get('OBJECTS', None), drawing)
            # sections just stored, if exists
            if 'THUMBNAILIMAGE' in sections:
                self._sections['THUMBNAILIMAGE'] = UnsupportedSection(sections['THUMBNAILIMAGE'], drawing)
            if 'ACDSDATA' in sections:
                self._sections['ACDSDATA'] = UnsupportedSection(sections['ACDSDATA'], drawing)

        for section_name in sections.keys():
            if section_name not in KNOWN_SECTIONS:
                logging.info('Found unknown SECTION: "{}", removed by ezdxf on saving!'.format(section_name))

    def __contains__(self, item):
        return Sections.key(item) in self._sections

    def __getattr__(self, key):
        try:
            return self._sections[Sections.key(key)]
        except KeyError:  # internal exception
            # DXFStructureError because a requested section is not present, maybe a typo, but usual a hint for an
            # invalid DXF file.
            raise DXFStructureError('{} section not found'.format(key.upper()))

    def get(self, name):
        return self._sections.get(Sections.key(name), None)

    def names(self):
        return list(self._sections.keys())

    def write(self, tagwriter):
        write_order = list(KNOWN_SECTIONS)

        unknown_sections = frozenset(self._sections.keys()) - frozenset(KNOWN_SECTIONS)
        if unknown_sections:
            write_order.extend(unknown_sections)

        written_sections = []
        for section_name in KNOWN_SECTIONS:
            section = self._sections.get(section_name, None)
            if section is not None:
                section.write(tagwriter)
                written_sections.append(section.name)

        tagwriter.write_tag2(0, 'EOF')

    def delete_section(self, name):
        """ Delete a complete section, please delete only unnecessary sections like 'THUMBNAILIMAGE' or 'ACDSDATA'.
        """
        del self._sections[Sections.key(name)]
