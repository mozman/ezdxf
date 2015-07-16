# Purpose: dxf objects wrapper, dxf-objects are non-graphical entities
# all dxf objects resides in the OBJECTS SECTION
# Created: 22.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from contextlib import contextmanager

from ..tags import DXFTag
from ..classifiedtags import ClassifiedTags
from ..dxfattr import DXFAttr, DXFAttributes, DefSubclass
from ..dxfentity import DXFEntity
from .dxfobjects import none_subclass
from ..tools.c23 import isstring

_GROUP_TPL = """  0
GROUP
  5
0
330
0
100
AcDbGroup
300

 70
     1
 71
     1
"""
GROUP_ITEM_CODE = 340


class DXFGroup(DXFEntity):
    TEMPLATE = ClassifiedTags.from_text(_GROUP_TPL)
    DXFATTRIBS = DXFAttributes(
        none_subclass,
        DefSubclass('AcDbGroup', {
            'description': DXFAttr(300),
            'unnamed': DXFAttr(70),
            'selectable': DXFAttr(71),
        }),
    )

    @property
    def AcDbGroup(self):
        return self.tags.subclasses[1]

    def __iter__(self):
        """ Yields all DXF entities of this group as wrapped DXFEntity (LINE, CIRCLE, ...) objects.
        """
        wrap = self.dxffactory.wrap_handle
        for handle in self.handles():
            yield wrap(handle)

    def __len__(self):
        return sum(1 for tag in self.AcDbGroup if tag.code == GROUP_ITEM_CODE)

    def __contains__(self, item):
        handle = item if isstring(item) else item.dxf.handle
        return handle in set(self.handles())

    def handles(self):
        return (tag.value for tag in self.AcDbGroup if tag.code == GROUP_ITEM_CODE)

    def get_name(self):
        owner_dict = self.dxffactory.wrap_handle(self.dxf.owner)
        my_handle = self.dxf.handle
        for name, handle in owner_dict.items():
            if handle == my_handle:
                return name
        return None

    @contextmanager
    def edit_data(self):
        data = list(self)
        yield data
        self.set_data(data)

    def set_data(self, data):
        def all_same_layout():
            """ Check if all entities in data are on the same layout.
            """
            handles = {}
            for entity in data:
                handles[entity.dxf.owner] = 1
            return sum(handles.values()) < 2  # 0 for no entities; 1 for all entities on the same layout

        if not all_same_layout():
            raise ValueError("All entities have to be on the same layout (model space, paper space or block).")

        self.clear()
        self.AcDbGroup.extend(DXFTag(GROUP_ITEM_CODE, entity.dxf.handle) for entity in data)

    def clear(self):
        self.AcDbGroup.remove_tags((GROUP_ITEM_CODE,))


class DXFGroupTable(object):
    def __init__(self, dxfgroups):
        self.dxfgroups = dxfgroups  # AcDbDictionary
        self.objects_section = dxfgroups.drawing.objects
        self._next_unnamed_number = 0

    def __iter__(self):
        wrap = self.dxfgroups.dxffactory.wrap_handle
        for name, handle in self.dxfgroups.items():
            yield name, wrap(handle)

    def __len__(self):
        return len(self.dxfgroups)

    def __contains__(self, name):
        return name in self.dxfgroups

    def next_name(self):
        name_exists = True
        while name_exists:
            name = self._next_name()
            name_exists = name in self.dxfgroups
        return name

    def _next_name(self):
        self._next_unnamed_number += 1
        return "*A{}".format(self._next_unnamed_number)

    def add(self, name=None, description="", selectable=1):
        if name in self.dxfgroups:
            raise ValueError("Group '{}' already exists. Group name has to be unique.".format(name))
        unnamed = 0
        if name is None:
            name = self.next_name()
            unnamed = 1
        # The group name isn't stored in the group entity itself.
        group = self.objects_section.create_new_dxf_entity("GROUP", dxfattribs={
            'description': description,
            'unnamed': unnamed,
            'selectable': selectable,
        })
        self.dxfgroups[name] = group.dxf.handle
        group.dxf.owner = self.dxfgroups.dxf.handle  # group table is owner of group
        return group

    def get(self, name):
        for group_name, group in self:
            if name == group_name:
                return group
        raise KeyError("KeyError: '{}'".format(name))

    def delete(self, group):
        if isstring(group):  # delete group by name
            name = group
            group_handle = self.dxfgroups[name]
            del self.dxfgroups[name]
        else:  # group should be a DXFEntity
            group_handle = group.dxf.handle
            for name, _group in self:
                if group_handle == _group.dxf.handle:
                    del self.dxfgroups[name]
                    return
            raise ValueError("Group not in group table registered.")
        self._destroy_dxf_group_entity(group_handle)

    def _destroy_dxf_group_entity(self, handle):
        self.objects_section.remove_handle(handle)  # remove from entity space
        self.objects_section.entitydb.delete_handle(handle)  # remove from drawing database

    def clear(self):
        for name, group in self:  # destroy dxf entities
            self._destroy_dxf_group_entity(group.dxf.handle)
        self.dxfgroups.clear()  # delete all references

