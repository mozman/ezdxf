# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-15
from typing import TYPE_CHECKING
from ezdxf.math import Vector
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter
    from .dxfentity import DXFNamespace

__all__ = ['Point']

acdb_point = DefSubclass('AcDbPoint', {
    'location': DXFAttr(10, xtype=XType.point3d, default=Vector(0, 0, 0)),
    'thickness': DXFAttr(39, default=0),
    'extrusion': DXFAttr(210, xtype=XType.point3d, default=Vector(0, 0, 1)),
    # angle of the X axis for the UCS in effect when the point was drawn (optional, default = 0); used when PDMODE is
    # nonzero
    'angle': DXFAttr(50, default=0),
})


@register_entity
class Point(DXFGraphic):
    """ DXF POINT entity """
    DXFTYPE = 'POINT'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_point)

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor is None:
            return dxf

        tags = processor.load_dxfattribs_into_namespace(dxf, acdb_point)
        if len(tags) and not processor.r12:
            processor.log_unprocessed_tags(tags, subclass=acdb_point.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_point.name)
        # for all DXF versions
        self.dxf.export_dxf_attribute(tagwriter, 'location', force=True)
        self.dxf.export_dxf_attribs(tagwriter, ['thickness', 'extrusion', 'angle'])

