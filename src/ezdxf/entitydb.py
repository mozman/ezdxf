# Purpose: new entity database, replaces module ezdxf.database
# Created: 2019-02-14
# Copyright (c) 2019-2020, Manfred Moitzi
# License: MIT License
from typing import Optional, Iterable, Tuple, TYPE_CHECKING, Dict, Set
from ezdxf.tools.handle import HandleGenerator
from ezdxf.lldxf.types import is_valid_handle
from ezdxf.entities.dxfentity import DXFEntity
from ezdxf.order import priority, zorder
from ezdxf.audit import AuditError, Auditor
from ezdxf.lldxf.const import DXFInternalEzdxfError

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter

DATABASE_EXCLUDE = {'SECTION', 'ENDSEC', 'EOF', 'TABLE', 'ENDTAB', 'CLASS', 'ACDSRECORD', 'ACDSSCHEMA'}


class EntityDB:
    """ A simple key/entity database.

    Every entity/object, except tables and sections, are represented as DXFEntity or inherited types, this entities are
    stored in the drawing-associated database, database-key is the `handle` as string (group code == 5 or 105).

    """

    def __init__(self):
        self._database: Dict[str, DXFEntity] = {}
        self._trashcan: Set[str] = set()  # dxf entities to delete as set of handles
        self.handles = HandleGenerator()
        self.locked = False  # for debugging

    def __getitem__(self, handle: str) -> DXFEntity:
        """ Get entity by `handle`. """
        return self._database[handle]

    def __setitem__(self, handle: str, entity: DXFEntity) -> None:
        """ Set `entity` for `handle`. """
        assert isinstance(handle, str), type(handle)
        assert isinstance(entity, DXFEntity), type(entity)
        if self.locked:
            raise DXFInternalEzdxfError('Locked entity database.')

        if handle == '0' or not is_valid_handle(handle):
            raise ValueError(f'Invalid handle {handle}.')
        self._database[handle] = entity

    def __delitem__(self, handle: str) -> None:
        """ Delete entity by `handle`. Removes entity only from database, does not destroy the entity. """
        if self.locked:
            raise DXFInternalEzdxfError('Locked entity database.')
        del self._database[handle]

    def __contains__(self, handle: str) -> bool:
        """ ``True`` if database contains `handle`. """
        assert isinstance(handle, str), type(handle)
        return handle in self._database

    def __len__(self) -> int:
        """ Count of database items. """
        return len(self._database)

    def __iter__(self) -> Iterable[str]:
        """ Iterable of all handles. """
        return iter(self._database.keys())

    def get(self, handle: str) -> Optional[DXFEntity]:
        """ Returns entity for `handle` or ``None`` if no entry for `handle` exist. """
        return self._database.get(handle)

    def next_handle(self) -> str:
        """ Returns next unique handle."""
        while True:
            handle = self.handles.next()
            if handle not in self._database:  # you can not trust $HANDSEED value
                return handle

    def keys(self) -> Iterable[str]:
        """ Iterable of all handles. """
        return self._database.keys()

    def values(self) -> Iterable[DXFEntity]:
        """ Iterable of all entities. """
        return self._database.values()

    def items(self) -> Iterable[Tuple[str, DXFEntity]]:
        """ Iterable of all (handle, entities) pairs. """
        return self._database.items()

    def add(self, entity: DXFEntity) -> None:
        """ Add `entity` to database, assigns a new handle to the `entity` if :attr:`entity.dxf.handle` is ``None``. """
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

        # add sub entities like ATTRIB, VERTEX and SEQEND to database
        # only INSERT and POLYLINE using this feature
        if hasattr(entity, 'add_sub_entities_to_entitydb'):
            entity.add_sub_entities_to_entitydb()

    def delete_entity(self, entity: DXFEntity) -> None:
        """ Removes `entity` from database and destroys the `entity`. """
        if entity.is_alive:
            del self[entity.dxf.handle]
            entity.destroy()

    def duplicate_entity(self, entity: DXFEntity) -> DXFEntity:
        """
        Duplicates `entity` and its sub entities (VERTEX, ATTRIB, SEQEND) and store them with new handles in the
        drawing database. This is the recommend method to duplicate DXF entities in a drawing. Graphical entities
        have to be added to a layout by :meth:`~ezdxf.layouts.BaseLayout.add_entity`, for other DXF entities:
        DON'T DUPLICATE THEM.

        To import DXF entities into another drawing use the :class:`~ezdxf.addons.importer.Importer` add-on.

        An existing owner tag is not changed because this is not the domain of the :class:`EntityDB` class, will be set
        by adding the duplicated entity to a layout.

        This is not a deep copy in the meaning of Python, because handles and links are changed.

        """
        new_entity = entity.copy()  # type: DXFEntity
        new_entity.dxf.handle = self.next_handle()
        self.add(new_entity)
        return new_entity

    def audit(self, auditor: 'Auditor'):
        """ Restore database integrity:

        - removes deleted database entries (purge)
        - restore database entries with modified handles (key != entity.dxf.handle)
        - remove entities with invalid handles

        """
        assert self.locked is False, 'Database is locked!'
        db = self._database
        add_entities = []
        for handle, entity in db.items():
            if not is_valid_handle(handle):
                auditor.fixed_error(
                    code=AuditError.INVALID_ENTITY_HANDLE,
                    message=f'Removed entity {entity.dxftype()} with invalid handle "{handle}" from entity database.',
                )
                self.trash(handle)
            if not entity.is_alive:
                self.trash(handle)
            elif handle != entity.dxf.get('handle'):
                # database handle != stored entity handle
                # prevent entity from being destroyed:
                self._database[handle] = None
                self.trash(handle)
                add_entities.append(entity)

        self.empty_trashcan()

        for entity in add_entities:
            handle = entity.dxf.get('handle')
            if handle is None:
                auditor.fixed_error(
                    code=AuditError.INVALID_ENTITY_HANDLE,
                    message=f'Removed entity {entity.dxftype()} without handle from entity database.',
                )
                continue
            if not is_valid_handle(handle) or handle == '0':
                auditor.fixed_error(
                    code=AuditError.INVALID_ENTITY_HANDLE,
                    message=f'Removed entity {entity.dxftype()} with invalid handle "{handle}" from entity database.',
                )
                continue
            self[handle] = entity

    def trash(self, handle: str) -> None:
        """ Put handle into trashcan to delete entity later, required while iterating th database. """
        self._trashcan.add(handle)

    def empty_trashcan(self) -> None:
        """ Remove handles in trashcan from database and destroy entities if still alive. """
        for handle in self._trashcan:
            entity = self.get(handle)
            if entity and entity.is_alive:
                self.delete_entity(entity)

            if handle in self:
                del self[handle]

        self._trashcan.clear()


