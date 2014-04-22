# Purpose: entity space
# Created: 13.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License

from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"


class EntitySpace(list):
    """An EntitySpace is a collection of drawing entities.
    The ENTITY section is such an entity space, but also blocks.
    The EntitySpace stores only handles to the drawing entity database.
    """
    def __init__(self, entitydb):
        self._entitydb = entitydb

    def get_tags_by_handle(self, handle):
        return self._entitydb[handle]

    def store_tags(self, tags):
        try:
            handle = tags.get_handle()
        except ValueError:  # no handle tag available
            # handle is not stored in tags!!!
            handle = self._entitydb.handles.next()
        self.append(handle)
        self._entitydb[handle] = tags

    def write(self, stream):
        for handle in self:
            # write linked entities
            while handle is not None:
                tags = self._entitydb[handle]
                tags.write(stream)
                handle = tags.link

    def delete_entity(self, entity):
        self.remove(entity.dxf.handle)


class LayoutSpaces(object):
    def __init__(self, entitydb, dxfversion):
        self._layout_spaces = {}
        self._entitydb = entitydb
        if dxfversion == 'AC1009':
            self._get_key = lambda t: t.noclass.find_first(67, default=0)  # paper space value
        else:
            self._get_key = lambda t: t.noclass.find_first(330)  # owner tag, required

    def __iter__(self):
        """ Iterate over all layout entity spaces.
        """
        return iter(self._layout_spaces.values())

    def __getitem__(self, key):
        """ Get layout entity space by *key*.
        """
        return self._layout_spaces[key]

    def handles(self):
        """ Iterate over all handles in all entity spaces.
        """
        for entity_space in self:
            for handle in entity_space:
                yield handle

    def get_entity_space(self, key):
        """ Get entity space by *key* or create new entity space.
        """
        try:
            entity_space = self._layout_spaces[key]
        except KeyError:  # create new entity space
            entity_space = EntitySpace(self._entitydb)
            self._layout_spaces[key] = entity_space
        return entity_space

    def store_tags(self, tags):
        """ Store *tags* in associated layout entity space.
        """
        entity_space = self.get_entity_space(self._get_key(tags))
        entity_space.store_tags(tags)

    def write(self, stream):
        """ Write all entity spaces to *stream*.
        """
        for entity_space in self:
            entity_space.write(stream)

    def del_entity(self, entity):
        """ Delete *entity* from associated layout entity space.
        Type of *entity* has to be DXFEntity() or inherited.
        """
        key = self._get_key(entity.tags)
        try:
            entity_space = self._layout_spaces[key]
        except KeyError:  # ignore
            pass
        else:
            entity_space.delete_entity(entity)

    def del_entity_space(self, key):
        """ Delete layout entity space *key*.
        """
        del self._layout_spaces[key]
