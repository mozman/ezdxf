# Purpose: entity section
# Created: 13.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable
from itertools import chain

from ezdxf.entityspace import EntitySpace

from .abstract import AbstractSection

if TYPE_CHECKING:  # import forward declarations
    from ezdxf.eztypes import ExtendedTags, Drawing, DXFEntity, TagWriter


class EntitySection(AbstractSection):
    """
    The new EntitySection() collects only at startup the entities in the ENTITIES section. By creating the Layouts()
    object all entities form the EntitySection() moved into the Layout() objects, and the entity space of the
    EntitySection() will be deleted by calling EntitySection.clear().

    """
    name = 'ENTITIES'

    def __init__(self, entities: Iterable['ExtendedTags'], drawing: 'Drawing'):
        super().__init__(EntitySpace(drawing.entitydb), entities, drawing)

    def __iter__(self) -> 'DXFEntity':
        layouts = self.drawing.layouts
        for entity in chain(layouts.modelspace(), layouts.active_layout()):
            yield entity

    def __len__(self) -> int:
        layouts = self.drawing.layouts
        return len(layouts.modelspace()) + len(layouts.active_layout())

    # none public interface

    def clear(self) -> None:
        # remove entities for entities section -> stored in layouts
        del self._entity_space

    def _setup_entities(self) -> Iterable['DXFEntity']:
        # required for the drawing setup process
        wrap = self.dxffactory.wrap_handle
        for handle in self._entity_space:
            yield wrap(handle)

    def model_space_entities(self) -> 'EntitySpace':
        # required for the drawing setup process
        es = EntitySpace(self.entitydb)
        es.extend(self._filter_entities(paper_space=0))
        return es

    def active_layout_entities(self) -> 'EntitySpace':
        # required for the drawing setup process
        es = EntitySpace(self.entitydb)
        es.extend(self._filter_entities(paper_space=1))
        return es

    def _filter_entities(self, paper_space: int = 0) -> Iterable[str]:
        # required for the drawing setup process
        return (entity.dxf.handle for entity in self._setup_entities() if
                entity.get_dxf_attrib('paperspace', 0) == paper_space)

    def delete_all_entities(self) -> None:
        layouts = self.drawing.layouts
        layouts.modelspace().delete_all_entities()
        layouts.active_layout().delete_all_entities()

    def write(self, tagwriter: 'TagWriter') -> None:
        tagwriter.write_str("  0\nSECTION\n  2\n%s\n" % self.name.upper())
        # Just write *Model_Space and the active *Paper_Space into the ENTITIES section.
        self.drawing.layouts.write_entities_section(tagwriter)
        tagwriter.write_tag2(0, "ENDSEC")
