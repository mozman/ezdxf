# Created: 17.02.2019
# Copyright (c) 2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING
import logging
from ezdxf.math import UCS, Vector
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER
from ezdxf.entities.dxfentity import base_class, SubclassProcessor, DXFEntity
from ezdxf.entities.layer import acdb_symbol_table_record
from .factory import register_entity

logger = logging.getLogger('ezdxf')

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter
    from ezdxf.entities.dxfentity import DXFNamespace

__all__ = ['UCSTable']


acdb_ucs = DefSubclass('AcDbUCSTableRecord', {
    'name': DXFAttr(2),
    'flags': DXFAttr(70, default=0),
    'origin': DXFAttr(10, xtype=XType.point3d, default=Vector(0, 0, 0)),
    'xaxis': DXFAttr(11, xtype=XType.point3d, default=Vector(1, 0, 0)),
    'yaxis': DXFAttr(12, xtype=XType.point3d, default=Vector(0, 1, 0)),
})


@register_entity
class UCSTable(DXFEntity):
    """ DXF UCS table entity """
    DXFTYPE = 'UCS'
    DXFATTRIBS = DXFAttributes(base_class, acdb_symbol_table_record, acdb_ucs)

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor is None:
            return dxf

        tags = processor.load_dxfattribs_into_namespace(dxf, acdb_ucs)
        if len(tags) and not processor.r12:
            processor.log_unprocessed_tags(tags, subclass=acdb_ucs.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_symbol_table_record.name)
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_ucs.name)

        # for all DXF versions
        self.dxf.export_dxf_attribs(tagwriter, ['name', 'flags', 'origin', 'xaxis', 'yaxis'], force=True)

    def ucs(self) -> UCS:
        return UCS(
            origin=self.get_dxf_attrib('origin', default=(0, 0, 0)),
            ux=self.get_dxf_attrib('xaxis', default=(1, 0, 0)),
            uy=self.get_dxf_attrib('yaxis', default=(0, 1, 0)),
        )
