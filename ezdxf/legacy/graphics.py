# Created: 25.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.dxfentity import DXFEntity


def make_attribs(additional: dict = None):
    dxfattribs = {
        'handle': DXFAttr(5),
        'layer': DXFAttr(8, default='0'),  # layer name as string, mandatory according to the DXF Reference
        'linetype': DXFAttr(6, default='BYLAYER'),  # linetype as string, special names BYLAYER/BYBLOCK
        'color': DXFAttr(62, default=256),  # dxf color index, 0 .. BYBLOCK, 256 .. BYLAYER
        'thickness': DXFAttr(39, default=0),  # thickness of 2D elements
        'paperspace': DXFAttr(67, default=0),  # 0=modelspace; 1=paperspace
        'extrusion': DXFAttr(210, xtype=XType.point3d, default=(0.0, 0.0, 1.0)),
    # Z-axis of OCS (Object-Coordinate-System)
    }
    if additional is not None:
        dxfattribs.update(additional)
    return DXFAttributes(DefSubclass(None, dxfattribs))


class GraphicEntity(DXFEntity):
    __slots__ = ()
    """ Default graphic entity wrapper, allows access to following dxf attributes:

     - handle
     - layer
     - linetype
     - color
     - paperspace
     - extrusion

     Wrapper for all unsupported graphic entities.
    """
    DXFATTRIBS = make_attribs()

    def audit(self, auditor):
        auditor.check_for_valid_layer_name(self)
        auditor.check_if_linetype_exists(self)
        auditor.check_for_valid_color_index(self)


_LINE_TPL = """0
LINE
5
0
8
0
10
0.0
20
0.0
30
0.0
11
1.0
21
1.0
31
1.0
"""


class Line(GraphicEntity):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_LINE_TPL)
    DXFATTRIBS = make_attribs({
        'start': DXFAttr(10, xtype=XType.any_point),
        'end': DXFAttr(11, xtype=XType.any_point),
    })


_POINT_TPL = """0
POINT
5
0
8
0
10
0.0
20
0.0
30
0.0
"""


class Point(GraphicEntity):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_POINT_TPL)
    DXFATTRIBS = make_attribs({
        'location': DXFAttr(10, xtype=XType.any_point),
    })


_CIRCLE_TPL = """0
CIRCLE
5
0
8
0
10
0.0
20
0.0
30
0.0
40
1.0
"""


class Circle(GraphicEntity):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_CIRCLE_TPL)
    DXFATTRIBS = make_attribs({
        'center': DXFAttr(10, xtype=XType.any_point),
        'radius': DXFAttr(40),
    })


_ARC_TPL = """0
ARC
5
0
8
0
10
0.0
20
0.0
30
0.0
40
1.0
50
0
51
360
"""


class Arc(GraphicEntity):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_ARC_TPL)
    DXFATTRIBS = make_attribs({
        'center': DXFAttr(10, xtype=XType.any_point),
        'radius': DXFAttr(40),
        'start_angle': DXFAttr(50),
        'end_angle': DXFAttr(51),
    })


class SeqEnd(GraphicEntity):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text("  0\nSEQEND\n  5\n0\n")
    DXFATTRIBS = DXFAttributes(DefSubclass(None, {
        'handle': DXFAttr(5),
        'paperspace': DXFAttr(67, default=0),
    }))


_SHAPE_TPL = """0
SHAPE
5
0
8
0
10
0.0
20
0.0
30
0.0
40
1.0
2
NAME
50
0.0
41
1.0
51
0.0
"""


# SHAPE is not tested with real world DXF drawings!
class Shape(GraphicEntity):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_SHAPE_TPL)
    DXFATTRIBS = make_attribs({
        'insert': DXFAttr(10, xtype=XType.any_point),
        'size': DXFAttr(40),
        'name': DXFAttr(2),
        'rotation': DXFAttr(50, default=0.0),
        'xscale': DXFAttr(41, default=1.0),
        'oblique': DXFAttr(51, default=0.0),
    })
