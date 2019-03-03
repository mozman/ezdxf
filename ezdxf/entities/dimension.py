# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-22
from typing import TYPE_CHECKING
from ezdxf.math import Vector
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER, DXF2010, DXF2000
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity
from .factory import register_entity
from ezdxf.lldxf.const import DXFInternalEzdxfError, DXFValueError
from ezdxf.lldxf.types import get_xcode_for
from ezdxf.tools import take2
import logging

if TYPE_CHECKING:
    from ezdxf.eztypes2 import TagWriter, DimStyle, DXFNamespace

logger = logging.getLogger('ezdxf')

__all__ = ['Dimension']

acdb_dimension = DefSubclass('AcDbDimension', {
    'version': DXFAttr(280, default=0, dxfversion=DXF2010),  # Version number: 0 = 2010
    'geometry': DXFAttr(2),  # Name of the block that contains the entities that make up the dimension picture
    'dimstyle': DXFAttr(3, default='Standard'),  # dimension style name
    # The dimension style is stored in doc.sections.tables.dimstyles,
    # shortcut Drawings.dimstyles property
    'defpoint': DXFAttr(10, xtype=XType.point3d, default=Vector(0, 0, 0)),  # definition point for all dimension types
    'text_midpoint': DXFAttr(11, xtype=XType.point3d),  # midpoint of dimension text
    'dimtype': DXFAttr(70, default=0),  # Dimension type:
    # Values 0–6 are integer values that represent the dimension type.
    # Values 32, 64, and 128 are bit values, which are added to the integer values
    # (value 32 is always set in R13 and later releases)
    # 0 = Rotated, horizontal, or vertical;
    # 1 = Aligned
    # 2 = Angular;
    # 3 = Diameter;
    # 4 = Radius
    # 5 = Angular 3 point;
    # 6 = Ordinate
    # 32 = Indicates that the block reference (group code 2) is referenced by this dimension only
    # 64 = Ordinate type. This is a bit value (bit 7) used only with integer
    # value 6. If set, ordinate is X-type; if not set, ordinate is Y-type
    # 128 = This is a bit value (bit 8) added to the other group 70 values if
    # the dimension text has been positioned at a user-defined location
    # rather than at the default location

    'attachment_point': DXFAttr(71, default=5, dxfversion=DXF2000),  # Attachment point:
    # 1 = Top left; 2 = Top center; 3 = Top right
    # 4 = Middle left; 5 = Middle center; 6 = Middle right
    # 7 = Bottom left; 8 = Bottom center; 9 = Bottom right

    'line_spacing_style': DXFAttr(72, default=1, dxfversion=DXF2000, optional=True),
    # Dimension text line-spacing style
    # 1 (or missing) = At least (taller characters will override)
    # 2 = Exact (taller characters will not override)
    'line_spacing_factor': DXFAttr(41, dxfversion=DXF2000, optional=True),  # Dimension text-line spacing factor
    # Percentage of default (3-on-5) line spacing to be applied. Valid values
    # range from 0.25 to 4.00
    'actual_measurement': DXFAttr(42, dxfversion=DXF2000, optional=True),
    # Actual measurement (optional; read-only value)
    'text': DXFAttr(1, default='', optional=True),  # Dimension text explicitly entered by the user
    # default is the measurement.
    # If null or “<>”, the dimension measurement is drawn as the text,
    # if “ “ (one blank space), the text is suppressed.
    # Anything else is drawn as the text.
    'oblique_angle': DXFAttr(52, default=0, optional=True),
    # Linear dimension types with an oblique angle have an optional group
    # code 52. When added to the rotation angle of the linear dimension (group code 50), it gives the angle of the
    # extension lines (DXF reference error: false subclass AcDbAlignedDimension)
    'text_rotation': DXFAttr(53, default=0, optional=True),
    # The optional group code 53 is the rotation angle of the dimension
    # text away from its default orientation (the direction of the dimension line) (optional)
    'horizontal_direction': DXFAttr(51, default=0, optional=True),
    # All dimension types have an optional 51 group code, which
    # indicates the horizontal direction for the dimension entity. The dimension entity determines the orientation of
    # dimension text and lines for horizontal, vertical, and rotated linear dimensions. This group value is the negative
    # of the angle between the OCS X axis and the UCS X axis. It is always in the XY plane of the OCS
    'extrusion': DXFAttr(210, xtype=XType.point3d, default=Vector(0, 0, 1), optional=True),
})

