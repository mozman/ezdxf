# Purpose: sections module
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .header import HeaderSection
from .tables import TablesSection
from .blocks import BlocksSection
from .classes import ClassesSection
from .objects import ObjectsSection
from .entities import EntitySection
from ..options import options
from ..lldxf.defaultchunk import DefaultChunk, iter_chunks, CompressedDefaultChunk
from ..lldxf.const import DXFStructureError
from ..lldxf.tags import group_tags


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


def section_as_tags_helper(dxf_structure_entities):
    """
    Just for refactoring ...
    """
    from ezdxf.lldxf.types import DXFTag
    for entity in dxf_structure_entities:
        for tag in entity:
            yield tag
    yield DXFTag(0, 'ENDSEC')


class Sections(object):
    def __init__(self, tagreader, drawing):
        self._sections = {}
        sections = loader(tagreader)
        self._setup_sections(sections, drawing)
        self._create_required_sections(drawing)
        if 'ENTITIES' not in self._sections:
            raise DXFStructureError('Mandatory ENTITIES section not found.')

    def __iter__(self):
        return iter(self._sections.values())

    @staticmethod
    def key(name):
        return name.upper()

    def _setup_sections(self, sections, drawing):
        def _create_instance(name, cls):
            entities = sections.get(name, None)
            section = cls(entities, drawing=drawing)
            if name in sections:
                del sections[name]
            return section

        # setup header section
        header_entities = sections.get('HEADER', None)
        if header_entities is not None:
            header = HeaderSection(header_entities[0])  # all tags in the first DXF structure entity
            del sections['HEADER']
        else:
            header = HeaderSection(None)
        self._sections['HEADER'] = header
        drawing._bootstraphook(header)
        header.set_headervar_factory(drawing.dxffactory.headervar_factory)

        if drawing.dxfversion > 'AC1009':
            self._sections['CLASSES'] = _create_instance('CLASSES', ClassesSection)

        for section_entities in sections.values():
            section_head = section_entities[0]
            name = section_head[1].value
            section_class = get_section_class(name)
            new_section = section_class(list(section_as_tags_helper(section_entities)), drawing)
            key = Sections.key(new_section.name)
            self._sections[key] = new_section

    def _create_required_sections(self, drawing):
        if 'BLOCKS' not in self:
            self._sections['BLOCKS'] = BlocksSection(tags=None, drawing=drawing)
        if 'TABLES' not in self:
            self._sections['TABLES'] = TablesSection(tags=None, drawing=drawing)
        if drawing.dxfversion > 'AC1009':  # required sections for DXF versions newer than R12 (AC1009)
            if 'CLASSES' not in self:
                self._sections['CLASSES'] = ClassesSection(entities=None, drawing=drawing)

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


SECTION_MAP = {
    'CLASSES': ClassesSection,
    'TABLES': TablesSection,
    'BLOCKS': BlocksSection,
    'ENTITIES': EntitySection,
    'OBJECTS': ObjectsSection,
}

KNOWN_SECTIONS = ('HEADER', 'CLASSES', 'TABLES', 'BLOCKS', 'ENTITIES', 'OBJECTS', 'THUMBNAILIMAGE', 'ACDSDATA')


def get_section_class(name):
    default_class = CompressedDefaultChunk if options.compress_default_chunks else DefaultChunk
    return SECTION_MAP.get(name, default_class)
