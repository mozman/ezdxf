# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, Callable, List, Optional

from ezdxf.entities import factory, DXFGraphic, SeqEnd, DXFEntity
from ezdxf.lldxf import const

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFEntity, EntityDB, Drawing

__all__ = ['entity_linker', 'LinkedEntities']


class LinkedEntities(DXFGraphic):
    """ Super class for common features of the INSERT and the POLYLINE entity.
    Both have linked entities like the VERTEX or ATTRIB entity and a
    SEQEND entity.

    """

    def __init__(self):
        super().__init__()
        self._sub_entities: List[DXFGraphic] = []
        self.seqend: Optional['SeqEnd'] = None

    def _copy_data(self, entity: 'LinkedEntities') -> None:
        """ Copy all sub-entities ands SEQEND. (internal API) """
        entity._sub_entities = [e.copy() for e in self._sub_entities]
        if self.seqend:
            entity.seqend = self.seqend.copy()

    def link_entity(self, entity: 'DXFGraphic') -> None:
        """ Link VERTEX ot ATTRIB entities. """
        entity.set_owner(self.dxf.owner, self.dxf.paperspace)
        self._sub_entities.append(entity)

    def link_seqend(self, seqend: 'DXFEntity') -> None:
        """ Link SEQEND entity. (internal API) """
        seqend.dxf.owner = self.dxf.owner
        self.seqend = seqend

    def post_bind_hook(self):
        """ Create always a SEQEND entity. """
        if self.seqend is None:
            self.new_seqend()

    def all_sub_entities(self) -> Iterable['DXFEntity']:
        """ Yields all sub-entities ans SEQEND. (internal API) """
        yield from self._sub_entities
        if self.seqend:
            yield self.seqend

    def process_sub_entities(self, func: Callable[['DXFEntity'], None]):
        """ Call `func` for all sub-entities and SEQEND. (internal API)
        """
        for entity in self.all_sub_entities():
            if entity.is_alive:
                func(entity)

    def add_sub_entities_to_entitydb(self, db: 'EntityDB') -> None:
        """ Add sub-entities (VERTEX, ATTRIB, SEQEND) to entity database `db`,
        called from EntityDB. (internal API)
        """

        def add(entity: 'DXFEntity'):
            entity.doc = self.doc  # grant same document
            db.add(entity)

        if not self.seqend or not self.seqend.is_alive:
            self.new_seqend()
        self.process_sub_entities(add)

    def new_seqend(self):
        """ Create and bind new SEQEND. (internal API) """
        attribs = {'layer': self.dxf.layer}
        if self.doc:
            seqend = factory.create_db_entry('SEQEND', attribs, self.doc)
        else:
            seqend = factory.new('SEQEND', attribs)
        self.link_seqend(seqend)

    def set_owner(self, owner: str, paperspace: int = 0):
        """ Set owner of all sub-entities and SEQEND. (internal API) """
        # Loading from file: POLYLINE/INSERT will be added to layout before
        # vertices/attrib entities are linked, so set_owner() of POLYLINE does
        # not set owner of vertices at loading time.
        super().set_owner(owner, paperspace)

        def set_owner(entity):
            if isinstance(entity, DXFGraphic):
                entity.set_owner(owner, paperspace)
            else:  # SEQEND
                entity.dxf.owner = owner

        self.process_sub_entities(set_owner)

    def remove_dependencies(self, other: 'Drawing' = None):
        """ Remove all dependencies from current document to bind entity to
        `other` document. (internal API)
        """
        self.process_sub_entities(lambda e: e.remove_dependencies(other))
        super().remove_dependencies(other)

    def destroy(self) -> None:
        """ Destroy all data and references. """
        if not self.is_alive:
            return

        self.process_sub_entities(func=lambda e: e.destroy())
        del self._sub_entities
        del self.seqend
        super().destroy()


# This attached MTEXT is a limited MTEXT entity, starting with (0, 'MTEXT')
# therefore separated entity, but without the base class: no handle, no owner
# nor AppData, and a limited AcDbEntity subclass.
# Detect attached entities (more than MTEXT?) by required but missing handle and
# owner tags use DXFEntity.link_entity() for linking to preceding entity,
# INSERT & POLYLINE do not have attached entities, so reuse of API for
# ATTRIB & ATTDEF should be safe.

LINKED_ENTITIES = {
    'INSERT': 'ATTRIB',
    'POLYLINE': 'VERTEX'
}


def entity_linker() -> Callable[[DXFEntity], bool]:
    """ Create an DXF entities linker. """
    main_entity: Optional[DXFEntity] = None
    prev: Optional[DXFEntity] = None
    expected_dxftype = ""

    def entity_linker_(entity: DXFEntity) -> bool:
        """ Collect and link entities which are linked to a parent entity:

        - VERTEX -> POLYLINE
        - ATTRIB -> INSERT
        - attached MTEXT entity

        Args:
             entity: examined DXF entity

        Returns:
             True if `entity` is linked to a parent entity

        """
        nonlocal main_entity, expected_dxftype, prev
        dxftype: str = entity.dxftype()
        # INSERT & POLYLINE are not linked entities, they are stored in the
        # entity space.
        are_linked_entities = False
        if main_entity is not None:
            # VERTEX, ATTRIB & SEQEND are linked tags, they are NOT stored in
            # the entity space.
            are_linked_entities = True
            if dxftype == 'SEQEND':
                main_entity.link_seqend(entity)
                # Marks also the end of the main entity
                main_entity = None
            # Check for valid DXF structure:
            #   VERTEX follows POLYLINE
            #   ATTRIB follows INSERT
            elif dxftype == expected_dxftype:
                main_entity.link_entity(entity)
            else:
                raise const.DXFStructureError(
                    f"Expected DXF entity {dxftype} or SEQEND"
                )

        elif dxftype in LINKED_ENTITIES:
            # Only INSERT and POLYLINE have a linked entities structure:
            if dxftype == 'INSERT' and not entity.dxf.get('attribs_follow', 0):
                # INSERT must not have following ATTRIBS, ATTRIB can be a stand
                # alone entity:
                #
                #   INSERT with no ATTRIBS, attribs_follow == 0
                #   ATTRIB as stand alone entity
                #   ....
                #   INSERT with ATTRIBS, attribs_follow == 1
                #   ATTRIB as connected entity
                #   SEQEND
                #
                # Therefore a ATTRIB following an INSERT doesn't mean that
                # these entities are linked.
                pass
            else:
                main_entity = entity
                expected_dxftype = LINKED_ENTITIES[dxftype]

        # Attached MTEXT entity:
        elif (dxftype == 'MTEXT') and (entity.dxf.handle is None):
            if prev:
                prev.link_entity(entity)
                are_linked_entities = True
            else:
                raise const.DXFStructureError(
                    "Found attached MTEXT entity without a preceding entity."
                )
        prev = entity
        return are_linked_entities

    return entity_linker_
