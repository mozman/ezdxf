# Purpose: DXF structure loader and validator
# Created: 25.01.2018
# Copyright (c) 2018-2019, Manfred Moitzi
# License: MIT License
import logging
from typing import Callable, Dict, Iterable, List, Union, TYPE_CHECKING
from collections import OrderedDict

from .const import DXFStructureError
from .tags import group_tags, DXFTag, Tags
from .extendedtags import ExtendedTags
from .validator import entity_structure_validator

from ezdxf.options import options

if TYPE_CHECKING:  # import forward declarations
    from ezdxf.entities.factory import EntityFactory
    from ezdxf.entities.dxfentity import DXFEntity

logger = logging.getLogger('ezdxf')

TagProcessor = Callable[[ExtendedTags], ExtendedTags]
modern_post_load_tag_processors = {}  # type: Dict[str, TagProcessor]
legacy_post_load_tag_processors = {}  # type: Dict[str, TagProcessor]

SectionDict = Dict[str, List[Union[Tags, ExtendedTags]]]


def load_dxf_structure(tagger: Iterable[DXFTag], ignore_missing_eof: bool = False) -> SectionDict:
    """
    Divide input tag stream from tagger into DXF structure entities. Each DXF structure entity starts with a DXF
    structure (0, ...) tag, and ends before the next DXF structure tag.

    Generated structure:

    each entity is a Tags() object

    {
        'HEADER': [entity],                # 1. section, HEADER section consist only of one entity
        'CLASSES': [entity, entity, ...],  # 2. section
        'TABLES': [entity, entity, ...],   # 3. section
        ...
        'OBJECTS': [entity, entity, ...],
    }

    {
        'HEADER': [(0, 'SECTION'), (2, 'HEADER'), .... ],  # HEADER section consist only of one entity
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

    def inside_section() -> bool:
        if len(section):
            return section[0][0] == (0, 'SECTION')  # first entity, first tag
        return False

    def outside_section() -> bool:
        if len(section):
            return section[0][0] != (0, 'SECTION')  # first entity, first tag
        return True

    sections = OrderedDict()  # type: SectionDict
    section = []  # type: List[Tags]
    eof = False
    # todo: possible improvement - ignore all end of structure tags
    # a (0, SECTION) tag could start a new section even without a preceding (0, ENDSEC) tag
    for entity in group_tags(tagger):
        tag = entity[0]
        if tag == (0, 'SECTION'):
            if inside_section():
                # todo: just log - end actual section and start a new one
                raise DXFStructureError("DXFStructureError: missing ENDSEC tag.")
            if len(section):
                logger.warning('DXF Structure Warning: found tags outside a SECTION, ignored by ezdxf.')
            section = [entity]
        elif tag == (0, 'ENDSEC'):  # not collected
            if outside_section():
                # todo: just log
                raise DXFStructureError("DXFStructureError: found ENDSEC tag without previous SECTION tag.")
            section_header = section[0]
            if len(section_header) < 2 or section_header[1].code != 2:  # this is important
                raise DXFStructureError(
                    'DXFStructureError: missing required section NAME tag (2, name) at start of section.')
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
        # todo: just log
        raise DXFStructureError("DXFStructureError: missing ENDSEC tag.")
    if not eof and not ignore_missing_eof:
        raise DXFStructureError('DXFStructureError: missing EOF tag.')
    return sections


EXCLUDE_STRUCTURE_CHECK = {'SECTION', 'ENDSEC', 'EOF', 'TABLE', 'ENDTAB', 'CLASS', 'ACDSRECORD', 'ACDSSCHEMA'}


def load_dxf_entities(dxf_entities: List[Tags], factory: 'EntityFactory') -> Iterable['DXFEntity']:
    check_tag_structure = options.check_entity_tag_structures
    for entity in dxf_entities:
        if len(entity) == 0:
            raise DXFStructureError('Invalid empty DXF entity.')
        code, dxftype = entity[0]
        if code != 0:
            raise DXFStructureError('Invalid first tag in DXF entity, group code={} .'.format(code))

        if check_tag_structure and (dxftype not in EXCLUDE_STRUCTURE_CHECK):
            entity = entity_structure_validator(entity)
        yield factory.load(entity)


def fill_database(sections: Dict, factory: 'EntityFactory') -> None:
    # CLASSES and HEADER have no EntityDB entries.
    for name in ['TABLES', 'CLASSES', 'ENTITIES', 'BLOCKS', 'OBJECTS']:
        if name in sections:
            section = sections[name]
            # entities stored in the database are converted from Tags() to ExtendedTags()
            for index, entity in enumerate(load_dxf_entities(section, factory)):
                # all entities are DXFEntity or inherited
                section[index] = entity
