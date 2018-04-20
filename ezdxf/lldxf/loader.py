# Purpose: DXF structure loader and validator
# Created: 25.01.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import logging
from .const import DXFStructureError
from .tags import group_tags
from .extendedtags import ExtendedTags
from .validator import entity_structure_validator
from .. import options

logger = logging.getLogger('ezdxf')

modern_post_load_tag_processors = {}
legacy_post_load_tag_processors = {}


def register_post_load_tag_processor(entity, processor, legacy=False):
    """
    Register functions to process from DXF file loaded tags.

    Args:
        entity: DXF type like 'LINE' or 'VERTEX'
        processor: function with one parameter 'tags'
        legacy: use for legacy tag structure (DXF version <= AC1009) or modern tag structures

    """
    processors = legacy_post_load_tag_processors if legacy else modern_post_load_tag_processors
    processors[entity] = processor


def load_dxf_structure(tagger, ignore_missing_eof=False):
    """
    Divide input tag stream from tagger into DXF structure entities. Each DXF structure entity starts with a DXF
    structure (0, ...) tag, and ends before the next DXF structure tag.

    Generated structure:

    each entity is a Tags() object

    {
        'HEADER': [entity],                # 1. section, HEADER section contains only the SECTION head tag
        'CLASSES': [entity, entity, ...],  # 2. section
        'TABLES': [entity, entity, ...],   # 3. section
        ...
        'OBJECTS': [entity, entity, ...],
    }

    {
        'HEADER': [(0, 'SECTION'), (2, 'HEADER'), .... ],  # HEADER section contains only the SECTION head tag
        'CLASSES': [[(0, 'SECTION'), (2, 'CLASSES')], [(0, 'CLASS'), ...], [(0, 'CLASS'), ...]],
        'TABLES': [[(0, 'SECTION'), (2, 'TABLES')], [(0, 'TABLE'), (2, 'VPORT')], [(0, 'VPORT'), ...], ... , [(0, 'ENDTAB')]],
        ...
        'OBJECTS': [[(0, 'SECTION'), (2, 'OBJECTS')], ...]
    }

    Args:
        tagger: generates DXFTag() entities from input data
        ignore_missing_eof: raises DXFStructureError() if False and EOF tag is not present, set to True only in tests

    Returns:
        dict of sections, each section is a list of DXF structure entities as Tags() objects

    """
    def inside_section():
        if len(section):
            return section[0][0] == (0, 'SECTION')  # first entity, first tag
        return False

    def outside_section():
        if len(section):
            return section[0][0] != (0, 'SECTION')  # first entity, first tag
        return True

    sections = {}
    section = []
    eof = False
    for entity in group_tags(tagger):
        tag = entity[0]
        if tag == (0, 'SECTION'):
            if inside_section():
                raise DXFStructureError("DXFStructureError: missing ENDSEC tag.")
            if len(section):
                logger.warning('DXF Structure Warning: found tags outside a SECTION, ignored by ezdxf.')
            section = [entity]
        elif tag == (0, 'ENDSEC'):  # not collected
            if outside_section():
                raise DXFStructureError("DXFStructureError: found ENDSEC tag without previous SECTION tag.")
            section_header = section[0]
            if len(section_header) < 2 or section_header[1].code != 2:
                raise DXFStructureError('DXFStructureError: missing required section NAME tag (2, name) at start of section.')
            name_tag = section_header[1]
            sections[name_tag.value] = section
            section = []  # collect tags outside of sections, but ignore it
        elif tag == (0, 'EOF'):  # not collected
            if eof:
                logger.warning('DXF Structure Warning: found more than one EOF tags.')
            eof = True
        else:
            section.append(entity)
    if inside_section():
        raise DXFStructureError("DXFStructureError: missing ENDSEC tag.")
    if not eof and not ignore_missing_eof:
        raise DXFStructureError('DXFStructureError: missing EOF tag.')
    return sections


DATABASE_EXCLUDE = frozenset(['SECTION', 'ENDSEC', 'EOF', 'TABLE', 'ENDTAB', 'CLASS', 'ACDSRECORD', 'ACDSSCHEMA'])


def load_dxf_entities_into_database(database, dxf_entities):
    check_tag_structure = options.check_entity_tag_structures
    for entity in dxf_entities:
        if len(entity) == 0:
            raise DXFStructureError('Invalid empty DXF entity.')
        code, dxftype = entity[0]
        if code != 0:
            raise DXFStructureError('Invalid first tag in DXF entity, group code={} .'.format(code))
        if dxftype not in DATABASE_EXCLUDE:
            if check_tag_structure:
                entity = entity_structure_validator(entity)
            # execution point for coming feature:
            # TagArray() and TagDict() compiling
            entity = ExtendedTags(entity)
            database.add_tags(entity)
        yield entity


def fill_database(database, sections, dxfversion='AC1009'):
    post_processors = legacy_post_load_tag_processors if dxfversion <= 'AC1009' else modern_post_load_tag_processors
    for name in ['TABLES', 'ENTITIES', 'BLOCKS', 'OBJECTS']:
        if name in sections:
            section = sections[name]
            # entities stored in the database are converted from Tags() to ExtendedTags()
            for index, entity in enumerate(load_dxf_entities_into_database(database, section)):
                # entities not stored in database are still Tags() e.g. CLASS
                processor = post_processors.get(entity.dxftype())
                if processor:
                    processor(entity)
                section[index] = entity
