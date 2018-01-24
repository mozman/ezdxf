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
from ..lldxf.tags import group_tags

logger = logging.getLogger('ezdxf')
KNOWN_SECTIONS = ('HEADER', 'CLASSES', 'TABLES', 'BLOCKS', 'ENTITIES', 'OBJECTS', 'THUMBNAILIMAGE', 'ACDSDATA')


def loader(tagger):
    """
    Divide input tag stream from tagger into DXF structure entities. Each DXF structure entity starts with a DXF
    structure (0, ...) tag, and ends before the next DXF structure tag.

    Generated structure:

    each entity is a Tags() object

    {
        'HEADER': [entity, entity, ...],  # 1. section
        'CLASSES': [entity, entity, ...],  # 2. section
        'TABLES': [entity, entity, ...],  # 3. section
        ...
        'OBJECTS': [entity, entity, ...],
    }

    {
        'HEADER': [(0, 'SECTION'), (2, 'HEADER'), .... ],
        'CLASSES': [(0, 'SECTION'), (2, 'CLASSES')], [(0, 'CLASS'), ...], [(0, 'CLASS'), ...]],
        'TABLES': [(0, 'SECTION'), (2, 'TABLES')], [(0, 'TABLE'), (2, 'VPORT')], [(0, 'VPORT'), ...], ... , [(0, 'ENDTAB')]],
        ...
        'OBJECTS': [(0, 'SECTION'), (2, 'OBJECTS')], ...]
    }

    loader() expects a valid DXF structure, use ezdxf.lldxf.validator.structure_validator() to filter input.

    Args:
        tagger: generates DXFTag() entities from input data

    Returns:
        dict of sections, each section is a list of DXF structure entities as Tags() objects

    """
    sections = {}
    section = []
    for entity in group_tags(tagger):
        tag = entity[0]
        if tag == (0, 'SECTION'):
            section = [entity]
        elif tag == (0, 'ENDSEC'):  # not collected
            section_header = section[0]
            if len(section_header) < 2 or section_header[1].code != 2:
                raise DXFStructureError('DXFStructureError: missing required section name tag (2, name) at start of section.')
            name_tag = section_header[1]
            sections[name_tag.value] = section
            section = []  # collect tags outside of sections, but ignore it
        elif tag == (0, 'EOF'):  # not collected
            pass
        else:
            section.append(entity)
    return sections


class Sections(object):
    def __init__(self, tagreader, drawing):
        self._sections = {}
        sections = loader(tagreader)
        self._setup_sections(sections, drawing)

    def __iter__(self):
        return iter(self._sections.values())

    @staticmethod
    def key(name):
        return name.upper()

    def _setup_sections(self, sections, drawing):
        def _create_instance(name, cls):
            entities = sections.get(name, None)
            section = cls(entities, drawing=drawing)
            return section

        # setup header section, header section is special!
        header_entities = sections.get('HEADER', None)
        if header_entities is not None:
            header = HeaderSection(header_entities[0])  # all tags in the first DXF structure entity
            del sections['HEADER']
        else:
            header = HeaderSection(None)
        self._sections['HEADER'] = header
        drawing._bootstraphook(header)
        header.set_headervar_factory(drawing.dxffactory.headervar_factory)

        # required sections
        self._sections['TABLES'] = _create_instance('TABLES', TablesSection)
        self._sections['BLOCKS'] = _create_instance('BLOCKS', BlocksSection)
        self._sections['ENTITIES'] = _create_instance('ENTITIES', EntitySection)
        if drawing.dxfversion > 'AC1009':
            # required sections
            self._sections['CLASSES'] = _create_instance('CLASSES', ClassesSection)
            self._sections['OBJECTS'] = _create_instance('OBJECTS', ObjectsSection)
            # sections just stored, if exists
            if 'THUMBNAILIMAGE' in sections:
                self._sections['THUMBNAILIMAGE'] = UnsupportedSection(sections['THUMBNAILIMAGE'], drawing)
            if 'ACDSDATA' in sections:
                self._sections['ACDSDATA'] = UnsupportedSection(sections['ACDSDATA'], drawing)

        for section_name in sections.keys():
            if section_name not in KNOWN_SECTIONS:
                logging.info('Found unknown SECTION: "{}", removed by ezdxf if saving.'.format(section_name))

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
