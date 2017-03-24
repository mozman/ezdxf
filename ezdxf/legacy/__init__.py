# Purpose: legacy dxf factory for R12/AC1009
# Created: 11.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
"""
File Sections
=============

The DXF file is subdivided into four editable sections, plus the END
OF FILE marker. File separator groups are used to delimit these file
sections. The following is an example of a void DXF file with only
the section markers and table headers present:

   0            (Begin HEADER section)
  SECTION
   2
  HEADER
               <<<<Header variable items go here>>>>
  0
  ENDSEC       (End HEADER section)
   0           (Begin TABLES section)
  SECTION
   2
  TABLES
   0
  TABLE
   2
  VPORT
   70
  (viewport table maximum item count)
               <<<<viewport table items go here>>>>
  0
  ENDTAB
  0
  TABLE
  2
  APPID, DIMSTYLE, LTYPE, LAYER, STYLE, UCS, VIEW, or VPORT
  70
  (Table maximum item count)
               <<<<Table items go here>>>>
  0
  ENDTAB
  0
  ENDSEC       (End TABLES section)
  0            (Begin BLOCKS section)
  SECTION
  2
  BLOCKS
               <<<<Block definition entities go here>>>>
  0
  ENDSEC       (End BLOCKS section)
  0            (Begin ENTITIES section)
  SECTION
  2
  ENTITIES
               <<<<Drawing entities go here>>>>
  0
  ENDSEC       (End ENTITIES section)
  0
  EOF          (End of file)

"""
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .headervars import VARMAP
from . import tableentries
from . import graphics
from .viewport import Viewport

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
    'VPORT': tableentries.Viewport,
    # dxf entities
    'LINE': graphics.Line,
    'POINT': graphics.Point,
    'CIRCLE': graphics.Circle,
    'ARC': graphics.Arc,
    'TRACE': graphics.Trace,
    'SOLID': graphics.Solid,
    '3DFACE': graphics.Face,
    'TEXT': graphics.Text,
    'ATTRIB': graphics.Attrib,
    'ATTDEF': graphics.Attdef,
    'INSERT': graphics.Insert,
    'BLOCK': graphics.Block,
    'ENDBLK': graphics.EndBlk,
    'POLYLINE': graphics.Polyline,
    'VERTEX': graphics.Vertex,
    'SEQEND': graphics.SeqEnd,
    'DIMENSION': graphics.Dimension,
    'SHAPE': graphics.Shape,
    'VIEWPORT': Viewport,
}


class LegacyDXFFactory(object):
    HEADERVARS = dict(VARMAP)
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


    def headervar_factory(self, key, value):
        factory = self.HEADERVARS[key]
        return factory(value)

    def new_entity(self, type_, handle, dxfattribs):
        """ Create a new entity. """
        try:
            class_ = self.ENTITY_WRAPPERS[type_]
            return class_.new(handle, dxfattribs, self.drawing)
        except KeyError:
            raise ValueError('Unsupported entity type: %s' % type_)

    def wrap_entity(self, tags):
        wrapper = self.ENTITY_WRAPPERS.get(tags.dxftype(), self.DEFAULT_WRAPPER)
        entity = wrapper(tags, self.drawing)
        if hasattr(entity, 'cast'):
            entity = entity.cast()
        return entity

    def wrap_handle(self, handle):
        tags = self.entitydb[handle]
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

    def modify_tags(self, tags):
        pass