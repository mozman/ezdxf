# Created: 09.03.2016
# Copyright (c) 2016-2018, Manfred Moitzi
# License: MIT License
from ezdxf.legacy import dimension
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.const import DXFInternalEzdxfError
from ezdxf.lldxf.tags import Tags
from .graphics import none_subclass, entity_subclass, ModernGraphicEntity, ExtendedTags

dimension_subclass = DefSubclass('AcDbDimension', {
    'geometry': DXFAttr(2),  # name of pseudo-Block containing the current dimension  entity geometry
    'dimstyle': DXFAttr(3, default='STANDARD'),  # dimension style name
    # The dimension style is stored in Drawing.sections.tables.dimstyles,
    # shortcut Drawings.dimstyles property
    'defpoint': DXFAttr(10, xtype=XType.point3d, default=(0.0, 0.0, 0.0)),  # definition point for all dimension types
    'text_midpoint': DXFAttr(11, xtype=XType.any_point),  # middle point of dimension text
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
    'align': DXFAttr(71),  # Attachment point:
    # 1 = Top left; 2 = Top center; 3 = Top right
    # 4 = Middle left; 5 = Middle center; 6 = Middle right
    # 7 = Bottom left; 8 = Bottom center; 9 = Bottom right
    'line_spacing_style': DXFAttr(72, default=1),  # Dimension text line-spacing style (optional):
    # 1 (or missing) = At least (taller characters will override)
    # 2 = Exact (taller characters will not override)
    'line_spacing_factor': DXFAttr(41),  # Dimension text-line spacing factor (optional):
    # Percentage of default (3-on-5) line spacing to be applied. Valid values
    # range from 0.25 to 4.00
    'actual_measurement': DXFAttr(42),  # Actual measurement (optional; read-only value)
    'text': DXFAttr(1),  # Dimension text explicitly entered by the user. Optional;
    # default is the measurement.
    # If null or “<>”, the dimension measurement is drawn as the text,
    # if “ “ (one blank space), the text is suppressed.
    # Anything else is drawn as the text.
    'text_rotation': DXFAttr(53, default=0),  # The optional group code 53 is the rotation angle of the dimension
    # text away from its default orientation (the direction of the dimension line) (optional)
    'horizontal_direction': DXFAttr(51, default=0),  # All dimension types have an optional 51 group code, which
    # indicates the horizontal direction for the dimension entity. The dimension entity determines the orientation of
    # dimension text and lines for horizontal, vertical, and rotated linear dimensions. This group value is the negative
    # of the angle between the OCS X axis and the UCS X axis. It is always in the XY plane of the OCS
    'extrusion': DXFAttr(210, xtype=XType.point3d, default=(0.0, 0.0, 1.0)),
})

aligned_dimension_subclass = DefSubclass('AcDbAlignedDimension', {
    'insert': DXFAttr(12, xtype=XType.point3d, default=(0.0, 0.0, 0.0)),  # Insertion point for clones of a
    # dimension—Baseline and Continue (in OCS)
    'defpoint2': DXFAttr(13, xtype=XType.point3d, default=(0.0, 0.0, 0.0)),  # Definition point for linear and angular dimensions (in WCS)
    'defpoint3': DXFAttr(14, xtype=XType.point3d, default=(0.0, 0.0, 0.0)),  # Definition point for linear and angular dimensions (in WCS)
    # The defpoint2 (13,23,33) specifies the start point of the first extension line and
    # the defpoint3 (14,24,34) specifies the start point of the second extension line.
    # Defpoint (10,20,30) specifies the dimension line location. The text_midpoint (11,21,31)
    # specifies the midpoint of the dimension text.
    'angle': DXFAttr(50, default=0),  # Angle of rotated, horizontal, or vertical dimensions
    'oblique_angle': DXFAttr(52, default=0),  # Linear dimension types with an oblique angle have an optional group
    # code 52. When added to the rotation angle of the linear dimension (group code 50), it gives the angle of the
    # extension lines
})

rotated_dimension_subclass = DefSubclass('AcDbRotatedDimension', {
})

radial_diametric_attribs = {
    'defpoint4': DXFAttr(15, xtype=XType.point3d, default=(0.0, 0.0, 0.0)),  # Definition point for diameter, radius, and angular dimensions (in WCS)
    'leader_length': DXFAttr(40),  # Leader length for radius and diameter dimensions
}

radial_dimension_subclass = DefSubclass('AcDbRadialDimension', radial_diametric_attribs)

diametric_dimension_subclass = DefSubclass('AcDbDiametricDimension', radial_diametric_attribs)

angular_dimension_subclass = DefSubclass('AcDb3dPointAngularDimension', {
    'defpoint2': DXFAttr(13, xtype=XType.point3d, default=(0.0, 0.0, 0.0)),  # Definition point for linear and angular dimensions (in WCS)
    'defpoint3': DXFAttr(14, xtype=XType.point3d, default=(0.0, 0.0, 0.0)),  # Definition point for linear and angular dimensions (in WCS)
    'defpoint4': DXFAttr(15, xtype=XType.point3d, default=(0.0, 0.0, 0.0)),  # Definition point for diameter, radius, and angular dimensions (in WCS)
    'defpoint5': DXFAttr(16, xtype=XType.point3d, default=(0.0, 0.0, 0.0)),  # Point defining dimension arc for angular dimensions (in OCS)
    # The defpoint2 (13,23,33) and defpoint3 (14,24,34) specify the endpoints of the line used to determine the first
    # extension line. Defpoint (10,20,30) and defpoint4 (15,25,35) specify the endpoints of the line used to determine
    # the second extension line. Defpoint5 (16,26,36) specifies the location of the dimension line arc.
    # The text_midpoint (11,21,31) specifies the midpoint of the dimension text.

    # The point (15,25,35) specifies the vertex of the angle. The points (13,23,33)
    # and (14,24,34) specify the endpoints of the extension lines. The point
    # (10,20,30) specifies the location of the dimension line arc and the point
    # (11,21,31) specifies the midpoint of the dimension text.

})