class EntitySpace:
    """
    An :class:`EntitySpace` is a collection of :class:`~ezdxf.entities.dxfentity.DXFEntity` objects, that stores only
    references to :class:`~ezdxf.entities.dxfentity.DXFEntity` objects.

    The :class:`~ezdxf.layouts.Modelspace`, any :class:`~ezdxf.layouts.Paperspace` layout and
    :class:`~ezdxf.layouts.BlockLayout` objects have an :class:`EntitySpace` container to store their entities.

    """

    def __init__(self, entities=None):
        entities = entities or []
        self.entities = list(e for e in entities if e.is_alive)

    def __iter__(self) -> Iterable['DXFEntity']:
        """ Iterable of all entities. """
        return (e for e in self.entities if e.is_alive)

    def __getitem__(self, index) -> 'DXFEntity':
        """ Get entity at index `item`

        :class:`EntitySpace` has a standard Python list like interface, therefore `index`
        can be any valid list indexing or slicing term, like a single index ``layout[-1]`` to get the last entity, or
        an index slice ``layout[:10]`` to get the first 10 or less entities as ``List[DXFEntity]``.

        """
        return self.entities[index]

    def __len__(self) -> int:
        """ Count of entities. """
        return len(self.entities)

    def has_handle(self, handle: str) -> bool:
        """ ``True`` if `handle` is present. """
        assert isinstance(handle, str), type(handle)
        return any(e.dxf.handle == handle for e in self)

    def purge(self):
        """ Remove deleted entities. """
        self.entities = list(self)

    def reorder(self, order: int = 1) -> None:
        """ Reorder entities in place.

        Args:
             order: ``1`` = priority order (highest first), ``2`` = z-order (inverted priority, lowest first)

        """
        if order == 1:
            reverse = True
        elif order == 2:
            reverse = False
        else:
            return  # do nothing

        self.entities.sort(key=lambda e: e.priority, reverse=reverse)

    def add(self, entity: 'DXFEntity') -> None:
        """ Add `entity`. """
        assert isinstance(entity, DXFEntity), type(entity)
        self.entities.append(entity)

    def extend(self, entities: Iterable['DXFEntity']) -> None:
        """ Add multiple `entities`."""
        for entity in entities:
            self.add(entity)

    def export_dxf(self, tagwriter: 'TagWriter', order=0) -> None:
        """
        Export all entities into DXF file by `tagwriter` in given `order`.

        Args:
            tagwriter: TagWriter()
            order: 0 = order of appearance, 1 = priority order (highest first), 2 = z-order (inverted priority,
                   lowest first)

        (internal API)
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
                    # INSERT: entity.seqend can be present, without attached ATTRIBS, if ATTRIBS were deleted
                    seqend = True
                    linked.export_dxf(tagwriter)

            if seqend:
                entity.export_seqend(tagwriter)

    def remove(self, entity: 'DXFEntity') -> None:
        """ Remove `entity`. """
        self.entities.remove(entity)

    def clear(self) -> None:
        """ Remove all entities. """
        # do not delete database objects - entity space just manage handles
        self.entities = list()
