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

__all__ = ['Text']

acdb_text = DefSubclass('AcDbText', {
    'insert': DXFAttr(10, xtype=XType.point3d, default=Vector(0, 0, 0)),  # First alignment point (in OCS)
    'height': DXFAttr(40, default=2.5),  # Text height
    'text': DXFAttr(1, default=''),  # Default value (the string itself)
    'rotation': DXFAttr(50, default=0),  # Text rotation (optional) in degrees (circle = 360deg)
    'oblique': DXFAttr(51, default=0),  # Oblique angle (optional) in degrees, vertical = 0deg
    'style': DXFAttr(7, default='Standard'),  # Text style name (optional)
    'width': DXFAttr(41, default=1),  # Relative X scale factor—width (optional)
    # This value is also adjusted when fit-type text is used
    'text_generation_flag': DXFAttr(71, default=0),  # Text generation flags (optional)
    # 2 = backward (mirror-x),
    # 4 = upside down (mirror-y)
    'halign': DXFAttr(72, default=0),  # Horizontal text justification type (optional) horizontal justification
    # 0 = Left
    # 2 = Right
    # 3 = Aligned (if vertical alignment = 0)
    # 4 = Middle (if vertical alignment = 0)
    # 5 = Fit (if vertical alignment = 0)
    'align_point': DXFAttr(11, xtype=XType.point3d),  # Second alignment point (in OCS) (optional)
    # This value is meaningful only if the value of a 72 or 73 group is nonzero (if the justification is anything other
    # than baseline/left)
    'thickness': DXFAttr(39, default=0),  # Thickness (optional)
    'extrusion': DXFAttr(210, xtype=XType.point3d, default=Vector(0, 0, 1)),  # Extrusion direction (optional)
})

acdb_text2 = DefSubclass('AcDbText', {
    'valign': DXFAttr(73, default=0)  # Vertical text justification type (optional)
    # 0 = Baseline
    # 1 = Bottom
    # 2 = Middle
    # 3 = Top
})


@register_entity
class Text(DXFGraphic):
    """ DXF TEXT entity """
    DXFTYPE = 'TEXT'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_text, acdb_text2)

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor is None:
            return dxf

        tags = processor.load_dxfattribs_into_namespace(dxf, acdb_text, 2)
        if len(tags) and not processor.r12:
            processor.log_unprocessed_tags(tags, subclass=acdb_text.name)

        tags = processor.load_dxfattribs_into_namespace(dxf, acdb_text2, 3)
        if len(tags) and not processor.r12:
            processor.log_unprocessed_tags(tags, subclass=acdb_text2.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_text.name)
        # for all DXF versions
        self.dxf.export_dxf_attribs(tagwriter, ['insert', 'height', 'text'], force=True)
        self.dxf.export_dxf_attribs(tagwriter, [
            'thickness', 'rotation', 'oblique', 'style', 'width', 'text_generation_flag', 'halign', 'align_point',
            'extrusion'
        ])
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_text2.name)
        self.dxf.export_dxf_attribute(tagwriter, 'valign')
