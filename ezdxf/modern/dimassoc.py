# Created: 15.04.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals
from .dxfobjects import DXFObject, DefSubclass, DXFAttributes, DXFAttr, none_subclass, ExtendedTags
# Autodesk gone crazy: subclass AcDbOsnapPointRef with group code 1!!!!!


_DIMASSOC_CLS = """0
CLASS
1
DIMASSOC
2
AcDbDimAssoc
3
"AcDbDimAssoc|Product Desc:     AcDim ARX App For Dimension|Company:          Autodesk, Inc.|WEB Address:      www.autodesk.com"
90
0
91
4
280
0
281
0
"""

_DIMASSOC_TPL = """0
DIMASSOC
5
0
102
{ACAD_REACTORS
330
0
102
}
330
0
100
AcDbDimAssoc
330
0
90
1
70
0
71
0
1
AcDbOsnapPointRef
72
0
331
0
73
0
91
0
40
0.0
10
0.0
20
0.0
30
0.0
75
0
"""


class DimAssoc(DXFObject):
    # requires AC1015/R2000
    # DIMASSOC objects implement associative dimensions by specifying an association between a dimension object and
    # drawing geometry objects. An associative dimension is a dimension that will automatically update when the
    # associated geometry is modified.
    TEMPLATE = ExtendedTags.from_text(_DIMASSOC_TPL)
    CLASS = ExtendedTags.from_text(_DIMASSOC_CLS)
    DXFATTRIBS = DXFAttributes(none_subclass, DefSubclass('AcDbDimAssoc', {
        'dimension': DXFAttr(330),  # handle of dimension object
        'point_flag': DXFAttr(90),  # Associativity flag (bit-coded)
        # 1 = First point reference
        # 2 = Second point reference
        # 4 = Third point reference
        # 8 = Fourth point reference
        'trans_space': DXFAttr(70),  # Trans-space flag (true/false)
        'rotated_dim_type': DXFAttr(71),  # Rotated Dimension type (parallel, perpendicular)
        # Autodesk gone crazy: subclass AcDbOsnapPointRef with group code 1!!!!!
        #  }), DefSubclass('AcDbOsnapPointRef', {
        'osnap_type': DXFAttr(72),  # Object Osnap type
        # 0 = None
        # 1 = Endpoint
        # 2 = Midpoint
        # 3 = Center
        # 4 = Node
        # 5 = Quadrant
        # 6 = Intersection
        # 7 = Insertion
        # 8 = Perpendicular
        # 9 = Tangent
        # 10 = Nearest
        # 11 = Apparent intersection
        # 12 = Parallel
        # 13 = Start point
        'object_id': DXFAttr(331),  # ID of main object (geometry)
        'object_subtype': DXFAttr(73),  # SubentType of main object (edge, face)
        'object_gs_marker': DXFAttr(91),  # GsMarker of main object (index)
        'object_xref_id': DXFAttr(301),  # Handle (string) of Xref object
        'near_param': DXFAttr(40),  # Geometry parameter for Near Osnap
        'osnap_point': DXFAttr(10, xtype='Point3D'),  # Osnap point in WCS
        'intersect_id': DXFAttr(332),  # ID of intersection object (geometry)
        'intersect_subtype': DXFAttr(74),  # SubentType of intersection object (edge/face)
        'intersect_gs_marker': DXFAttr(92),  # GsMarker of intersection object (index)
        'intersect_xref_id': DXFAttr(302),  # Handle (string) of intersection Xref object
        'has_last_point_ref': DXFAttr(75),  # hasLastPointRef flag (true/false)
    }))
