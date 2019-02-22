# Created: 17.02.2019
# Copyright (c) 2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Union, Iterable, cast
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
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_symbol_table_record.name)
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_view.name)
        self.dxf.export_dxf_attribs(tagwriter, [
            'name', 'flags', 'height', 'center', 'width', 'direction', 'focal_length', 'front_clipping',
            'back_clipping', 'view_twist', 'vie_mode'
        ], force=True)
