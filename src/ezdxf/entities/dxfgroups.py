# Created: 2019-02-19
# Copyright (c) 2019-2020, Manfred Moitzi
# License: MIT-License
from typing import TYPE_CHECKING, Iterable, cast, Union, List
from contextlib import contextmanager
import logging
from ezdxf.lldxf import validator
from ezdxf.lldxf.const import DXFValueError, SUBCLASS_MARKER, DXFTypeError
from ezdxf.lldxf.attributes import (
    DXFAttr, DXFAttributes, DefSubclass, RETURN_DEFAULT,
)
from ezdxf.audit import AuditError
from .dxfentity import base_class, SubclassProcessor
from .dxfobj import DXFObject
from .dxfgfx import DXFGraphic
from .factory import register_entity
from .objectcollection import ObjectCollection

logger = logging.getLogger('ezdxf')

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, Drawing, DXFNamespace, Auditor

__all__ = ['DXFGroup', 'GroupCollection']

acdb_group = DefSubclass('AcDbGroup', {
    # Group description
    'description': DXFAttr(300, default=''),

    # 1 = Unnamed
    # 0 = Named
    'unnamed': DXFAttr(
        70, default=1, validator=validator.is_integer_bool,
        fixer=RETURN_DEFAULT,
    ),

    # 1 = Selectable
    # 0 = Not selectable
    'selectable': DXFAttr(
        71, default=1,
        validator=validator.is_integer_bool,
        fixer=RETURN_DEFAULT,
    ),

    # 340: Hard-pointer handle to entity in group (one entry per object)
})

GROUP_ITEM_CODE = 340


@register_entity
class DXFGroup(DXFObject):
    """ Groups are not allowed in block definitions, and each entity can only
    reside in one group, so cloning of groups creates also new entities.

    """
    DXFTYPE = 'GROUP'
    DXFATTRIBS = DXFAttributes(base_class, acdb_group)

    def __init__(self, doc: 'Drawing' = None):
        super().__init__(doc)
        self._data = list()  # type: List[Union[str, DXFGraphic]]

    def copy(self):
        raise DXFTypeError('Copying of GROUP not supported.')

    def load_dxf_attribs(self,
                         processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor is None:
            return dxf
        tags = processor.load_dxfattribs_into_namespace(dxf, acdb_group)
        self.load_group(tags)
        return dxf

    def load_group(self, tags):
        for code, value in tags:
            if code == GROUP_ITEM_CODE:
                # First store handles, because at this point, not all objects
                # are stored in the EntityDB, at access convert the handle to
                # DXFEntity:
                try:
                    entity = self.entitydb[value]
                except KeyError:
                    # Store entity as handle string
                    entity = value
                self._data.append(entity)

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        super().export_entity(tagwriter)
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_group.name)
        self.dxf.export_dxf_attribs(tagwriter, [
            'description', 'unnamed', 'selectable'])
        self.export_group(tagwriter)

    def export_group(self, tagwriter: 'TagWriter'):
        for entity in self._data:
            if isinstance(entity, str):
                handle = entity
            else:
                handle = entity.dxf.handle
            tagwriter.write_tag2(GROUP_ITEM_CODE, handle)

    def __iter__(self) -> Iterable['DXFGraphic']:
        """ Iterate over all DXF entities in :class:`DXFGroup` as instances of
        :class:`DXFGraphic` or inherited (LINE, CIRCLE, ...).

        """
        for index, entity in enumerate(self._data):
            if isinstance(entity, str):
                # replace handle string by DXFEntity
                entity = self.entitydb[entity]
                self._data[index] = entity
            yield entity

    def __len__(self) -> int:
        """ Returns the count of DXF entities in :class:`DXFGroup`. """
        return len(self._data)

    def __getitem__(self, item):
        """ Returns entities by standard Python indexing and slicing. """
        return self._data[item]

    def __contains__(self, item: Union[str, 'DXFGraphic']) -> bool:
        """ Returns ``True`` if item is in :class:`DXFGroup`. `item` has to be
        a handle string or an object of type :class:`DXFGraphic` or inherited.

        """
        handle = item if isinstance(item, str) else item.dxf.handle
        return handle in set(self.handles())

    def handles(self) -> Iterable[str]:
        """ Iterable of handles of all DXF entities in :class:`DXFGroup`. """
        return (entity.dxf.handle for entity in self)

    def get_name(self) -> str:
        """ Get name of :class:`DXFGroup`. """
        group_table = cast('Dictionary', self.entitydb[self.dxf.owner])
        for name, entity in group_table.items():
            if entity is self:
                return name

    @contextmanager
    def edit_data(self) -> List['DXFGraphic']:
        """ Context manager which yields all the group entities as
        standard Python list::

            with group.edit_data() as data:
               # add new entities to a group
               data.append(modelspace.add_line((0, 0), (3, 0)))
               # remove last entity from a group
               data.pop()

        """
        data = list(self)
        yield data
        self.set_data(data)

    def set_data(self, entities: Iterable['DXFGraphic']) -> None:
        """  Set `entities` as new group content, entities should be an iterable
        :class:`DXFGraphic` or inherited (LINE, CIRCLE, ...).
        Raises :class:`DXFValueError` if not all entities be on the same layout
        (modelspace or any paperspace layout but not block)

        """
        entities = list(entities)
        if not all_entities_on_same_layout(entities):
            raise DXFValueError(
                "All entities have to be on the same layout (modelspace or any "
                "paperspace layout but not a block)."
            )
        self.clear()
        self._data = entities

    def extend(self, entities: Iterable['DXFGraphic']) -> None:
        """ Add `entities` to :class:`DXFGroup`. """
        self._data.extend(entities)

    def clear(self) -> None:
        """ Remove all entities from :class:`DXFGroup`, does not delete any
        drawing entities referenced by this group.

        """
        self._data = []

    def audit(self, auditor: 'Auditor') -> None:
        """ Remove invalid handles from :class:`DXFGroup`.

        Invalid handles are: deleted entities, not all entities in the same
        layout or entities in a block layout.

        """
        # Remove destroyed or invalid entities:
        self._data = list(self.filter_invalid_entities())
        if len(self._data) == 0:
            return

        if not all_entities_on_same_layout(self._data):
            auditor.fixed_error(
                code=AuditError.GROUP_ENTITIES_IN_DIFFERENT_LAYOUTS,
                message=f'Cleared {str(self)}, not all entities are located in '
                        f'the same layout.',
            )
            self.clear()

    def has_valid_owner(self, entity) -> bool:
        # no owner -> no layout association
        if entity.dxf.owner is None:
            return False
        owner = self.entitydb.get(entity.dxf.owner)
        # owner does not exist or is destroyed -> no layout association
        if owner is None or not owner.is_alive:
            return False
        # owner block_record.layout is 0 if entity is in a block definition,
        # which is not allowed:
        valid = owner.dxf.layout != '0'
        if not valid:
            logger.debug(
                f'Removed {str(entity)} from {str(self)}, because entity is '
                f'located in a block layout.')
        return valid

    def filter_invalid_entities(self) -> Iterable['DXFGraphic']:
        db = self.entitydb
        for e in self._data:
            if e is None:
                continue
            if isinstance(e, str):
                e = db.get(e)  # returns None for not existing entities
            if isinstance(e, DXFGraphic) and \
                    e.is_alive and \
                    self.has_valid_owner(e):
                yield e


