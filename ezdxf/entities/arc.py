# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-15
from typing import TYPE_CHECKING
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import acdb_entity
from .circle import acdb_circle, Circle
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes2 import TagWriter, DXFNamespace

__all__ = ['Arc']


acdb_arc = DefSubclass('AcDbArc', {
    'start_angle': DXFAttr(50, default=0),
    'end_angle': DXFAttr(51, default=360),
})


@register_entity
class Arc(Circle):
    """ DXF ARC entity """
    DXFTYPE = 'ARC'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_circle, acdb_arc)

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.load_dxfattribs_into_namespace(dxf, acdb_arc)
            if len(tags) and not processor.r12:
                processor.log_unprocessed_tags(tags, subclass=acdb_arc.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        # AcDbCircle export is done by parent class
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_arc.name)
        # for all DXF versions
        self.dxf.export_dxf_attribs(tagwriter, ['start_angle', 'end_angle'])

