# Purpose: new entity database, replaces module ezdxf.database
# Created: 2019-02-14
# Copyright (c) 2019, Manfred Moitzi
# License: MIT License
from typing import Optional, Iterable, Tuple, Union, TYPE_CHECKING
from ezdxf.tools.handle import HandleGenerator
from ezdxf.entities.dxfentity import DXFEntity
from ezdxf.order import priority, zorder

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter

DATABASE_EXCLUDE = {'SECTION', 'ENDSEC', 'EOF', 'TABLE', 'ENDTAB', 'CLASS', 'ACDSRECORD', 'ACDSSCHEMA'}


class EntityDB:
    """ A simple key/entity database.

    The new Data Model

    Every entity/object, except tables and sections, are represented as DXFEntity or inherited types, this entities are
    stored in the drawing-associated database, database-key is the `handle` as string (group code == 5 or 105).

    """
    def __init__(self):
        self._database = {}
        self.handles = HandleGenerator()

    def __getitem__(self, handle: str) -> DXFEntity:
        return self._database[handle]

    def __setitem__(self, handle: str, entity: DXFEntity) -> None:
        self._database[handle] = entity

    def __delitem__(self, handle: str) -> None:
        del self._database[handle]

    def __contains__(self, item: Union[str, DXFEntity]) -> bool:
        """ Database contains handle? """
        if isinstance(item, str):
            handle = item
        else:
            handle = item.dxf.handle
        return handle in self._database

    def __len__(self) -> int:
        """ Count of database items. """
        return len(self._database)

    def __iter__(self) -> Iterable[str]:
        """ Iterate over all handles. """
        return iter(self._database.keys())

    def get(self, handle: str) -> Optional[DXFEntity]:
        try:
            return self.__getitem__(handle)
        except KeyError:  # internal exception
            return None

    def next_handle(self) -> str:
        """ Returns next unique handle."""
        while True:
            handle = self.handles.next()
            if handle not in self._database:  # you can not trust $HANDSEED value
                return handle

    def keys(self) -> Iterable[str]:
        """ Iterate over all handles. """
        return self._database.keys()

    def values(self) -> Iterable[DXFEntity]:
        """ Iterate over all entities. """
        return self._database.values()

    def items(self) -> Iterable[Tuple[str, DXFEntity]]:
        """ Iterate over all (handle, entities) pairs. """
        return self._database.items()

    def add(self, entity: DXFEntity) -> None:
        if entity.dxftype() in DATABASE_EXCLUDE:
            if entity.dxf.handle is not None:
                # store entities with handles (TABLE, maybe others) to avoid reassigning of its handle
                self[entity.dxf.handle] = entity
            return
        handle = entity.dxf.handle  # type: str
        if handle is None:
            handle = self.next_handle()
            # update_handle() requires the objects section to update the owner handle of the extension dictionary,
            # but this is no problem at file loading, all entities have handles, and DXF R12 (without handles) have no
            # extension dictionaries.
            entity.update_handle(handle)
        self[handle] = entity

    def delete_entity(self, entity: DXFEntity) -> None:
        del self[entity.dxf.handle]
        entity.destroy()

    def duplicate_entity(self, entity: DXFEntity) -> DXFEntity:
        """
        Deep copy of tags with new handle and duplicated linked entities (VERTEX, ATTRIB, SEQEND) with also new handles.
        An existing owner tag is not changed because this is not the domain of the EntityDB() class.
        The new entity tags are added to the drawing database.

        This is not a deep copy in the meaning of Python, because handle and link is changed.

        """
        new_entity = entity.copy()  # type: DXFEntity
        new_entity.dxf.handle = self.next_handle()
        self.add(new_entity)
        return new_entity


class EntitySpace:
    """
    An EntitySpace is a collection of drawing entities.
    The ENTITY section is such an entity space, but also blocks.
    The EntitySpace stores only handles to the drawing entity database.

    """

    def __init__(self, entities=None):
        entities = entities or []
        self.entities = list(e for e in entities if e.is_alive)

    def __iter__(self) -> Iterable['DXFEntity']:
        return (e for e in self.entities if e.is_alive)

    def __getitem__(self, item) -> 'DXFEntity':
        return self.entities[item]

    def __len__(self):
        return len(self.entities)

    def has_handle(self, handle: str):
        return any(e.dxf.handle == handle for e in self)

    def purge(self):
        """ Remove deleted entities. """
        self.entities = list(self)

    def reorder(self, order=1):
        """ Reorder entities in place.

        Args:
             order: 1 = priority order (highest first), 2 = z-order (inverted priority, lowest first)

        """
        if order == 1:
            reverse = True
        elif order == 2:
            reverse = False
        else:
            return  # do nothing

        self.entities.sort(key=lambda e: e.priority, reverse=reverse)

    def add(self, entity: 'DXFEntity'):
        """ Add `entity` to entity space. """
        self.entities.append(entity)

    def extend(self, entities: Iterable['DXFEntity']) -> None:
        self.entities.extend(entities)

    def export_dxf(self, tagwriter: 'TagWriter', order=0) -> None:
        """
        Export all entities into DXF file by `tagwriter` in given `order`.

        Args:
            tagwriter: TagWriter()
            order: 0 = order of appearance, 1 = priority order (highest first), 2 = z-order (inverted priority,
                   lowest first)

        """
        if order == 0:
            entities = iter(self)
        elif order == 1:
            entities = priority(self)
        elif order == 2:
            entities = zorder(self)
        else:
            raise ValueError('invalid order: 0, 1 or 2')

        for entity in entities:
            entity.export_dxf(tagwriter)
            seqend = False
            if hasattr(entity, 'linked_entities'):  # only POLYLINE & INSERT can have linked entities
                for linked in entity.linked_entities():
                    seqend = True
                    linked.export_dxf(tagwriter)

            if seqend:
                entity.export_seqend(tagwriter)

    def remove(self, entity: 'DXFEntity') -> None:
        """ Remove `entity` from entity space """
        self.entities.remove(entity)

    def clear(self) -> None:
        """ Remove all entities from entity space. """
        # do not delete database objects - entity space just manage handles
        self.entities = list()