ordinate_dimension_subclass = DefSubclass('AcDbOrdinateDimension', {
    'defpoint2': DXFAttr(13, xtype=XType.point3d, default=(0.0, 0.0, 0.0)),  # Definition point for linear and angular dimensions (in WCS)
    'defpoint3': DXFAttr(14, xtype=XType.point3d, default=(0.0, 0.0, 0.0)),  # Definition point for linear and angular dimensions (in WCS)
    # The defpoint1 (13,23,33) specifies the feature location and the defpoint2 (14,24,34) specifies the leader
    # endpoint. The text_midpoint (11,21,31) specifies the midpoint of the dimension text. Defpoint (10,20,30) is placed
    # at the origin of the UCS that is current when the dimension is created.
})


_DIMTXSTY = 'dimtxsty'

_DIMENSION_TPL = """  0
DIMENSION
5
0
102
{ACAD_REACTORS
330
0
102
}
330
DEAD
100
AcDbEntity
8
0
100
AcDbDimension
2
*D0
10
0.0
20
0.0
30
0.0
70
32
71
5
42
0.0
3
STANDARD
"""

_ALIGNED_TPL = """100
AcDbAlignedDimension
 13
0.0
 23
0.0
 33
0.0
 14
0.0
 24
0.0
 34
0.0
"""

_ROTATED_TPL = """100
AcDbRotatedDimension
"""

_RADIAL_TPL = """100
AcDbRadialDimension
"""

_DIAMETRIC_TPL = """100
AcDbDiametricDimension
"""

_ANGULAR_TPL = """100
AcDb3dPointAngularDimension
"""

_ORDINATE_TPL = """100
AcDbOrdinateDimension
"""


class Dimension(dimension.Dimension, ModernGraphicEntity):
    __slots__ = ()
    BLOCK_EXCLUSIVE = 32
    TEMPLATE = ExtendedTags.from_text(_DIMENSION_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, dimension_subclass)

    def post_new_hook(self) -> None:
        self.add_subclasses()

    def add_subclasses(self) -> None:
        def add_subclasses(templates) -> None:
            for template in templates:
                self.tags.subclasses.append(Tags.from_text(template))
        dim_type = self.dim_type
        if dim_type == self.LINEAR:
            add_subclasses([_ALIGNED_TPL, _ROTATED_TPL])
        elif dim_type == self.ALIGNED:
            add_subclasses([_ALIGNED_TPL])
        elif dim_type in (self.ANGULAR, self.ANGULAR_3P):
            add_subclasses([_ANGULAR_TPL])
        elif dim_type == self.RADIUS:
            add_subclasses([_RADIAL_TPL])
        elif dim_type == self.DIAMETER:
            add_subclasses([_DIAMETRIC_TPL])
        elif dim_type == self.ORDINATE:
            add_subclasses([_ORDINATE_TPL])

    def cast(self) -> 'Dimension':  # create the REAL dimension entity
        DimClass = DimensionClasses[self.dim_type]
        return DimClass(self.tags, self.drawing)

    def set_acad_dstyle(self, data: dict, dim_style) -> None:
        if self.drawing is None:
            raise DXFInternalEzdxfError('Dimension.drawing attribute not initialized.')
        # replace virtual 'dimtxsty' attribute by 'dimtxsty_handle'
        if _DIMTXSTY in data:
            dimtxsty = data[_DIMTXSTY]
            txtstyle = self.drawing.styles.get(dimtxsty)
            data['dimtxsty_handle'] = txtstyle.dxf.handle
            del data[_DIMTXSTY]
        super().set_acad_dstyle(data, dim_style)


class AlignedDimension(Dimension):
    __slots__ = ()
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, dimension_subclass, aligned_dimension_subclass)


class RotatedDimension(Dimension):
    __slots__ = ()
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, dimension_subclass, aligned_dimension_subclass,
                               rotated_dimension_subclass)


class RadialDimension(Dimension):
    __slots__ = ()
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, dimension_subclass, radial_dimension_subclass)


class DiametricDimension(Dimension):
    __slots__ = ()
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, dimension_subclass, diametric_dimension_subclass)


class AngularDimension(Dimension):
    __slots__ = ()
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, dimension_subclass, angular_dimension_subclass)


class OrdinateDimension(Dimension):
    __slots__ = ()
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, dimension_subclass, ordinate_dimension_subclass)


DimensionClasses = [
    RotatedDimension,  # 0
    AlignedDimension,  # 1
    AngularDimension,  # 2
    DiametricDimension,  # 3
    RadialDimension,  # 4
    AngularDimension,  # 5
    OrdinateDimension,  # 6
]
