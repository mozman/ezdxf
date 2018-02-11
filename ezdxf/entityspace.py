# Purpose: entity space
# Created: 13.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals


class EntitySpace(list):
    """
    An EntitySpace is a collection of drawing entities.
    The ENTITY section is such an entity space, but also blocks.
    The EntitySpace stores only handles to the drawing entity database.
    """
    def __init__(self, entitydb):
        self._entitydb = entitydb

    def get_tags_by_handle(self, handle):
        return self._entitydb[handle]

    def store_tags(self, tags):
        handle = tags.get_handle()
        self.append(handle)
        return handle

    def write(self, tagwriter):
        for handle in self:
            # write linked entities
            while handle is not None:
                tags = self._entitydb[handle]
                tagwriter.write_tags(tags)
                handle = tags.link

    def delete_entity(self, entity):
        # do not delete database objects - entity space just manage handles
        self.remove(entity.dxf.handle)

    def delete_all_entities(self):
        # do not delete database objects - entity space just manage handles
        del self[:]

    def add_handle(self, handle):
        self.append(handle)
