# Purpose: DXF structure loader and validator
# Created: 25.01.2018
# Copyright (C) 2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"
import logging
from .const import DXFStructureError
from .tags import group_tags
from .extendedtags import ExtendedTags
from .validator import entity_structure_validator
from .. import options

logger = logging.getLogger('ezdxf')


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

            entity = ExtendedTags(entity)
            database.add_tags(entity)
        yield entity


def fill_database(database, sections, dxffactory=None):
    post_read_tags_fixer = None if dxffactory is None else dxffactory.post_read_tags_fixer
    for name in ['TABLES', 'ENTITIES', 'BLOCKS', 'OBJECTS']:
        if name in ('ENTITIES', 'BLOCKS'):
            fix_tags = post_read_tags_fixer
        else:
            fix_tags = None
        if name in sections:
            section = sections[name]
            # entities stored in the database are converted from Tags() to ExtendedTags()
            for index, entity in enumerate(load_dxf_entities_into_database(database, section)):
                if fix_tags is not None and isinstance(entity, ExtendedTags):
                    fix_tags(entity)
                section[index] = entity
