# Copyright (c) 2019-2021, Manfred Moitzi
# License: MIT License
from typing import (
    Optional,
    Iterable,
    Tuple,
    TYPE_CHECKING,
    Dict,
    Set,
    List,
    Iterator,
)
from contextlib import contextmanager
from ezdxf.tools.handle import HandleGenerator
from ezdxf.lldxf.types import is_valid_handle
from ezdxf.entities.dxfentity import DXFEntity
from ezdxf.entities.dxfobj import DXFObject
from ezdxf.audit import AuditError, Auditor
from ezdxf.lldxf.const import DXFInternalEzdxfError
from ezdxf.entities import factory

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter

DATABASE_EXCLUDE = {
    "SECTION",
    "ENDSEC",
    "EOF",
    "TABLE",
    "ENDTAB",
    "CLASS",
    "ACDSRECORD",
    "ACDSSCHEMA",
}


class EntityDB:
    """A simple key/entity database.

    Every entity/object, except tables and sections, are represented as
    DXFEntity or inherited types, this entities are stored in the
    DXF document database, database-key is the `handle` as string.

    """

    class Trashcan:
        """Store handles to entities which should be deleted later."""

        def __init__(self, db: "EntityDB"):
            self._database = db._database
            self._handles: Set[str] = set()

        def add(self, handle: str):
            """Put handle into trashcan to delete the entity later, this is
            required for deleting entities while iterating the database.
            """
            self._handles.add(handle)

        def clear(self):
            """Remove handles in trashcan from database and destroy entities if
            still alive.
            """
            db = self._database
            for handle in self._handles:
                entity = db.get(handle)
                if entity and entity.is_alive:
                    entity.destroy()

                if handle in db:
                    del db[handle]

            self._handles.clear()

    def __init__(self):
        self._database: Dict[str, DXFEntity] = {}
        # DXF handles of entities to delete later:
        self.handles = HandleGenerator()
        self.locked: bool = False  # used only for debugging

    def __getitem__(self, handle: str) -> DXFEntity:
        """Get entity by `handle`, does not filter destroyed entities nor
        entities in the trashcan.
        """
        return self._database[handle]

    def __setitem__(self, handle: str, entity: DXFEntity) -> None:
        """Set `entity` for `handle`."""
        assert isinstance(handle, str), type(handle)
        assert isinstance(entity, DXFEntity), type(entity)
        assert entity.is_alive, "Can not store destroyed entity."
        if self.locked:
            raise DXFInternalEzdxfError("Locked entity database.")

        if handle == "0" or not is_valid_handle(handle):
            raise ValueError(f"Invalid handle {handle}.")
        self._database[handle] = entity

    def __delitem__(self, handle: str) -> None:
        """Delete entity by `handle`. Removes entity only from database, does
        not destroy the entity.
        """
        if self.locked:
            raise DXFInternalEzdxfError("Locked entity database.")
        del self._database[handle]

    def __contains__(self, handle: str) -> bool:
        """``True`` if database contains `handle`."""
        if handle is None:
            return False
        assert isinstance(handle, str), type(handle)
        return handle in self._database

    def __len__(self) -> int:
        """Count of database items."""
        return len(self._database)

    def __iter__(self) -> Iterator[str]:
        """Iterable of all handles, does filter destroyed entities but not
        entities in the trashcan.
        """
        return self.keys()  # type: ignore

    def get(self, handle: str) -> Optional[DXFEntity]:
        """Returns entity for `handle` or ``None`` if no entry exist, does
        not filter destroyed entities.
        """
        return self._database.get(handle)

    def next_handle(self) -> str:
        """Returns next unique handle."""
        while True:
            handle = self.handles.next()
            if handle not in self._database:
                return handle

    def keys(self) -> Iterable[str]:
        """Iterable of all handles, does filter destroyed entities."""
        return (handle for handle, entity in self.items())

    def values(self) -> Iterable[DXFEntity]:
        """Iterable of all entities, does filter destroyed entities."""
        return (entity for handle, entity in self.items())

    def items(self) -> Iterable[Tuple[str, DXFEntity]]:
        """Iterable of all (handle, entities) pairs, does filter destroyed
        entities.
        """
        return (
            (handle, entity)
            for handle, entity in self._database.items()
            if entity.is_alive
        )

    def add(self, entity: DXFEntity) -> None:
        """Add `entity` to database, assigns a new handle to the `entity`
        if :attr:`entity.dxf.handle` is ``None``. Adding the same entity
        multiple times is possible and creates only a single database entry.

        """
        if entity.dxftype() in DATABASE_EXCLUDE:
            if entity.dxf.handle is not None:
                # Mark existing entity handle as used to avoid
                # reassigning the same handle again.
                self[entity.dxf.handle] = entity
            return
        handle: str = entity.dxf.handle
        if handle is None:
            handle = self.next_handle()
            entity.update_handle(handle)
        self[handle] = entity

        # Add sub entities ATTRIB, VERTEX and SEQEND to database:
        # Add linked MTEXT columns to database:
        if hasattr(entity, "add_sub_entities_to_entitydb"):
            entity.add_sub_entities_to_entitydb(self)  # type: ignore

    def delete_entity(self, entity: DXFEntity) -> None:
        """Remove `entity` from database and destroy the `entity`."""
        if entity.is_alive:
            del self[entity.dxf.handle]
            entity.destroy()

    def discard(self, entity: DXFEntity) -> None:
        """Discard `entity` from database without destroying the `entity`."""
        if entity.is_alive:
            if hasattr(entity, "process_sub_entities"):
                entity.process_sub_entities(lambda e: self.discard(e))  # type: ignore

            handle = entity.dxf.handle
            try:
                del self._database[handle]
                entity.dxf.handle = None
            except KeyError:
                pass

    def duplicate_entity(self, entity: DXFEntity) -> DXFEntity:
        """Duplicates `entity` and its sub entities (VERTEX, ATTRIB, SEQEND)
        and store them with new handles in the entity database.
        Graphical entities have to be added to a layout by
        :meth:`~ezdxf.layouts.BaseLayout.add_entity`. DXF objects will
        automatically added to the OBJECTS section.

        To import DXF entities from another drawing use the
        :class:`~ezdxf.addons.importer.Importer` add-on.

        A new owner handle will be set by adding the duplicated entity to a
        layout.

        """
        doc = entity.doc
        assert doc is not None, "valid DXF document required"
        new_handle = self.next_handle()
        new_entity: DXFEntity = entity.copy()
        new_entity.dxf.handle = new_handle
        factory.bind(new_entity, doc)
        if isinstance(new_entity, DXFObject):
            # add DXF objects automatically to the OBJECTS section
            doc.objects.add_object(new_entity)
        return new_entity

    def audit(self, auditor: "Auditor"):
        """Restore database integrity:

        - restore database entries with modified handles (key != entity.dxf.handle)
        - remove entities with invalid handles
        - empty trashcan - destroy all entities in the trashcan
        - removes destroyed database entries (purge)

        """
        assert self.locked is False, "Database is locked!"
        add_entities = []

        with self.trashcan() as trash:  # type: ignore
            for handle, entity in self.items():
                # Destroyed entities are already filtered!
                if not is_valid_handle(handle):
                    auditor.fixed_error(
                        code=AuditError.INVALID_ENTITY_HANDLE,
                        message=f"Removed entity {entity.dxftype()} with invalid "
                        f'handle "{handle}" from entity database.',
                    )
                    trash.add(handle)
                if handle != entity.dxf.get("handle"):
                    # database handle != stored entity handle
                    # prevent entity from being destroyed:
                    self._database[handle] = None  # type: ignore
                    trash.add(handle)
                    add_entities.append(entity)

        # Remove all destroyed entities from database:
        self.purge()

        for entity in add_entities:
            handle = entity.dxf.get("handle")
            if handle is None:
                auditor.fixed_error(
                    code=AuditError.INVALID_ENTITY_HANDLE,
                    message=f"Removed entity {entity.dxftype()} without handle "
                    f"from entity database.",
                )
                continue
            if not is_valid_handle(handle) or handle == "0":
                auditor.fixed_error(
                    code=AuditError.INVALID_ENTITY_HANDLE,
                    message=f"Removed entity {entity.dxftype()} with invalid "
                    f'handle "{handle}" from entity database.',
                )
                continue
            self[handle] = entity

    def new_trashcan(self) -> "EntityDB.Trashcan":
        """Returns a new trashcan, empty trashcan manually by: :
        func:`Trashcan.clear()`.
        """
        return EntityDB.Trashcan(self)

    @contextmanager  # type: ignore
    def trashcan(self) -> "EntityDB.Trashcan":  # type: ignore
        """Returns a new trashcan in context manager mode, trashcan will be
        emptied when leaving context.
        """
        trashcan_ = self.new_trashcan()
        yield trashcan_
        # try ... finally is not required, in case of an exception the database
        # is maybe already in an unreliable state.
        trashcan_.clear()

    def purge(self) -> None:
        """Remove all destroyed entities from database, but does not empty the
        trashcan.
        """
        # Important: operate on underlying data structure:
        db = self._database
        dead_handles = [
            handle for handle, entity in db.items() if not entity.is_alive
        ]
        for handle in dead_handles:
            del db[handle]

    def dxf_types_in_use(self) -> Set[str]:
        return set(entity.dxftype() for entity in self.values())

    def reset_handle(self, entity: DXFEntity, handle: str) -> bool:
        """Try to reset the entity handle to a certain value.
        Returns ``True`` if successful and ``False`` otherwise.

        """
        if handle in self._database:
            return False
        self.discard(entity)
        entity.dxf.handle = handle
        self.add(entity)
        return True


