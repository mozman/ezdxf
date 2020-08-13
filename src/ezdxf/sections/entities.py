# Created: 13.03.2011
# Copyright (c) 2011-2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, List, Iterator
from itertools import chain

from ezdxf.lldxf.tags import DXFStructureError
from ezdxf.entities import entity_linker

if TYPE_CHECKING:
    from ezdxf.eztypes import (
        TagWriter, Drawing, DXFEntity, Tags, DXFTagStorage, DXFGraphic,
        BlockRecord,
    )


class StoredSection:
    def __init__(self, entities: List['Tags']):
        self.entities = entities

    def export_dxf(self, tagwriter: 'TagWriter'):
        # (0, SECTION) (2, NAME) is stored in entities
        for entity in self.entities:
            tagwriter.write_tags(entity)
        # ENDSEC not stored in entities !!!
        tagwriter.write_str('  0\nENDSEC\n')


class EntitySection:
    """ :class:`EntitiesSection` is just a proxy for :class:`Modelspace` and
    active :class:`Paperspace` linked together.
    """

    def __init__(self, doc: 'Drawing' = None,
                 entities: Iterable['DXFEntity'] = None):
        self.doc = doc
        if entities is not None:
            self._build(iter(entities))

    def __iter__(self) -> Iterable['DXFEntity']:
        """ Iterable for all entities of modelspace and active paperspace. """
        layouts = self.doc.layouts
        for entity in chain(layouts.modelspace(), layouts.active_layout()):
            yield entity

    def __len__(self) -> int:
        """ Returns count of all entities of modelspace and active paperspace.
        """
        layouts = self.doc.layouts
        return len(layouts.modelspace()) + len(layouts.active_layout())

    # none public interface

    def _build(self, entities: Iterator['DXFEntity']) -> None:
        section_head: 'DXFTagStorage' = next(entities)
        if section_head.dxftype() != 'SECTION' or section_head.base_class[
            1] != (2, 'ENTITIES'):
            raise DXFStructureError(
                "Critical structure error in ENTITIES section.")

        def add(entity: 'DXFGraphic'):
            handle = entity.dxf.owner
            # higher priority for owner handle
            if handle == msp_layout_key:
                paperspace = 0
            elif handle == psp_layout_key:
                paperspace = 1
            else:  # paperspace flag as fallback
                paperspace = entity.dxf.paperspace

            if paperspace:
                psp.add_entity(entity)
            else:
                msp.add_entity(entity)

        msp: 'BlockRecord' = self.doc.block_records.get('*Model_Space')
        psp: 'BlockRecord' = self.doc.block_records.get('*Paper_Space')
        msp_layout_key = msp.dxf.handle
        psp_layout_key = psp.dxf.handle
        linked_entities = entity_linker()
        # Don't store linked entities (VERTEX, ATTRIB, SEQEND) in entity space
        for entity in entities:
            if not linked_entities(entity):
                add(entity)

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        layouts = self.doc.layouts
        tagwriter.write_str("  0\nSECTION\n  2\nENTITIES\n")
        # Just write *Model_Space and the active *Paper_Space into the
        # ENTITIES section.
        layouts.modelspace().entity_space.export_dxf(tagwriter)
        layouts.active_layout().entity_space.export_dxf(tagwriter)
        tagwriter.write_tag2(0, "ENDSEC")
