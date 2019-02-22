# Created: 17.02.2019
# Copyright (c) 2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING
import logging
from ezdxf.math import Vector
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER
from ezdxf.entities.dxfentity import base_class, SubclassProcessor, DXFEntity
from ezdxf.entities.layer import acdb_symbol_table_record
from .factory import register_entity

logger = logging.getLogger('ezdxf')

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter
    from ezdxf.entities.dxfentity import DXFNamespace

__all__ = ['VPort']

# todo DXF2000+ support for VPORT
acdb_vport = DefSubclass('AcDbViewportTableRecord', {
    'name': DXFAttr(2),
    'flags': DXFAttr(70, default=0),
    'lower_left': DXFAttr(10, xtype=XType.point2d, default=(0, 0)),
    'upper_right': DXFAttr(11, xtype=XType.point2d, default=(1, 1)),
    'center': DXFAttr(12, xtype=XType.point2d, default=(70, 50)),
    'snap_base': DXFAttr(13, xtype=XType.point2d, default=(0, 0)),
    'snap_spacing': DXFAttr(14, xtype=XType.point2d, default=(.5, .5)),
    'grid_spacing': DXFAttr(15, xtype=XType.point2d, default=(.5, .5)),
    'direction': DXFAttr(16, xtype=XType.point3d, default=Vector(0, 0, 1)),
    'target': DXFAttr(17, xtype=XType.point3d, default=Vector(0, 0, 0)),
    'height': DXFAttr(40, default=1),
    'aspect_ratio': DXFAttr(41, default=1.34),
    'focal_length': DXFAttr(42, default=50),
    'front_clipping': DXFAttr(43, default=0),
    'back_clipping': DXFAttr(44, default=0),
    'snap_rotation': DXFAttr(50, default=0),
    'view_twist': DXFAttr(51, default=0),
    'view_mode': DXFAttr(71, default=0),
    'circle_zoom': DXFAttr(72, default=1000),
    'fast_zoom': DXFAttr(73, default=1),
    'ucs_icon': DXFAttr(74, default=3),
    'snap_on': DXFAttr(75, default=0),
    'grid_on': DXFAttr(76, default=0),
    'snap_style': DXFAttr(77, default=0),
    'snap_isopair': DXFAttr(78, default=0),
})

EXPORT_MAP = [
    'name', 'flags', 'lower_left', 'upper_right', 'center', 'snap_base', 'snap_spacing', 'grid_spacing', 'direction',
    'target', 'height', 'aspect_ratio', 'focal_length', 'front_clipping', 'back_clipping', 'snap_rotation',
    'view_twist', 'view_mode', 'circle_zoom', 'fast_zoom', 'ucs_icon', 'snap_on', 'grid_on', 'snap_style',
    'snap_isopair',
]


@register_entity
class VPort(DXFEntity):
    """ DXF VIEW entity """
    DXFTYPE = 'VPORT'
    DXFATTRIBS = DXFAttributes(base_class, acdb_symbol_table_record, acdb_vport)

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.load_dxfattribs_into_namespace(dxf, acdb_vport)
            if len(tags) and not processor.r12:
                processor.log_unprocessed_tags(tags, subclass=acdb_vport.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_symbol_table_record.name)
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_vport.name)
        self.dxf.export_dxf_attribs(tagwriter, EXPORT_MAP)
