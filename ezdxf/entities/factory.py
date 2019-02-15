# Created: 2019-02-15
# Copyright (c) 2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Optional

from ezdxf.tools.handle import ImageKeyGenerator, UnderlayKeyGenerator
from ezdxf.lldxf.const import DXFKeyError

if TYPE_CHECKING:
    from ezdxf.eztypes import Drawing, Table

from ezdxf.entitydb import EntityDB
from .dxfentity import UnknownEntity, DXFEntity
from .dxfclass import DXFClass
from .line import Line
from .lwpolyline import LWPolyline

ENTITY_WRAPPERS = {
    'CLASS': DXFClass,
    'LINE': Line,
    'LWPOLYLINE': LWPolyline

}


class EntityFactory:
    DEFAULT_WRAPPER = UnknownEntity
    ENTITY_WRAPPERS = dict(ENTITY_WRAPPERS)

    def __init__(self, doc: 'Drawing'):
        self.doc = doc
        self.image_key_generator = ImageKeyGenerator()
        self.underlay_key_generator = UnderlayKeyGenerator()

    @property
    def entitydb(self) -> 'EntityDB':
        return self.doc.entitydb

    @property
    def dxfversion(self):
        return self.doc.dxfversion

    @property
    def rootdict(self) -> 'DXFDictionary':
        return self.doc.rootdict

    @property
    def blocks(self) -> 'BlocksSection':
        return self.doc.blocks

    @property
    def block_records(self) -> 'Table':
        return self.doc.sections.tables.block_records

    def new_entity(self, dxftype: str, handle: str = None, owner: str = None, dxfattribs: dict = None) -> 'DXFEntity':
        """ Create a new entity. """
        class_ = self.ENTITY_WRAPPERS.get(dxftype, self.DEFAULT_WRAPPER)
        entity = class_.new(handle, owner, dxfattribs, self.doc)
        # track used DXF types, but only for new created DXF entities
        self.doc.tracker.dxftypes.add(dxftype)
        return entity

    def create_db_entry(self, type_: str, dxfattribs: dict) -> 'DXFEntity':
        """ Create new entity and add to drawing-database. """
        entity = self.new_entity(type_, None, None, dxfattribs)
        self.entitydb.add(entity)
        return entity

    def get_layouts(self):
        return Layouts(self.doc)

    def create_block_entry_in_block_records_table(self, block_layout: 'BlockLayout') -> None:
        block_record = self.block_records.new(block_layout.name)
        block_layout.set_block_record_handle(block_record.dxf.handle)

    def new_block_layout(self, block_handle: str, endblk_handle: str) -> 'BlockLayout':
        # Warning: Do not call create_block_entry_in_block_records_table() from this point, this will not work!
        return BlockLayout(self.entitydb, self, block_handle, endblk_handle)

    def copy_layout(self, source_entity: 'DXFEntity', target_entity: 'DXFEntity'):
        """
        Place `target_entity` in same layout as `source_entity`
        """
        target_entity.dxf.paperspace = source_entity.dxf.paperspace
        target_entity.dxf.owner = source_entity.dxf.owner

    def next_image_key(self, checkfunc=lambda k: True) -> str:
        while True:
            key = self.image_key_generator.next()
            if checkfunc(key):
                return key

    def next_underlay_key(self, checkfunc=lambda k: True) -> str:
        while True:
            key = self.underlay_key_generator.next()
            if checkfunc(key):
                return key

    def get_layout_for_entity(self, entity: 'DXFEntity') -> Optional['GenericLayoutType']:
        if entity.dxf.owner not in self.entitydb:
            return None

        doc = self.doc
        try:
            layout = doc.layouts.get_layout_for_entity(entity)
        except DXFKeyError:
            block_rec = self.entitydb[entity.dxf.owner]
            block_name = block_rec.dxf.name
            layout = doc.blocks.get(block_name)
        return layout
