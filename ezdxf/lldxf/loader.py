# Purpose: DXF structure loader and validator
# Created: 25.01.2018
# Copyright (C) 2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"
import logging
from ..lldxf.const import DXFStructureError
from ..lldxf.tags import group_tags

logger = logging.getLogger('ezdxf')
KNOWN_SECTIONS = ('HEADER', 'CLASSES', 'TABLES', 'BLOCKS', 'ENTITIES', 'OBJECTS', 'THUMBNAILIMAGE', 'ACDSDATA')


def load_dxf_structure(tagger, eof_error=True):
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
        eof_error: raises DXFStructureError() if True and EOF tag is not present, set to False only for testing

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
    if not eof and eof_error:
        raise DXFStructureError('DXFStructureError: missing EOF tag.')
    return sections