acdb_dimension_dummy = DefSubclass('AcDbDimensionDummy', {
    'insert': DXFAttr(12, xtype=XType.point3d, default=Vector(0, 0, 0)),  # Insertion point for clones of a
    # dimension—Baseline and Continue (in OCS)
    'defpoint2': DXFAttr(13, xtype=XType.point3d, default=Vector(0, 0, 0)),
    # Definition point for linear and angular dimensions (in WCS)
    'defpoint3': DXFAttr(14, xtype=XType.point3d, default=Vector(0, 0, 0)),
    # Definition point for linear and angular dimensions (in WCS)
    # The defpoint2 (13,23,33) specifies the start point of the first extension line and
    # the defpoint3 (14,24,34) specifies the start point of the second extension line.
    # Defpoint (10,20,30) specifies the dimension line location. The text_midpoint (11,21,31)
    # specifies the midpoint of the dimension text.
    'angle': DXFAttr(50, default=0),  # Angle of rotated, horizontal, or vertical dimensions
    'defpoint4': DXFAttr(15, xtype=XType.point3d, default=Vector(0, 0, 0)),
    # Definition point for diameter, radius, and angular dimensions (in WCS)
    'leader_length': DXFAttr(40),  # Leader length for radius and diameter dimensions
    'defpoint5': DXFAttr(16, xtype=XType.point3d, default=Vector(0, 0, 0)),
    # Point defining dimension arc for angular dimensions (in OCS)
    # The defpoint2 (13,23,33) and defpoint3 (14,24,34) specify the endpoints of the line used to determine the first
    # extension line. Defpoint (10,20,30) and defpoint4 (15,25,35) specify the endpoints of the line used to determine
    # the second extension line. Defpoint5 (16,26,36) specifies the location of the dimension line arc.
    # The text_midpoint (11,21,31) specifies the midpoint of the dimension text.
})


