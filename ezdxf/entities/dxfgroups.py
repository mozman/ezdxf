# Created: 2019-02-19
# Copyright (c) 2019, Manfred Moitzi
# License: MIT-License
from typing import TYPE_CHECKING, Iterable, cast, Union, List
from contextlib import contextmanager

from ezdxf.lldxf.const import DXFValueError, SUBCLASS_MARKER, DXFTypeError
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from .dxfentity import base_class, SubclassProcessor, DXFEntity
from .dxfobj import DXFObject
from .factory import register_entity
from .objectcollection import ObjectCollection

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter
    from ezdxf.drawing2 import Drawing
    from .dxfentity import DXFNamespace

__all__ = ['DXFGroup']

acdb_group = DefSubclass('AcDbGroup', {
    'description': DXFAttr(300, default=''),  # Group description
    'unnamed': DXFAttr(70, default=1),  # 1 = Unnamed; 0 = Named
    'selectable': DXFAttr(71, default=1),  # 1 = Selectable; 0 = Not selectable
    # 340: Hard-pointer handle to entity in group (one entry per object)
})

GROUP_ITEM_CODE = 340


@register_entity
class DXFGroup(DXFObject):
    """
    groups are not allowed in block definitions
    """
    DXFTYPE = 'GROUP'
    DXFATTRIBS = DXFAttributes(base_class, acdb_group)

    def __init__(self, doc: 'Drawing' = None):
        super().__init__(doc)
        self._data = list()  # type: List[Union[str, DXFEntity]]

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor is None:
            return dxf
        tags = processor.load_dxfattribs_into_namespace(dxf, acdb_group)
        self.load_group(tags)
        return dxf

    def load_group(self, tags):
        for code, value in tags:
            if code == GROUP_ITEM_CODE:
                # first store handles, because at this point, not all objects are stored in the EntityDB,
                # at access convert the handle to DXFEntity
                try:
                    entity = self.entitydb[value]
                except KeyError:
                    entity = value  # store entity as handle string
                self._data.append(entity)

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        super().export_entity(tagwriter)
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_group.name)
        self.dxf.export_dxf_attribs(tagwriter, ['description', 'unnamed', 'selectable'], force=True)
        self.export_group(tagwriter)

    def export_group(self, tagwriter: 'TagWriter'):
        for entity in self._data:
            if isinstance(entity, str):
                handle = entity
            else:
                handle = entity.dxf.handle
            tagwriter.write_tag2(GROUP_ITEM_CODE, handle)

    def __iter__(self) -> Iterable[DXFEntity]:
        """ Yields all DXF entities of this group as wrapped DXFEntity (LINE, CIRCLE, ...) objects. """
        for index, entity in enumerate(self._data):
            if isinstance(entity, str):
                # replace handle string by DXFEntity
                entity = self.entitydb[entity]
                self._data[index] = entity
            yield entity

    def __len__(self) -> int:
        return len(self._data)

    def __contains__(self, item: Union[str, DXFEntity]) -> bool:
        handle = item if isinstance(item, str) else item.dxf.handle
        return handle in set(self.handles())

    def handles(self) -> Iterable[str]:
        return (entity.dxf.handle for entity in self)

    def get_name(self):
        group_table = cast('Dictionary', self.entitydb[self.dxf.owner])
        for name, entity in group_table.items():
            if entity is self:
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
        self._data = entities

    def extend(self, entities: Iterable['DXFEntity']) -> None:
        """
        Add `entities` to group.

        Args:
            entities: iterable of DXFEntity

        """
        self._data.extend(entities)

    def clear(self) -> None:
        """
        Remove all entity references, does not delete any drawing entities referenced by this group.

        """
        self._data = []

    def remove_invalid_handles(self) -> None:
        """
        Remove invalid handles from group.

        Invalid handles are: deleted entities, entities in a block layout

        """

        def handle_not_in_block_definition(entity) -> bool:
            # owner block_record.layout is 0 if entity is in a block definition
            owner = self.entitydb[entity.dxf.owner]
            return owner.dxf.layout != '0'

        self._data = [entity for entity in self if entity.is_alive]

        # If one entity is in a block layout remove all entities, because they have to be on the same layout
        if self._data and handle_not_in_block_definition(self._data[0]):
            self.clear()


def all_entities_on_same_layout(entities: Iterable['DXFEntity']):
    """
    Check if all entities are on the same layout (model space or any paper layout but not block).

    """
    owners = set(entity.dxf.owner for entity in entities)
    return len(owners) < 2  # 0 for no entities; 1 for all entities on the same layout


class GroupCollection(ObjectCollection):
    def __init__(self, doc: 'Drawing'):
        super().__init__(doc, dict_name='ACAD_GROUP', object_type='GROUP')
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
            name = group
        elif group.dxftype() == 'GROUP':
            name = group.get_name()
        else:
            raise DXFTypeError(group.dxftype())

        if name in self:
            super().delete(group)
        else:
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
