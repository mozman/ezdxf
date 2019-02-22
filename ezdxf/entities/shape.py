# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-21
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

__all__ = ['Shape']


acdb_shape = DefSubclass('AcDbShape', {
    'thickness': DXFAttr(39, default=0),  # Thickness (optional)
    'insert': DXFAttr(10, xtype=XType.point3d, default=Vector(0, 0, 0)),  # Insertion point (in WCS)
    'size': DXFAttr(40, default=1),
    'name': DXFAttr(2, default=''),  # Shape name
    'rotation': DXFAttr(50, default=0),  # Rotation angle (optional) in degrees
    'xscale': DXFAttr(41, default=1),  # Relative X scale factor (optional)
    'oblique': DXFAttr(51, default=0),  # Oblique angle (optional)
    'extrusion': DXFAttr(210, xtype=XType.point3d, default=Vector(0, 0, 1)),  # Extrusion direction (optional)
})


@register_entity
class Shape(DXFGraphic):
    """ DXF SHAPE entity """
    DXFTYPE = 'SHAPE'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_shape)

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.load_dxfattribs_into_namespace(dxf, acdb_shape)
            if len(tags) and not processor.r12:
                processor.log_unprocessed_tags(tags, subclass=acdb_shape.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_shape.name)
        # for all DXF versions
        self.dxf.export_dxf_attribs(tagwriter, ['insert', 'size', 'name'], force=True)
        self.dxf.export_dxf_attribs(tagwriter, ['thickness', 'rotation', 'xscale', 'oblique', 'extrusion'])

