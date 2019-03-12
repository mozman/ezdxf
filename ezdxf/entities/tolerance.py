# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-03-12
from typing import TYPE_CHECKING
from ezdxf.math import Vector
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.const import SUBCLASS_MARKER, DXF2000
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, DXFNamespace

__all__ = ['Tolerance']


acdb_tolerance = DefSubclass('AcDbFcf', {
    'dimstyle': DXFAttr(3, default='Standard'),
    'insert': DXFAttr(10, xtype=XType.point3d, default=Vector(0, 0, 0)),  # Insertion point (in WCS)
    'content': DXFAttr(1, default=""),  # String representing the visual representation of the tolerance
    'extrusion': DXFAttr(210, xtype=XType.point3d, default=Vector(0, 0, 1), optional=True),  # Extrusion direction
    'x_axis_vector': DXFAttr(11, xtype=XType.point3d, default=Vector(1, 0, 0)),  # X-axis direction vector (in WCS)
})


@register_entity
class Tolerance(DXFGraphic):
    """ DXF TOLERANCE entity """
    DXFTYPE = 'TOLERANCE'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_tolerance)
    MIN_DXF_VERSION_FOR_EXPORT = DXF2000

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.load_dxfattribs_into_namespace(dxf, acdb_tolerance)
            if len(tags):
                processor.log_unprocessed_tags(tags, subclass=acdb_tolerance.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_tolerance.name)
        self.dxf.export_dxf_attribs(tagwriter, [
            'dimstyle', 'insert', 'content', 'extrusion', 'x_axis_vector'
        ])
