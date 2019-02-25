# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-21
from typing import TYPE_CHECKING
from ezdxf.math import Vector
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER, VERTEXNAMES
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes2 import TagWriter, DXFNamespace

__all__ = ['Solid', 'Trace', 'Face3d']


acdb_trace = DefSubclass('AcDbTrace', {
    'vtx0': DXFAttr(10, xtype=XType.point3d, default=Vector(0, 0, 0)),  # 1. corner Solid WCS; Trace OCS
    'vtx1': DXFAttr(11, xtype=XType.point3d, default=Vector(0, 0, 0)),  # 2. corner Solid WCS; Trace OCS
    'vtx2': DXFAttr(12, xtype=XType.point3d, default=Vector(0, 0, 0)),  # 3. corner Solid WCS; Trace OCS
    # If only three corners are entered to define the SOLID, then the fourth corner coordinate is the same as the third.
    'vtx3': DXFAttr(13, xtype=XType.point3d, default=Vector(0, 0, 0)),  # 4. corner Solid WCS; Trace OCS
    'thickness': DXFAttr(39, default=0, optional=True),  # Thickness
    'extrusion': DXFAttr(210, xtype=XType.point3d, default=Vector(0, 0, 1), optional=True),  # Extrusion direction
})


class _Base(DXFGraphic):
    def __getitem__(self, num):
        return self.dxf.get(VERTEXNAMES[num])

    def __setitem__(self, num, value):
        return self.dxf.set(VERTEXNAMES[num], value)


@register_entity
class Solid(_Base):
    """ DXF SHAPE entity """
    DXFTYPE = 'SOLID'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_trace)

    def __getitem__(self, num):
        return self.dxf.get(VERTEXNAMES[num])

    def __setitem__(self, num, value):
        return self.dxf.set(VERTEXNAMES[num], value)

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.load_dxfattribs_into_namespace(dxf, acdb_trace)
            if len(tags) and not processor.r12:
                processor.log_unprocessed_tags(tags, acdb_trace.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_trace.name)
        # for all DXF versions
        if not self.dxf.hasattr('vtx3'):
            self.dxf.vtx3 = self.dxf.vtx2
        self.dxf.export_dxf_attribs(tagwriter, [
            'vtx0', 'vtx1', 'vtx2', 'vtx3', 'thickness', 'extrusion',
        ])


@register_entity
class Trace(Solid):
    """ DXF TRACE entity """
    DXFTYPE = 'TRACE'


acdb_face = DefSubclass('AcDbFace', {
    'vtx0': DXFAttr(10, xtype=XType.point3d, default=Vector(0, 0, 0)),  # 1. corner WCS
    'vtx1': DXFAttr(11, xtype=XType.point3d, default=Vector(0, 0, 0)),  # 2. corner WCS
    'vtx2': DXFAttr(12, xtype=XType.point3d, default=Vector(0, 0, 0)),  # 3. corner WCS
    # If only three corners are entered to define the SOLID, then the fourth corner coordinate is the same as the third.
    'vtx3': DXFAttr(13, xtype=XType.point3d, default=Vector(0, 0, 0)),  # 4. corner WCS
    'invisible': DXFAttr(70, default=0, optional=True),  # Invisible edge flags
    # 1 = First edge is invisible
    # 2 = Second edge is invisible
    # 4 = Third edge is invisible
    # 8 = Fourth edge is invisible
})


@register_entity
class Face3d(_Base):
    """ DXF 3DFACE entity """
    DXFTYPE = '3DFACE'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_face)

    def is_invisible_edge(self, num)->bool:
        """ Returns True if edge `num` is an invisible edge. """
        return bool(self.dxf.invisible & (1 << num))

    def set_edge_visibilty(self, num, status=False):
        """ Set visibilty of edge `num`, status `True` for visible, status `False` for invisible. """
        if status:
            self.dxf.invisible = self.dxf.invisible | (1 << num)
        else:
            self.dxf.invisible = self.dxf.invisible & ~(1 << num)

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.load_dxfattribs_into_namespace(dxf, acdb_face)
            if len(tags) and not processor.r12:
                processor.log_unprocessed_tags(tags, acdb_face.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_face.name)
        # for all DXF versions
        if not self.dxf.hasattr('vtx3'):
            self.dxf.vtx3 = self.dxf.vtx2
        self.dxf.export_dxf_attribs(tagwriter, ['vtx0', 'vtx1', 'vtx2', 'vtx3', 'invisible'])
