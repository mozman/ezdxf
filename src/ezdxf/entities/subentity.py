# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, Callable, List, Optional
from ezdxf.entities import factory, DXFGraphic, SeqEnd

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFEntity, TagWriter, EntityDB, Drawing


class LinkedEntities(DXFGraphic):
    """ Super class for common features of the INSERT and the POLYLINE entity.
    Both have linked entities like the VERTEX or ATTRIB entity and a
    SEQEND entity.

    """

    def __init__(self, doc: 'Drawing' = None):
        super().__init__(doc)
        self._sub_entities: List[DXFGraphic] = []
        self.seqend: Optional['SeqEnd'] = None
        self._has_new_sub_entities = True

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
        if not self._has_new_sub_entities:
            return

        def add(entity: 'DXFEntity'):
            entity.doc = self.doc  # grant same document
            db.add(entity)

        if not self.seqend or not self.seqend.is_alive:
            self.new_seqend()
        self.process_sub_entities(add)
        self._has_new_sub_entities = False

    def new_seqend(self):
        """ Create new SEQEND. (internal API) """
        attribs = {'layer': self.dxf.layer}
        if self.doc:
            seqend = factory.create_db_entry('SEQEND', attribs, self.doc)
        else:
            seqend = factory.new('SEQEND', attribs)
        self.link_seqend(seqend)
        self._has_new_sub_entities = True

    def set_owner(self, owner: str, paperspace: int = 0):
        """ Set owner of all sub-entities and SEQEND. (internal API) """
        # Loading from file: POLYLINE/INSERT will be added to layout before
        # vertices/attrib entities are linked, so set_owner() of POLYLINE does
        # not set owner of vertices at loading time.
        super().set_owner(owner, paperspace)
        for entity in self.all_sub_entities():
            if isinstance(entity, DXFGraphic):
                entity.set_owner(owner, paperspace)
            else:  # SEQEND
                entity.dxf.owner = owner

    def export_dxf_sub_entities(self, tagwriter: 'TagWriter'):
        """ Export all sub-entities and SEQEND as DXF. """
        for entity in self.all_sub_entities():
            entity.export_dxf(tagwriter)

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
