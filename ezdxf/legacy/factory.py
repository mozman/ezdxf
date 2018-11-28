# Purpose: legacy dxf factory for DXF R12/AC1009
# Created: 11.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from ezdxf.lldxf.const import DXFValueError, DXFKeyError

from . import tableentries
from . import graphics
from . import polyline
from . import trace
from . import text
from . import attrib
from . import block
from . import insert
from . import dimension
from . import viewport
from .layouts import DXF12Layouts, DXF12BlockLayout



ENTITY_WRAPPERS = {
    # tables entries
    'LAYER': tableentries.Layer,
    'DIMSTYLE': tableentries.DimStyle,
    'LTYPE': tableentries.Linetype,
    'APPID': tableentries.AppID,
    'STYLE': tableentries.Style,
    'UCS': tableentries.UCS,
    'VIEW': tableentries.View,
    'VPORT': tableentries.VPort,
    # dxf entities
    'LINE': graphics.Line,
    'POINT': graphics.Point,
    'CIRCLE': graphics.Circle,
    'ARC': graphics.Arc,
    'TRACE': trace.Trace,
    'SOLID': trace.Solid,
    '3DFACE': trace.Face,
    'TEXT': text.Text,
    'ATTRIB': attrib.Attrib,
    'ATTDEF': attrib.Attdef,
    'INSERT': insert.Insert,
    'BLOCK': block.Block,
    'ENDBLK': block.EndBlk,
    'POLYLINE': polyline.Polyline,
    'VERTEX': polyline.Vertex,
    'SEQEND': graphics.SeqEnd,
    'SHAPE': graphics.Shape,
    'VIEWPORT': viewport.Viewport,
    'DIMENSION': dimension.Dimension,
}


class LegacyDXFFactory(object):
    DEFAULT_WRAPPER = graphics.GraphicEntity

    def __init__(self, drawing):
        self.ENTITY_WRAPPERS = dict(ENTITY_WRAPPERS)
        self.drawing = drawing

    @property
    def entitydb(self):
        return self.drawing.entitydb

    @property
    def handles(self):
        return self.entitydb.handles

    @property
    def blocks(self):
        return self.drawing.blocks

    @property
    def dxfversion(self):
        return self.drawing.dxfversion

    def new_entity(self, dxftype, handle, dxfattribs):
        """ Create a new entity. """
        wrapper_class = self.get_wrapper_class(dxftype)
        entity = wrapper_class.new(handle, dxfattribs, self.drawing)
        # track used DXF types, but only for new created DXF entities
        self.drawing.tracker.dxftypes.add(dxftype)
        return entity

    def get_wrapper_class(self, dxftype):
        # future feature: to track all used DXF types, this is the right place
        return self.ENTITY_WRAPPERS.get(dxftype, self.DEFAULT_WRAPPER)

    def wrap_entity(self, tags):
        wrapper_class = self.get_wrapper_class(tags.dxftype())
        entity = wrapper_class(tags, self.drawing)
        if hasattr(entity, 'cast'):
            entity = entity.cast()
        return entity

    def wrap_handle(self, handle):
        try:
            tags = self.entitydb[handle]
        except KeyError:
            raise DXFKeyError('invalid handle #{}'.format(handle))

        return self.wrap_entity(tags)

    def create_db_entry(self, type_, dxfattribs):
        """ Create new entity and add to drawing-database. """
        handle = self.handles.next()
        dbentry = self.new_entity(type_, handle, dxfattribs)
        self.entitydb[handle] = dbentry.tags
        return dbentry

    def get_layouts(self):
        return DXF12Layouts(self.drawing)

    def create_block_entry_in_block_records_table(self, block_layout):
        # required for DXFVERSION > ac1009: Entry in the BLOCK_RECORDS section
        pass

    def new_block_layout(self, block_handle, endblk_handle):
        return DXF12BlockLayout(self.entitydb, self, block_handle, endblk_handle)

    def copy_layout(self, source_entity, target_entity):
        # Place target_entity in same layout as source_entity
        target_entity.dxf.paperspace = source_entity.dxf.paperspace

    def get_layout_for_entity(self, entity):
        dwg = self.drawing
        layout = dwg.layouts.get_layout_for_entity(entity)
        if layout is not None:
            return layout
        handle = entity.dxf.handle
        for block in dwg.blocks:  # search block definitions
            if handle in block._entity_space:
                return block
        return None