@register_entity
class Dimension(DXFGraphic):
    """ DXF DIMENSION entity """
    DXFTYPE = 'DIMENSION'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_dimension, acdb_dimension_dummy)

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.load_dxfattribs_into_namespace(dxf, acdb_dimension)
            if len(tags) and not processor.r12:
                processor.log_unprocessed_tags(tags, subclass=acdb_dimension.name)
            tags = processor.load_dxfattribs_into_namespace(dxf, acdb_dimension_dummy, index=4)
            # ignore possible 5. subclass AcDbRotatedDimension, has no content
            if len(tags) and not processor.r12:
                processor.log_unprocessed_tags(tags, subclass=acdb_dimension_dummy.name)

        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        if tagwriter.dxfversion == DXF12:
            self.dxf.export_dxf_attribs(tagwriter, [
                'geometry', 'dimstyle', 'defpoint', 'text_midpoint', 'insert', 'dimtype', 'text', 'defpoint2',
                'defpoint3', 'defpoint4', 'defpoint5', 'leader_length', 'angle', 'horizontal_direction',
                'oblique_angle', 'text_rotation'
            ])
            return

        # else DXF2000+
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_dimension.name)
        self.dxf.export_dxf_attribs(tagwriter, [
            'version', 'geometry', 'dimstyle', 'defpoint', 'text_midpoint', 'dimtype', 'attachment_point',
            'line_spacing_style', 'line_spacing_factor', 'actual_measurement', 'text', 'oblique_angle',
            'text_rotation', 'horizontal_direction', 'extrusion',
        ])
        dxfversion = tagwriter.dxfversion
        dim_type = self.dim_type
        if dim_type == 0:  # linear
            tagwriter.write_tag2(SUBCLASS_MARKER, 'AcDbAlignedDimension')
            self.dxf.export_dxf_attribs(tagwriter, ['defpoint2', 'defpoint3', 'angle'])
            # empty but required subclass
            tagwriter.write_tag2(SUBCLASS_MARKER, 'AcDbRotatedDimension')
        elif dim_type == 1:  # aligned
            tagwriter.write_tag2(SUBCLASS_MARKER, 'AcDbAlignedDimension')
            self.dxf.export_dxf_attribs(tagwriter, ['defpoint2', 'defpoint3', 'angle'])
        elif dim_type == 2:  # angular & angulr3p
            tagwriter.write_tag2(SUBCLASS_MARKER, 'AcDb2LineAngularDimension')
            self.dxf.export_dxf_attribs(tagwriter, ['defpoint2', 'defpoint3', 'defpoint4', 'defpoint5'])
        elif dim_type == 3:  # diameter
            tagwriter.write_tag2(SUBCLASS_MARKER, 'AcDbDiametricDimension')
            self.dxf.export_dxf_attribs(tagwriter, ['defpoint4', 'leader_length'])
        elif dim_type == 4:  # radius
            tagwriter.write_tag2(SUBCLASS_MARKER, 'AcDbRadialDimension')
            self.dxf.export_dxf_attribs(tagwriter, ['defpoint4', 'leader_length'])
        elif dim_type == 5:  # angular & angulr3p
            tagwriter.write_tag2(SUBCLASS_MARKER, 'AcDb3dPointAngularDimension')
            self.dxf.export_dxf_attribs(tagwriter, ['defpoint2', 'defpoint3', 'defpoint4', 'defpoint5'])
        elif dim_type == 6:  # ordinate
            tagwriter.write_tag2(SUBCLASS_MARKER, 'AcDbOrdinateDimension')
            self.dxf.export_dxf_attribs(tagwriter, ['defpoint3', 'defpoint3'])

    @property
    def dim_type(self) -> int:
        return self.dxf.dimtype & 7

    def dim_style(self) -> 'DimStyle':
        if self.drawing is None:
            raise DXFInternalEzdxfError('Dimension.drawing attribute not initialized.')

        dim_style_name = self.dxf.dimstyle
        # raises ValueError if not exists, but all used dim styles should exists!
        return self.drawing.dimstyles.get(dim_style_name)

    def cast(self) -> 'Dimension':  # for modern dimension lines
        return self

    def dim_style_attributes(self) -> 'DXFAttributes':
        return self.dim_style().DXFATTRIBS

    def set_acad_dstyle(self, data: dict) -> None:
        if self.doc is None:
            raise DXFInternalEzdxfError('Dimension.doc attribute not initialized.')

        # replace virtual 'dimtxsty' attribute by 'dimtxsty_handle'
        if 'dimtxsty' in data:
            dimtxsty = data.pop('dimtxsty')
            txtstyle = self.doc.styles.get(dimtxsty)
            data['dimtxsty_handle'] = txtstyle.dxf.handle

        tags = []
        dim_style_attributes = self.dim_style_attributes()
        for key, value in data.items():
            if key not in dim_style_attributes:  # ignore unknown attributes, but log
                logging.debug('ignore unknown DIMSTYLE attribute: "{}"'.format(key))
                continue
            dxf_attr = dim_style_attributes.get(key)
            if dxf_attr and dxf_attr.code > 0:  # skip internal and virtual tags
                code = dxf_attr.code
                tags.append((1070, code))
                if code == 5:  # DimStyle 'dimblk' has group code 5 but is not a handle
                    tags.append((1000, value))
                else:
                    tags.append((get_xcode_for(code), value))

        if len(tags):
            self.set_xdata_list('ACAD', 'DSTYLE', tags)

    def get_acad_dstyle(self, dim_style: 'DimStyle') -> dict:
        try:
            data = self.get_xdata_list('ACAD', 'DSTYLE')
        except DXFValueError:
            return {}
        attribs = {}
        codes = dim_style.CODE_TO_DXF_ATTRIB
        for code_tag, value_tag in take2(data):
            group_code = code_tag.value
            value = value_tag.value
            if group_code in codes:
                attribs[codes[group_code]] = value
        return attribs
