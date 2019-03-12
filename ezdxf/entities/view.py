# Created: 17.02.2019
# Copyright (c) 2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING
import logging
from ezdxf.math import Vector
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER, DXF2000, DXF2007, DXF2010
from ezdxf.entities.dxfentity import base_class, SubclassProcessor, DXFEntity
from ezdxf.entities.layer import acdb_symbol_table_record
from .factory import register_entity

logger = logging.getLogger('ezdxf')

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, DXFNamespace

__all__ = ['View']

acdb_view = DefSubclass('AcDbViewTableRecord', {
    'name': DXFAttr(2),
    'flags': DXFAttr(70, default=0),
    'height': DXFAttr(40, default=1),
    'width': DXFAttr(41, default=1),
    'center': DXFAttr(10, xtype=XType.point2d, default=(0, 0)),
    'direction': DXFAttr(11, xtype=XType.point3d, default=Vector(1, 1, 1)),
    'target': DXFAttr(12, xtype=XType.point3d, default=Vector(0, 0, 0)),
    'focal_length': DXFAttr(42, default=50),
    'front_clipping': DXFAttr(43, default=0),
    'back_clipping': DXFAttr(44, default=0),
    'view_twist': DXFAttr(50, default=0),
    'view_mode': DXFAttr(71, default=0),
    'render_mode': DXFAttr(281, default=0, dxfversion=DXF2000),
    # Render mode:
    # 0 = 2D Optimized (classic 2D)
    # 1 = Wireframe
    # 2 = Hidden line
    # 3 = Flat shaded
    # 4 = Gouraud shaded
    # 5 = Flat shaded with wireframe
    # 6 = Gouraud shaded with wireframe
    'ucs': DXFAttr(72, default=0),  # 1 if there is a UCS associated to this view, 0 otherwise.
    'camera_plottable': DXFAttr(73, default=0, dxfversion=DXF2007),  # 1 if the camera is plottable
    'background_handle': DXFAttr(332, optional=True, dxfversion=DXF2007),
    'live_selection_handle': DXFAttr(334, optional=True, dxfversion=DXF2007),
    'visual_style_handle': DXFAttr(348, optional=True, dxfversion=DXF2007),
    'sun_handle': DXFAttr(361, optional=True, dxfversion=DXF2010),
})


@register_entity
class View(DXFEntity):
    """ DXF VIEW entity """
    DXFTYPE = 'VIEW'
    DXFATTRIBS = DXFAttributes(base_class, acdb_symbol_table_record, acdb_view)

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.load_dxfattribs_into_namespace(dxf, acdb_view)
            if len(tags) and not processor.r12:
                processor.log_unprocessed_tags(tags, subclass=acdb_view.name)
        # todo support for associated UCS
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_symbol_table_record.name)
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_view.name)

        if self.dxf.hasattr('ucs'):
            self.dxf.ucs = 0  # todo support for associated UCS
        self.dxf.export_dxf_attribs(tagwriter, [
            'name', 'flags', 'height', 'center', 'width', 'direction', 'focal_length', 'front_clipping',
            'back_clipping', 'view_twist', 'view_mode', 'render_mode', 'ucs', 'camera_plottable', 'background_handle',
            'live_selection_handle', 'visual_style_handle',
        ])
