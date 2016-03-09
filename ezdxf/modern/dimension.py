# Purpose: support for the Ac1015 DIMENSION entity
# Created: 09.03.2016
# Copyright (C) 2016, Manfred Moitzi
# License: MIT License

from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .graphics import none_subclass, entity_subclass, ModernGraphicEntity
from ..lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ..lldxf import const


dimension_subclass = DefSubclass('AcDbDimension', {
    'geometry': DXFAttr(2),  # name of pseudo-Block containing the current dimension  entity geometry
    'defpoint': DXFAttr(10, xtype='Point3D', default=(0.0, 0.0, 0.0)),
    'text_midpoint': DXFAttr(11, xtype='Point2D/3D'),
    'dimtype': DXFAttr(70),  # Dimension type:
    # Values 0–6 are integer values that represent the dimension type. Values
    # 32, 64, and 128 are bit values, which are added to the integer values
    # (value 32 is always set in R13 and later releases)
    # 0 = Rotated, horizontal, or vertical; 1 = Aligned
    # 2 = Angular; 3 = Diameter; 4 = Radius
    # 5 = Angular 3 point; 6 = Ordinate
    # 32 = Indicates that the block reference (group code 2) is referenced by
    # this dimension only
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
    'user_text': DXFAttr(1),  # Dimension text explicitly entered by the user. Optional; default is the
    # measurement. If null or “<>”, the dimension measurement is drawn as
    # the text, if “ “ (one blank space), the text is suppressed. Anything else is
    # drawn as the text
    'dim_text_rotation': DXFAttr(53, default=0),  # The optional group code 53 is the rotation angle of the dimension
    # text away from its default orientation (the direction of the dimension line) (optional)
    'horizontal_direction': DXFAttr(51, default=0),  # All dimension types have an optional 51 group code, which
    # indicates the horizontal direction for the dimension entity. The dimension entity determines the orientation of
    # dimension text and lines for horizontal, vertical, and rotated linear dimensions. This group value is the negative
    # of the angle between the OCS X axis and the UCS X axis. It is always in the XY plane of the OCS
    'extrusion': DXFAttr(210, xtype='Point3D', default=(0.0, 0.0, 1.0)),
})

aligned_dimension_subclass = DefSubclass('AcDbAlignedDimension', {
    'insert': DXFAttr(12, xtype='Point3D', default=(0.0, 0.0, 0.0)),  # Insertion point for clones of a
    # dimension—Baseline and Continue (in OCS)
    'defpoint2': DXFAttr(13, xtype='Point3D', default=(0.0, 0.0, 0.0)),  # Definition point for linear and angular dimensions (in WCS)
    'defpoint3': DXFAttr(14, xtype='Point3D', default=(0.0, 0.0, 0.0)),  # Definition point for linear and angular dimensions (in WCS)
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
    'defpoint4': DXFAttr(15, xtype='Point3D', default=(0.0, 0.0, 0.0)),  # Definition point for diameter, radius, and angular dimensions (in WCS)
    'leader_length': DXFAttr(40),  # Leader length for radius and diameter dimensions
}

radial_dimension_subclass = DefSubclass('AcDbRadialDimension', radial_diametric_attribs)

diametric_dimension_subclass = DefSubclass('AcDbDiametricDimension', radial_diametric_attribs)

angular_dimension_subclass = DefSubclass('AcDb3dPointAngularDimension', {
    'defpoint2': DXFAttr(13, xtype='Point3D', default=(0.0, 0.0, 0.0)),  # Definition point for linear and angular dimensions (in WCS)
    'defpoint3': DXFAttr(14, xtype='Point3D', default=(0.0, 0.0, 0.0)),  # Definition point for linear and angular dimensions (in WCS)
    'defpoint4': DXFAttr(15, xtype='Point3D', default=(0.0, 0.0, 0.0)),  # Definition point for diameter, radius, and angular dimensions (in WCS)
    'defpoint5': DXFAttr(16, xtype='Point3D', default=(0.0, 0.0, 0.0)),  # Point defining dimension arc for angular dimensions (in OCS)
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
    'defpoint2': DXFAttr(13, xtype='Point3D', default=(0.0, 0.0, 0.0)),  # Definition point for linear and angular dimensions (in WCS)
    'defpoint3': DXFAttr(14, xtype='Point3D', default=(0.0, 0.0, 0.0)),  # Definition point for linear and angular dimensions (in WCS)
    # The defpoint1 (13,23,33) specifies the feature location and the defpoint2 (14,24,34) specifies the leader
    # endpoint. The text_midpoint (11,21,31) specifies the midpoint of the dimension text. Defpoint (10,20,30) is placed
    # at the origin of the UCS that is current when the dimension is created.
})


# bootstrap dimension entity
class Dimension(ModernGraphicEntity):
    def cast(self):  # create the REAL dimension entity
        subclasses = self.tags.subclasses
        dimtype = subclasses[3][0].value
        if dimtype == 'AcDbAlignedDimension' and len(subclasses) > 4:
            dimtype = 'AcDbRotatedDimension'
        try:
            DimClass = DimensionClasses[dimtype]
        except KeyError:
            raise const.DXFInternalEzdxfError("Unknown dimension type: '{}', "
                                              "send a message to mozman@gmx.at".format(dimtype))
        return DimClass(self.tags, self.drawing, dimtype)


class AbstractDimension(ModernGraphicEntity):
    def __init__(self, tags, drawing, dimtype):
        super(self, AbstractDimension).__init__(tags, drawing)
        self._dimtype = dimtype

    @property
    def dimtype(self):
        return self._dimtype


class AlignedDimension(AbstractDimension):
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, dimension_subclass, aligned_dimension_subclass)


class RotatedDimension(AbstractDimension):
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, dimension_subclass, aligned_dimension_subclass,
                               rotated_dimension_subclass)


class RadialDimension(AbstractDimension):
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, dimension_subclass, radial_dimension_subclass)


class DiametricDimension(AbstractDimension):
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, dimension_subclass, diametric_dimension_subclass)


class AngularDimension(AbstractDimension):
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, dimension_subclass, angular_dimension_subclass)


class OrdinateDimension(AbstractDimension):
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, dimension_subclass, ordinate_dimension_subclass)


DimensionClasses = {
    'AcDbAlignedDimension': AlignedDimension,
    'AcDbRotatedDimension': RotatedDimension,
    'AcDbRadialDimension': RadialDimension,
    'AcDbDiametricDimension': DiametricDimension,
    'AcDb3dPointAngularDimension': AngularDimension,
    'AcDbOrdinateDimension': OrdinateDimension,
}