class EntitySpace:
    """
    An :class:`EntitySpace` is a collection of :class:`~ezdxf.entities.DXFEntity`
    objects, that stores only  references to :class:`DXFEntity` objects.

    The :class:`~ezdxf.layouts.Modelspace`, any :class:`~ezdxf.layouts.Paperspace`
    layout and :class:`~ezdxf.layouts.BlockLayout` objects have an
    :class:`EntitySpace` container to store their entities.

    """

    def __init__(self, entities: Iterable[DXFEntity] = None):
        self.entities: List[DXFEntity] = (
            list(e for e in entities if e.is_alive) if entities else []
        )

    def __iter__(self) -> Iterator[DXFEntity]:
        """Iterable of all entities, filters destroyed entities."""
        return (e for e in self.entities if e.is_alive)

    def __getitem__(self, index) -> DXFEntity:
        """Get entity at index `item`

        :class:`EntitySpace` has a standard Python list like interface,
        therefore `index` can be any valid list indexing or slicing term, like
        a single index ``layout[-1]`` to get the last entity, or an index slice
        ``layout[:10]`` to get the first 10 or less entities as
        ``List[DXFEntity]``. Does not filter destroyed entities.

        """
        return self.entities[index]

    def __len__(self) -> int:
        """Count of entities including destroyed entities."""
        return len(self.entities)

    def has_handle(self, handle: str) -> bool:
        """``True`` if `handle` is present, does filter destroyed entities."""
        assert isinstance(handle, str), type(handle)
        return any(e.dxf.handle == handle for e in self)

    def purge(self):
        """Remove all destroyed entities from entity space."""
        self.entities = list(self)

    def add(self, entity: DXFEntity) -> None:
        """Add `entity`."""
        assert isinstance(entity, DXFEntity), type(entity)
        assert entity.is_alive, "Can not store destroyed entities"
        self.entities.append(entity)

    def extend(self, entities: Iterable[DXFEntity]) -> None:
        """Add multiple `entities`."""
        for entity in entities:
            self.add(entity)

    def export_dxf(self, tagwriter: "TagWriter") -> None:
        """Export all entities into DXF file by `tagwriter`.

        (internal API)
        """
        for entity in iter(self):
            entity.export_dxf(tagwriter)

    def remove(self, entity: DXFEntity) -> None:
        """Remove `entity`."""
        self.entities.remove(entity)

    def clear(self) -> None:
        """Remove all entities."""
        # Do not destroy entities!
        self.entities = list()
