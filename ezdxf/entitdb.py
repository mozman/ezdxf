# Purpose: new entity database, replaces module ezdxf.database
# Created: 2019-02-14
# Copyright (c) 2019, Manfred Moitzi
# License: MIT License
from typing import Optional, Iterable, Tuple, Union
from ezdxf.clone import clone
from ezdxf.tools.handle import HandleGenerator
from ezdxf.entities.dxfentity import DXFEntity


class RealEntityDB:
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

    def add(self, entity: DXFEntity) -> str:
        handle = entity.dxf.handle  # type: str
        if handle is None:
            handle = self.next_handle()
            entity.dxf.handle = handle
        self[handle] = entity
        return handle

    def delete_entity(self, entity: DXFEntity) -> None:
        entity.destroy()
        del self[entity.dxf.handle]

    def duplicate_entity(self, entity: DXFEntity) -> DXFEntity:
        """
        Deep copy of tags with new handle and duplicated linked entities (VERTEX, ATTRIB, SEQEND) with also new handles.
        An existing owner tag is not changed because this is not the domain of the EntityDB() class.
        The new entity tags are added to the drawing database.

        This is not a deep copy in the meaning of Python, because handle and link is changed.

        """
        new_entity = clone(entity)  # type: DXFEntity
        new_entity.dxf.handle = self.next_handle()
        self.add(new_entity)
        return new_entity
