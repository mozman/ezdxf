# Purpose: entity section
# Created: 13.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, List
from itertools import chain

from ezdxf.entitydb import EntitySpace
from .abstract2 import AbstractSection

if TYPE_CHECKING:  # import forward declarations
    from ezdxf.eztypes2 import TagWriter, Drawing, DXFEntity, Tags


class StoredSection:
    def __init__(self, entities: List['Tags']):
        self.entities = entities

    def export_dxf(self, tagwriter: 'TagWriter'):
        # (0, SECTION) (2, NAME) is stored in entities
        for entity in self.entities:
            tagwriter.write_tags(entity)
        # ENDSEC not stored in entities !!!
        tagwriter.write_str('  0\nENDSEC\n')


class EntitySection(AbstractSection):
    """
    The new EntitySection() collects only at startup the entities in the ENTITIES section. By creating the Layouts()
    object all entities form the EntitySection() moved into the Layout() objects, and the entity space of the
    EntitySection() will be deleted by calling EntitySection.clear().

    """
    name = 'ENTITIES'

    def __init__(self, doc: 'Drawing' = None, entities: Iterable['DXFEntity'] = None):
        super().__init__(EntitySpace(), entities, doc)

    def __iter__(self) -> 'DXFEntity':
        layouts = self.doc.layouts
        for entity in chain(layouts.modelspace(), layouts.active_layout()):
            yield entity

    def __len__(self) -> int:
        layouts = self.doc.layouts
        return len(layouts.modelspace()) + len(layouts.active_layout())

    # none public interface

    def clear(self) -> None:
        # remove entities for entities section -> stored in layouts
        del self._entity_space

    def model_space_entities(self) -> 'EntitySpace':
        # required for the drawing setup process
        return EntitySpace(self._filter_entities(paper_space=0))

    def active_layout_entities(self) -> 'EntitySpace':
        # required for the drawing setup process
        return EntitySpace(self._filter_entities(paper_space=1))

    def _filter_entities(self, paper_space: int = 0) -> Iterable['DXFEntity']:
        # required for the drawing setup process
        return (entity for entity in self._entity_space if entity.dxf.paperspace == paper_space)

    def delete_all_entities(self) -> None:
        layouts = self.doc.layouts
        layouts.modelspace().delete_all_entities()
        layouts.active_layout().delete_all_entities()

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        layouts = self.doc.layouts
        tagwriter.write_str("  0\nSECTION\n  2\nENTITIES\n")
        # Just write *Model_Space and the active *Paper_Space into the ENTITIES section.
        layouts.modelspace().entity_space.export_dxf(tagwriter)
        layouts.active_layout().entity_space.export_dxf(tagwriter)
        tagwriter.write_tag2(0, "ENDSEC")
