# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, Callable
from abc import abstractmethod
from ezdxf.entities import factory, DXFGraphic
if TYPE_CHECKING:
    from ezdxf.eztypes import DXFEntity, TagWriter, EntityDB


class LinkedEntitiesMixin:
    """ Mixin for common features of the INSERT and the POLYLINE entity.

    Both have linked entities.
    """
    @abstractmethod
    def all_sub_entities(self) -> Iterable['DXFEntity']:
        """ Yield ALL entities."""
        pass

    def process_sub_entities(self, func: Callable[['DXFEntity'], None]):
        """ Call `func` for each sub-entity (VERTEX, SEQEND).

        (internal API)
        """
        for entity in self.all_sub_entities():
            if entity.is_alive:
                func(entity)

    def add_sub_entities_to_entitydb(self, db: 'EntityDB') -> None:
        """ Add sub-entities (VERTEX, ATTRIB, SEQEND) to entity database `db`,
        called from EntityDB.

        (internal API)
        """
        if not self._has_new_sub_entities:
            return

        def add(entity: 'DXFEntity'):
            entity.doc = self.doc  # grant same document
            db.add(entity)

        self.process_sub_entities(add)
        if not self.seqend or not self.seqend.is_alive:
            self.new_seqend()
        self._has_new_sub_entities = False

    def new_seqend(self):
        """ Create new ENDSEQ. (internal API)"""
        seqend = factory.create_db_entry(
            'SEQEND',
            dxfattribs={'layer': self.dxf.layer},
            doc=self.doc,
        )
        self.link_seqend(seqend)
        self._has_new_sub_entities = True

    def link_seqend(self, seqend: 'DXFEntity') -> None:
        seqend.dxf.owner = self.dxf.owner
        self.seqend = seqend

    def export_seqend(self, tagwriter: 'TagWriter'):
        self.seqend.dxf.owner = self.dxf.owner
        self.seqend.dxf.layer = self.dxf.layer
        self.seqend.export_dxf(tagwriter)

    def set_owner(self, owner: str, paperspace: int = 0):
        # Loading from file: POLYLINE/INSERT will be added to layout before
        # vertices/attrib entities are linked, so set_owner() of POLYLINE does
        # not set owner of vertices at loading time.
        super().set_owner(owner, paperspace)
        for entity in self.all_sub_entities():
            if isinstance(entity, DXFGraphic):
                entity.set_owner(owner, paperspace)
            else:  # SEQEND
                entity.dxf.owner = owner
