# Copyright (c) 2019-2020, Manfred Moitzi
# License: MIT-License
from typing import TYPE_CHECKING, Iterable, cast, Union, List, Set
from contextlib import contextmanager
import logging
from ezdxf.lldxf import validator, const
from ezdxf.lldxf.attributes import (
    DXFAttr, DXFAttributes, DefSubclass, RETURN_DEFAULT, group_code_mapping,
)
from ezdxf.audit import AuditError
from .dxfentity import base_class, SubclassProcessor, DXFEntity
from .dxfobj import DXFObject
from .factory import register_entity
from .objectcollection import ObjectCollection

logger = logging.getLogger('ezdxf')

if TYPE_CHECKING:
    from ezdxf.eztypes import (
        TagWriter, Drawing, DXFNamespace, Auditor, EntityDB,
    )

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
acdb_group_group_codes = group_code_mapping(acdb_group)
GROUP_ITEM_CODE = 340


@register_entity
class DXFGroup(DXFObject):
    """ Groups are not allowed in block definitions, and each entity can only
    reside in one group, so cloning of groups creates also new entities.

    """
    DXFTYPE = 'GROUP'
    DXFATTRIBS = DXFAttributes(base_class, acdb_group)

    def __init__(self):
        super().__init__()
        self._handles: Set[str] = set()  # only needed at the loading stage
        self._data: List[DXFEntity] = []

    def copy(self):
        raise const.DXFTypeError('Copying of GROUP not supported.')

    def load_dxf_attribs(self,
                         processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.fast_load_dxfattribs(
                dxf, acdb_group_group_codes, 1, log=False)
            self.load_group(tags)
        return dxf

    def load_group(self, tags):
        for code, value in tags:
            if code == GROUP_ITEM_CODE:
                # First store handles, because at this point, objects
                # are not stored in the EntityDB:
                self._handles.add(value)

    def preprocess_export(self, tagwriter: 'TagWriter') -> bool:
        self.purge(self.doc.entitydb)
        return True  # export even empty groups

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        super().export_entity(tagwriter)
        tagwriter.write_tag2(const.SUBCLASS_MARKER, acdb_group.name)
        self.dxf.export_dxf_attribs(tagwriter, [
            'description', 'unnamed', 'selectable'])
        self.export_group(tagwriter)

    def export_group(self, tagwriter: 'TagWriter'):
        for entity in self._data:
            tagwriter.write_tag2(GROUP_ITEM_CODE, entity.dxf.handle)

    def __iter__(self) -> Iterable[DXFEntity]:
        """ Iterate over all DXF entities in :class:`DXFGroup` as instances of
        :class:`DXFGraphic` or inherited (LINE, CIRCLE, ...).

        """
        return (e for e in self._data if e.is_alive)

    def __len__(self) -> int:
        """ Returns the count of DXF entities in :class:`DXFGroup`. """
        return len(self._data)

    def __getitem__(self, item):
        """ Returns entities by standard Python indexing and slicing. """
        return self._data[item]

    def __contains__(self, item: Union[str, DXFEntity]) -> bool:
        """ Returns ``True`` if item is in :class:`DXFGroup`. `item` has to be
        a handle string or an object of type :class:`DXFEntity` or inherited.

        """
        handle = item if isinstance(item, str) else item.dxf.handle
        return handle in set(self.handles())

    def handles(self) -> Iterable[str]:
        """ Iterable of handles of all DXF entities in :class:`DXFGroup`. """
        return (entity.dxf.handle for entity in self)

    def post_load_hook(self, doc: 'Drawing') -> None:
        super().post_load_hook(doc)
        db_get = doc.entitydb.get

        def entities():
            for handle in self._handles:
                entity = db_get(handle)
                if entity and entity.is_alive:
                    yield entity

        try:
            self.set_data(entities())
        except const.DXFStructureError as e:
            logger.error(str(e))
        del self._handles  # all referenced entities are stored in _data

    @contextmanager
    def edit_data(self) -> List[DXFEntity]:
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

    def set_data(self, entities: Iterable[DXFEntity]) -> None:
        """  Set `entities` as new group content, entities should be an iterable
        :class:`DXFGraphic` or inherited (LINE, CIRCLE, ...).
        Raises :class:`DXFValueError` if not all entities be on the same layout
        (modelspace or any paperspace layout but not block)

        """
        entities = list(entities)
        if not all_entities_on_same_layout(entities):
            raise const.DXFStructureError(
                "All entities have to be in the same layout and are not allowed"
                " to be in a block layout."
            )
        self.clear()
        self._data = entities

    def extend(self, entities: Iterable[DXFEntity]) -> None:
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
        self.purge(auditor.entitydb)
        if not all_entities_on_same_layout(self._data):
            auditor.fixed_error(
                code=AuditError.GROUP_ENTITIES_IN_DIFFERENT_LAYOUTS,
                message=f'Cleared {str(self)}, not all entities are located in '
                        f'the same layout.',
            )
            self.clear()

    def _has_valid_owner(self, entity, db: 'EntityDB') -> bool:
        # no owner -> no layout association
        if entity.dxf.owner is None:
            return False
        owner = db.get(entity.dxf.owner)
        # owner does not exist or is destroyed -> no layout association
        if owner is None or not owner.is_alive:
            return False
        # owner block_record.layout is 0 if entity is in a block definition,
        # which is not allowed:
        valid = owner.dxf.layout != '0'
        if not valid:
            logger.debug(
                f"{str(entity)} in {str(self)} is located in a block layout, "
                f"which is not allowed")
        return valid

    def _filter_invalid_entities(self, db: 'EntityDB') -> List[DXFEntity]:
        assert db is not None
        return [e for e in self._data
                if e.is_alive and self._has_valid_owner(e, db)]

    def purge(self, db: 'EntityDB') -> None:
        """ Remove invalid group entities. """
        self._data = self._filter_invalid_entities(db)


def all_entities_on_same_layout(entities: Iterable[DXFEntity]):
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
            raise const.DXFValueError(f"GROUP '{name}' already exists.")

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
            name = get_group_name(group, self.entitydb)
        else:
            raise TypeError(group.dxftype())

        if name in self:
            super().delete(name)
        else:
            raise const.DXFValueError("GROUP not in group table registered.")

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


def get_group_name(group: DXFGroup, db: 'EntityDB') -> str:
    """ Get name of `group`. """
    group_table = cast('Dictionary', db[group.dxf.owner])
    for name, entity in group_table.items():
        if entity is group:
            return name
