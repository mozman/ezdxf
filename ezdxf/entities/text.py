# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-15
from typing import TYPE_CHECKING, Tuple, Union
from ezdxf.math import Vector
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType, DXFValueError
from ezdxf.lldxf import const
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes2 import TagWriter, Vertex, DXFNamespace

__all__ = ['Text', 'acdb_text']

acdb_text = DefSubclass('AcDbText', {
    'insert': DXFAttr(10, xtype=XType.point3d, default=Vector(0, 0, 0)),  # First alignment point (in OCS)
    'height': DXFAttr(40, default=2.5),  # Text height
    'text': DXFAttr(1, default=''),  # Default value (the string itself)
    'rotation': DXFAttr(50, default=0, optional=True),  # Text rotation (optional) in degrees (circle = 360deg)
    'oblique': DXFAttr(51, default=0, optional=True),  # Oblique angle (optional) in degrees, vertical = 0deg
    'style': DXFAttr(7, default='Standard', optional=True),  # Text style name (optional)
    'width': DXFAttr(41, default=1, optional=True),  # Relative X scale factor—width (optional)
    # This value is also adjusted when fit-type text is used
    'text_generation_flag': DXFAttr(71, default=0, optional=True),  # Text generation flags (optional)
    # 2 = backward (mirror-x),
    # 4 = upside down (mirror-y)

    # Horizontal text justification type (optional) horizontal justification
    'halign': DXFAttr(72, default=0, optional=True),
    # 0 = Left
    # 2 = Right
    # 3 = Aligned (if vertical alignment = 0)
    # 4 = Middle (if vertical alignment = 0)
    # 5 = Fit (if vertical alignment = 0)

    # This value is meaningful only if the value of a 72 or 73 group is nonzero (if the justification is anything other
    # than baseline/left)
    'align_point': DXFAttr(11, xtype=XType.point3d, optional=True),  # Second alignment point (in OCS) (optional)
    'thickness': DXFAttr(39, default=0, optional=True),  # Thickness (optional)
    # Extrusion direction (optional)
    'extrusion': DXFAttr(210, xtype=XType.point3d, default=Vector(0, 0, 1), optional=True),
})

acdb_text2 = DefSubclass('AcDbText', {
    'valign': DXFAttr(73, default=0, optional=True)  # Vertical text justification type (optional)
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
    # horizontal align values
    LEFT = 0
    CENTER = 1
    RIGHT = 2
    # vertical align values
    BASELINE = 0
    BOTTOM = 1
    MIDDLE = 2
    TOP = 3
    # text generation flags
    MIRROR_X = 2
    MIRROR_Y = 4
    BACKWARD = MIRROR_X
    UPSIDE_DOWN = MIRROR_Y

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
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
        self.export_acdb_text(tagwriter)
        self.export_acdb_text2(tagwriter)

    def export_acdb_text(self, tagwriter: 'TagWriter') -> None:
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_text.name)
        # for all DXF versions
        self.dxf.export_dxf_attribs(tagwriter, [
            'insert', 'height', 'text', 'thickness', 'rotation', 'oblique', 'style', 'width', 'text_generation_flag',
            'halign', 'align_point', 'extrusion'
        ])

    def export_acdb_text2(self, tagwriter: 'TagWriter') -> None:
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_text2.name)
        self.dxf.export_dxf_attribs(tagwriter, 'valign')

    def set_pos(self, p1: 'Vertex', p2: 'Vertex' = None, align: str = None) -> 'Text':
        if align is None:
            align = self.get_align()
        align = align.upper()
        self.set_align(align)
        self.set_dxf_attrib('insert', p1)
        if align in ('ALIGNED', 'FIT'):
            if p2 is None:
                raise DXFValueError("Alignment '{}' requires a second alignment point.".format(align))
        else:
            p2 = p1
        self.set_dxf_attrib('align_point', p2)
        return self

    def get_pos(self) -> Tuple[str, 'Vertex', Union['Vertex', None]]:
        p1 = self.dxf.insert
        p2 = self.get_dxf_attrib('align_point', (0., 0., 0.))
        align = self.get_align()
        if align == 'LEFT':
            return align, p1, None
        if align in ('FIT', 'ALIGN'):
            return align, p1, p2
        return align, p2, None

    def set_align(self, align: str = 'LEFT') -> 'Text':
        align = align.upper()
        halign, valign = const.TEXT_ALIGN_FLAGS[align]
        self.set_dxf_attrib('halign', halign)
        self.set_dxf_attrib('valign', valign)
        return self

    def get_align(self) -> str:
        halign = self.get_dxf_attrib('halign', 0)
        valign = self.get_dxf_attrib('valign', 0)
        if halign > 2:
            valign = 0
        return const.TEXT_ALIGNMENT_BY_FLAGS.get((halign, valign), 'LEFT')
