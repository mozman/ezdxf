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

    def build_link_structure(self, wrap_handle):
        def get_pocess_entities():
            db = self._entitydb
            for index, handle in enumerate(self):
                tags = db[handle]
                dxftype = tags.dxftype()
                if dxftype == 'INSERT':
                    entity = wrap_handle(handle)
                    if entity.dxf.attribs_follow == 1:
                        yield index
                elif dxftype == 'POLYLINE':
                    yield index

        def get_index_of_seqend(index):
            db = self._entitydb
            tags = db[self[index]]
            while tags.dxftype() != 'SEQEND':
                index += 1
                tags = db[self[index]]
            return index

        def link_entities(start_index, end_index):
            db = self._entitydb
            prev = db[self[start_index]]  # INSERT or POLYLINE entity
            index = start_index + 1  # first ATTRIB or VERTEX entity
            while index <= end_index:  # stop before SEQEND
                handle = self[index]
                prev.link = handle  # link from previous Entity to Entity at index
                self[index] = None  # set invalid handle, mark for delete
                prev = db[handle]  # get ClassifiedTags()
                index += 1

            prev.link = None  # just to be sure
            self[end_index] = None  # set invalid handle, mark for delete

        def remove_invalid_handles():
            valid_handles = [handle for handle in self if handle is not None]
            self[:] = valid_handles

        for index in list(get_pocess_entities()):
            seqend_index = get_index_of_seqend(index+1)
            link_entities(index, seqend_index)
        remove_invalid_handles()

