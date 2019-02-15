# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-15
from typing import TYPE_CHECKING
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter
    from .dxfentity import DXFNamespace

__all__ = ['Line', 'acdb_line', 'export_acdb_line']

acdb_line = DefSubclass('AcDbLine', {
    'start': DXFAttr(10, xtype=XType.point3d),
    'end': DXFAttr(11, xtype=XType.point3d),
    'thickness': DXFAttr(39, default=0),
    'extrusion': DXFAttr(210, xtype=XType.point3d, default=(0.0, 0.0, 1.0)),
})


def export_acdb_line(attribs: 'DXFNamespace', tagwriter: 'TagWriter'):
    """ Export subclass 'AcDbEntity' as DXF tags. """
    if tagwriter.dxfversion > DXF12:
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_line.name)
    # for all DXF versions
    attribs.export_dxf_attribs(tagwriter, ['start', 'end', 'thickness', 'extrusion'])


class Line(DXFGraphic):
    """ DXF LINE entity """
    DXFTYPE = 'LINE'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_line)
    DEFAULT_ATTRIBS = {
        'start': (0, 0, 0),
        'end': (0, 0, 0),
    }

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        """
        Adds subclass processing for 'AcDbLine', requires previous base class and 'AcDbEntity' processing by parent
        class.
        """
        dxf = super().load_dxf_attribs(processor)
        if processor is None:
            return dxf

        tags = processor.load_dxfattribs_into_namespace(dxf, acdb_line)
        if len(tags) and not processor.r12:
            processor.log_unprocessed_tags(tags, subclass=acdb_line.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class (handle, appoid, reactors, xdict, owner) export is done by parent class
        # 'AcDbEntity' export is done by parent class
        super().export_entity(tagwriter)
        export_acdb_line(self.dxf, tagwriter)
        # xdata and embedded objects  export is also done by parent