def all_entities_on_same_layout(entities: Iterable['DXFGraphic']):
    """ Check if all entities are on the same layout (model space or any paper
    layout but not block).

    """
    owners = set(entity.dxf.owner for entity in entities)
    # 0 for no entities; 1 for all entities on the same layout
    return len(owners) < 2


class GroupCollection(ObjectCollection):
    def __init__(self, doc: 'Drawing'):
        super().__init__(doc, dict_name='ACAD_GROUP', object_type='GROUP')
        self._next_unnamed_number = 0

    def groups(self) -> Iterable[DXFGroup]:
        """ Iterable of all existing groups. """
        for name, group in self:
            yield group

    def next_name(self) -> str:
        name = self._next_name()
        while name in self:
            name = self._next_name()
        return name

    def _next_name(self) -> str:
        self._next_unnamed_number += 1
        return f"*A{self._next_unnamed_number}"

    def new(self, name: str = None, description: str = "",
            selectable: bool = True) -> DXFGroup:
        r""" Creates a new group. If `name` is ``None`` an unnamed group is
        created, which has an automatically generated name like "\*Annnn".

        Args:
            name: group name as string
            description: group description as string
            selectable: group is selectable if ``True``

        """
        if name in self:
            raise DXFValueError(f"GROUP '{name}' already exists.")

        if name is None:
            name = self.next_name()
            unnamed = 1
        else:
            unnamed = 0
        # The group name isn't stored in the group entity itself.
        dxfattribs = {
            'description': description,
            'unnamed': unnamed,
            'selectable': int(bool(selectable)),
        }
        return cast(DXFGroup, self._new(name, dxfattribs))

    def delete(self, group: Union[DXFGroup, str]) -> None:
        """ Delete `group`, `group` can be an object of type :class:`DXFGroup`
        or a group name as string.

        """
        # Delete group by name:
        if isinstance(group, str):
            name = group
        elif group.dxftype() == 'GROUP':
            name = group.get_name()
        else:
            raise DXFTypeError(group.dxftype())

        if name in self:
            super().delete(name)
        else:
            raise DXFValueError("GROUP not in group table registered.")

    def audit(self, auditor: 'Auditor') -> None:
        """ Removes empty groups and invalid handles from all groups. """
        trash = []
        for name, group in self:
            group.audit(auditor)
            if not len(group):  # remove empty group
                # do not delete groups while iterating over groups!
                trash.append(name)

        # now delete empty groups
        for name in trash:
            auditor.fixed_error(
                code=AuditError.REMOVE_EMPTY_GROUP,
                message=f'Removed empty group "{name}".',
            )
            self.delete(name)
