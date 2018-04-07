# Purpose: dxf objects wrapper, dxf-objects are non-graphical entities
# all dxf objects resides in the OBJECTS SECTION
# Created: 22.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals
__author__ = "mozman <me@mozman.at>"

from contextlib import contextmanager

from .dxfobjects import none_subclass
from .object_manager import ObjectManager
from ..lldxf.tags import DXFTag
from ..lldxf.extendedtags import ExtendedTags
from ..lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ..dxfentity import DXFEntity
from ..tools.c23 import isstring
from ..lldxf.const import DXFValueError, DXFKeyError

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
    # groups are not allowed in block definitions
    TEMPLATE = ExtendedTags.from_text(_GROUP_TPL)
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
            try:
                entity = wrap(handle)
                yield entity
            except KeyError:  # handle not in entity database, maybe entity were deleted; internal exception
                pass

    def __len__(self):
        return sum(1 for tag in self.AcDbGroup if tag.code == GROUP_ITEM_CODE)

    def __contains__(self, item):
        handle = item if isstring(item) else item.dxf.handle
        return handle in set(self.handles())

    def handles(self):
        return (tag.value for tag in self.AcDbGroup if tag.code == GROUP_ITEM_CODE)

    def get_name(self):
        group_table = self.dxffactory.wrap_handle(self.dxf.owner)  # returns DXFDictionary() and not GroupManager()!!!
        my_handle = self.dxf.handle
        for name, handle in group_table.items():
            if handle == my_handle:
                return name
        return None

    @contextmanager
    def edit_data(self):
        data = list(self)
        yield data
        self.set_data(data)

    def set_data(self, entities):
        entities = list(entities)  # for generators
        if not all_entities_on_same_layout(entities):
            raise DXFValueError("All entities have to be on the same layout (model space or any paper layout but not block).")
        self.clear()
        self.AcDbGroup.extend(DXFTag(GROUP_ITEM_CODE, entity.dxf.handle) for entity in entities)

    def extend(self, entities):
        with self.edit_data() as e:
            e.extend(entities)

    def clear(self):
        """ Remove all entity references, does not delete any drawing entities referenced by this group.
        """
        self.AcDbGroup.remove_tags((GROUP_ITEM_CODE,))

    def remove_invalid_handles(self):
        """ Remove invalid handles from group.

        Invalid handles: deleted entities, entities in a block layout
        """
        def handle_not_in_block_definition(handle):
            wrap = self.dxffactory.wrap_handle  # shortcut
            # owner block_record.layout is 0 if entity is in a block definition
            owner_handle = wrap(handle).dxf.owner
            return wrap(owner_handle).dxf.layout != 0

        db = self.entitydb  # faster local var
        valid_handles = [handle for handle in self.handles() if handle in db]
        self.clear()

        # If one entity is in a block layout remove all entities, because they have to be on the same layout
        if len(valid_handles) and handle_not_in_block_definition(valid_handles[0]):
            self.AcDbGroup.extend(DXFTag(GROUP_ITEM_CODE, handle) for handle in valid_handles)


def all_entities_on_same_layout(entities):
    """ Check if all entities are on the same layout (model space or any paper layout but not block).
    """
    owners = set(entity.dxf.owner for entity in entities)
    return len(owners) < 2  # 0 for no entities; 1 for all entities on the same layout


class GroupManager(ObjectManager):
    def __init__(self, drawing):
        super(GroupManager, self).__init__(drawing, dict_name='ACAD_GROUP', object_type='GROUP')
        self._next_unnamed_number = 0

    def groups(self):
        for name, group in self:
            yield group

    def next_name(self):
        name = self._next_name()
        while name in self:
            name = self._next_name()
        return name

    def _next_name(self):
        self._next_unnamed_number += 1
        return "*A{}".format(self._next_unnamed_number)

    def new(self, name=None, description="", selectable=1):
        if name in self:
            raise DXFValueError("GROUP '{}' already exists.".format(name))
        unnamed = 0
        if name is None:
            name = self.next_name()
            unnamed = 1
        # The group name isn't stored in the group entity itself.
        owner = self.object_dict.dxf.handle
        group = self.objects.create_new_dxf_entity(self.object_type, dxfattribs={
            'owner': owner,
            'description': description,
            'unnamed': unnamed,
            'selectable': selectable,
        })
        self.object_dict.add(name, group.dxf.handle)
        group.set_reactors([owner])
        return group

    def delete(self, group):
        """
        Delete GROUP by name or Group() object.

        """
        if isstring(group):  # delete group by name
            super(GroupManager, self).delete(group)
        else:  # group should be a DXFEntity
            group_handle = group.dxf.handle
            for name, _group in self:
                if group_handle == _group.dxf.handle:
                    super(GroupManager, self).delete(name)
                    return
            raise DXFValueError("GROUP not in group table registered.")

    def cleanup(self):
        """
        Removes invalid handles in all groups and removes empty groups.

        """
        empty_groups = []
        for name, group in self:
            group.remove_invalid_handles()
            if not len(group):  # remove empty group
                # do not delete groups while iterating over groups!
                empty_groups.append(name)

        # now delete emtpy groups
        for name in empty_groups:
            self.delete(name)
