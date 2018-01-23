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
    Divide input tag stream from tagger into DXF entities. Each DXF entity starts with a DXF structure (0, ...) tag, and
    ends before the next DXF structure tag.

    Generated structure:

    each entity is a Tags() object

    [
        [entity, entity, ...],  # 1. section
        [entity, entity, ...],  # 2. section
        [entity, entity, ...],  # 3. section
        ...
    ]

    [
        [(0, 'SECTION'), (2, 'HEADER'), .... ],
        [(0, 'SECTION'), (2, 'CLASSES')], [(0, 'CLASS'), ...], [(0, 'CLASS'), ...]],
        [(0, 'SECTION'), (2, 'TABLES')], [(0, 'TABLE'), (2, 'VPORT')], [(0, 'VPORT'), ...], ... , [(0, 'ENDTAB')]],
        ...
        [(0, 'SECTION'), (2, 'OBJECTS')], ...]
    ]

    Function expects a valid DXF structure, use ezdxf.lldxf.validator.structure_validator() to filter input.

    Args:
        tagger: generates DXFTag() entities from input data

    Returns:
        list if sections, each section is a list of DXF entity tag groups
    """
    sections = []
    section = []
    for entity in group_tags(tagger):
        tag = entity[0]
        if tag == (0, 'SECTION'):
            section = [entity]
        elif tag == (0, 'ENDSEC'):  # not collected
            sections.append(section)
            section = []  # collect tags outside of sections, but ignore it
        elif tag == (0, 'EOF'):  # not collected
            pass
        else:
            section.append(entity)
    return sections


class Sections(object):
    def __init__(self, tagreader, drawing):
        self._sections = {}
        self._setup_sections(tagreader, drawing)
        self._create_required_sections(drawing)
        if 'entities' not in self._sections:
            raise DXFStructureError('Mandatory ENTITIES section not found.')

    def __iter__(self):
        return iter(self._sections.values())

    def _setup_sections(self, tagreader, drawing):
        bootstrap = True
        for section_tags in iter_chunks(tagreader, stoptag='EOF', endofchunk='ENDSEC'):
            name_tag = section_tags[1]
            if name_tag.code != 2:
                raise DXFStructureError("Invalid first section tag: ({0.code}, {0.value})".format(name_tag))

            if bootstrap:
                if name_tag != (2, 'HEADER'):
                    new_section = HeaderSection(None)
                else:
                    new_section = HeaderSection(section_tags)
                    section_tags = None  # this tags are done
                drawing._bootstraphook(new_section)
                new_section.set_headervar_factory(drawing.dxffactory.headervar_factory)
                bootstrap = False
                self._sections[new_section.name] = new_section

            if section_tags is not None:
                section_class = get_section_class(name_tag.value)
                new_section = section_class(section_tags, drawing)
                self._sections[new_section.name] = new_section

    def _create_required_sections(self, drawing):
        if 'blocks' not in self:
            self._sections['blocks'] = BlocksSection(tags=None, drawing=drawing)
        if 'tables' not in self:
            self._sections['tables'] = TablesSection(tags=None, drawing=drawing)
        if drawing.dxfversion > 'AC1009':  # required sections for DXF versions newer than R12 (AC1009)
            if 'classes' not in self:
                self._sections['classes'] = ClassesSection(tags=None, drawing=drawing)

    def __contains__(self, item):
        return item in self._sections

    def __getattr__(self, key):
        try:
            return self._sections[key]
        except KeyError:  # internal exception
            # DXFStructureError because a requested section is not present, maybe a typo, but usual a hint for an
            # invalid DXF file.
            raise DXFStructureError('{} section not found'.format(key.upper()))

    def get(self, name):
        return self._sections.get(name, None)

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
        del self._sections[name.lower()]


SECTION_MAP = {
    'CLASSES': ClassesSection,
    'TABLES': TablesSection,
    'BLOCKS': BlocksSection,
    'ENTITIES': EntitySection,
    'OBJECTS': ObjectsSection,
}

KNOWN_SECTIONS = ('header', 'classes', 'tables', 'blocks', 'entities', 'objects', 'thumbnailimage', 'acdsdata')


def get_section_class(name):
    default_class = CompressedDefaultChunk if options.compress_default_chunks else DefaultChunk
    return SECTION_MAP.get(name, default_class)
