# Purpose: entity space
# Created: 13.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # import forward declarations
    from ezdxf.eztypes2 import EntityDB, ExtendedTags, TagWriter, DXFEntity


class EntitySpace(list):
    """
    An EntitySpace is a collection of drawing entities.
    The ENTITY section is such an entity space, but also blocks.
    The EntitySpace stores only handles to the drawing entity database.

    """

    def __init__(self, entitydb: 'EntityDB'):
        self._entitydb = entitydb

    def get_tags_by_handle(self, handle: str) -> 'ExtendedTags':
        return self._entitydb[handle]

    def store_tags(self, tags: 'ExtendedTags') -> str:
        handle = tags.get_handle()
        self.append(handle)
        return handle

    def write(self, tagwriter: 'TagWriter') -> None:
        for handle in self:
            # write linked entities
            while handle is not None:
                tags = self._entitydb[handle]
                tagwriter.write_tags(tags)
                handle = tags.link

    def delete_entity(self, entity: 'DXFEntity') -> None:
        # do not delete database objects - entity space just manage handles
        self.remove(entity.dxf.handle)

    def delete_all_entities(self) -> None:
        # do not delete database objects - entity space just manage handles
        del self[:]

    def add_handle(self, handle: str) -> None:
        self.append(handle)
