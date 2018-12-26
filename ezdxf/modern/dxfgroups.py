# Created: 22.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT-License
from typing import TYPE_CHECKING, Iterable, Union, cast, List
from contextlib import contextmanager

from ezdxf.lldxf.types import DXFTag
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ezdxf.dxfentity import DXFEntity
from ezdxf.lldxf.const import DXFValueError

from .dxfobjects import none_subclass
from .object_manager import ObjectManager

if TYPE_CHECKING:
    from ezdxf.eztypes import Tags, Drawing

_GROUP_TPL = """0
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
    __slots__ = ()
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
    def AcDbGroup(self) -> 'Tags':
        return self.tags.subclasses[1]

    def __iter__(self) -> Iterable[DXFEntity]:
        """ Yields all DXF entities of this group as wrapped DXFEntity (LINE, CIRCLE, ...) objects.
        """
        wrap = self.dxffactory.wrap_handle
        for handle in self.handles():
            try:
                entity = wrap(handle)
                yield entity
            except KeyError:  # handle not in entity database, maybe entity were deleted; internal exception
                pass

    def __len__(self) -> int:
        return sum(1 for tag in self.AcDbGroup if tag.code == GROUP_ITEM_CODE)

    def __contains__(self, item: Union[str, DXFEntity]) -> bool:
        handle = item if isinstance(item, str) else item.dxf.handle
        return handle in set(self.handles())

    def handles(self) -> Iterable[str]:
        return (tag.value for tag in self.AcDbGroup if tag.code == GROUP_ITEM_CODE)

    def get_name(self):
        group_table = cast('DXFDictionary', self.dxffactory.wrap_handle(self.dxf.owner))
        my_handle = self.dxf.handle
        for name, handle in group_table.items():
            if handle == my_handle:
                return name
        return None

    @contextmanager
    def edit_data(self) -> List['DXFEntity']:
        data = list(self)
        yield data
        self.set_data(data)

    def set_data(self, entities: List['DXFEntity']) -> None:
        entities = list(entities)  # for generators
        if not all_entities_on_same_layout(entities):
            raise DXFValueError(
                "All entities have to be on the same layout (model space or any paper layout but not block).")
        self.clear()
        self.AcDbGroup.extend(DXFTag(GROUP_ITEM_CODE, entity.dxf.handle) for entity in entities)

    def extend(self, entities: Iterable['DXFEntity']) -> None:
        """
        Add `entities` to group.

        Args:
            entities: iterable of DXFEntity

        """
        with self.edit_data() as e:
            e.extend(entities)

    def clear(self) -> None:
        """
        Remove all entity references, does not delete any drawing entities referenced by this group.

        """
        self.AcDbGroup.remove_tags((GROUP_ITEM_CODE,))

    def remove_invalid_handles(self) -> None:
        """
        Remove invalid handles from group.

        Invalid handles are: deleted entities, entities in a block layout
        """

        def handle_not_in_block_definition(handle: str) -> bool:
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


def all_entities_on_same_layout(entities: Iterable['DXFEntity']):
    """
    Check if all entities are on the same layout (model space or any paper layout but not block).

    """
    owners = set(entity.dxf.owner for entity in entities)
    return len(owners) < 2  # 0 for no entities; 1 for all entities on the same layout


class GroupManager(ObjectManager):
    def __init__(self, drawing: 'Drawing'):
        super().__init__(drawing, dict_name='ACAD_GROUP', object_type='GROUP')
        self._next_unnamed_number = 0

    def groups(self) -> Iterable[DXFGroup]:
        for name, group in self:
            yield group

    def next_name(self) -> str:
        name = self._next_name()
        while name in self:
            name = self._next_name()
        return name

    def _next_name(self) -> str:
        self._next_unnamed_number += 1
        return "*A{}".format(self._next_unnamed_number)

    def new(self, name: str = None, description: str = "", selectable: int = 1) -> DXFGroup:
        if name in self:
            raise DXFValueError("GROUP '{}' already exists.".format(name))

        if name is None:
            name = self.next_name()
            unnamed = 1
        else:
            unnamed = 0
        # The group name isn't stored in the group entity itself.
        dxfattribs = {
            'description': description,
            'unnamed': unnamed,
            'selectable': selectable,
        }
        return cast(DXFGroup, self._new(name, dxfattribs))

    def delete(self, group: DXFGroup) -> None:
        """
        Delete GROUP by name or Group() object.

        """
        if isinstance(group, str):  # delete group by name
            super(GroupManager, self).delete(group)
        else:  # group should be a DXFEntity
            group_handle = group.dxf.handle
            for name, _group in self:
                if group_handle == _group.dxf.handle:
                    super(GroupManager, self).delete(name)
                    return
            raise DXFValueError("GROUP not in group table registered.")

    def cleanup(self) -> None:
        """
        Removes invalid handles in all groups and removes empty groups.

        """
        empty_groups = []
        for name, group in self:
            group.remove_invalid_handles()
            if not len(group):  # remove empty group
                # do not delete groups while iterating over groups!
                empty_groups.append(name)

        # now delete empty groups
        for name in empty_groups:
            self.delete(name)
