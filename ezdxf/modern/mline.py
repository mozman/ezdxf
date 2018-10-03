# Created: 08.04.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals

from ezdxf.lldxf.const import DXFIndexError

from .graphics import ExtendedTags, DXFAttr, DefSubclass, DXFAttributes
from .graphics import none_subclass, entity_subclass, ModernGraphicEntity
from .dxfobjects import DXFObject
from .object_manager import ObjectManager

# example: processing: D:\source\dxftest\CADKitSamples\Lock-Off.dxf


_MLINE_TPL = """0
MLINE
5
0
330
0
100
AcDbEntity
8
0
100
AcDbMline
2
STANDARD
340
0
40
1.0
70
0
71
1
72
1
73
1
10
0.0
20
0.0
30
0.0
210
0.0
220
0.0
230
1.0
"""

mline_subclass = DefSubclass('AcDbMline', {
    'mline_style': DXFAttr(2),
    'mline_style_id': DXFAttr(340),
    'scale_factor': DXFAttr(40, default=1),
    'justification': DXFAttr(70),  # 0 = Top; 1 = Zero; 2 = Bottom
    'flags': DXFAttr(71),  # Flags (bit-coded values):
    # 1 = Has at least one vertex (code 72 is greater than 0)
    # 2 = Closed
    # 4 = Suppress start caps
    # 8 = Suppress end caps
    'n_vertices': DXFAttr(72),  # Number of vertices
    'n_style_elements': DXFAttr(73),  # Number of elements in MLINESTYLE definition
    'start_point': DXFAttr(10, xtype='Point3D'),  # in WCS!
    'extrusion': DXFAttr(210, xtype='Point3D'),  # but all vertices in WCS!
    # 11: vertex coordinates (multiple entries; one entry for each vertex)
    # 12: Direction vector of segment starting at this vertex (multiple entries; one for each vertex)
    # 13: Direction vector of miter at this vertex (multiple entries: one for each vertex)
    # 73: Number of parameters for this element (repeats for each element in segment)
    # 41: Element parameters (repeats based on previous code 74)
    # 75: Number of area fill parameters for this element (repeats for each element in segment)
    # 42: Area fill parameters (repeats based on previous code 75)
})

# The group code 41 parameterization is a list of real values, one real per group code 41. The list may contain zero or
# more items. The first group code 41 value is the distance from the segment vertex along the miter vector to the point
# where the line element's path intersects the miter vector. The next group code 41 value is the distance along the line
# element's path from the point defined by the first group 41 to the actual start of the line element. The next is the
# distance from the start of the line element to the first break (or cut) in the line element. The successive group
# code 41 values continue to list the start and stop points of the line element in this segment of the mline. Linetypes
# do not affect group 41 lists.
#
# The group code 42 parameterization is also a list of real values. Similar to the 41 parameterization, it describes the
# parameterization of the fill area for this mline segment. The values are interpreted identically to the 41 parameters
# and when taken as a whole for all line elements in the mline segment, they define the boundary of the fill area for
# the mline segment.
#
# A common example of the use of the group code 42 mechanism is when an unfilled mline crosses over a filled mline and
# mledit is used to cause the filled mline to appear unfilled in the crossing area. This would result in two group 42s
# for each line element in the affected mline segment; one for the fill stop and one for the fill start.
#
# The 2 group codes in mline entities and mlinestyle objects are redundant fields. These groups should not be modified
# under any circumstances, although it is safe to read them and use their values. The correct fields to modify are as
# follows:
#
# Mline
# The 340 group in the same object, which indicates the proper MLINESTYLE object.
#
# Mlinestyle
# The 3 group value in the MLINESTYLE dictionary, which precedes the 350 group that has the handle or entity name of
# the current mlinestyle.


class MLine(ModernGraphicEntity):
    # Requires AC1021/R2007
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_MLINE_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, mline_subclass)

    def get_points(self):
        return []


_MLINE_STYLE_TPL = """0
MLINESTYLE
5
0
102
{ACAD_REACTORS
102
}
330
0
100
AcDbMlineStyle
2
STANDARD
70
0
3

62
256
51
90.0
52
90.0
71
2
49
0.5
62
256
6
BYLAYER
49
-0.5
62
256
6
BYLAYER
"""

mline_style_subclass = DefSubclass('AcDbMlineStyle', {
    'name': DXFAttr(2),
    'flags': DXFAttr(70),  # Flags (bit-coded):
    # 1 =Fill on
    # 2 = Display miters
    # 16 = Start square end (line) cap
    # 32 = Start inner arcs cap
    # 64 = Start round (outer arcs) cap
    # 256 = End square (line) cap
    # 512 = End inner arcs cap
    # 1024 = End round (outer arcs) cap
    'description': DXFAttr(3),  # Style description (string, 255 characters maximum)
    'fill_color': DXFAttr(62),  # Fill color (integer, default = 256)
    'start_angle': DXFAttr(51),  # Start angle (real, default is 90 degrees)
    'end_angle': DXFAttr(52),  # End angle (real, default is 90 degrees)
    'n_elements': DXFAttr(71),  # Number of elements
    # 49: Element offset (real, no default). Multiple entries can exist; one entry for each element
    # 62: Element color (integer, default = 0). Multiple entries can exist; one entry for each element
    # 6: Element linetype (string, default = BYLAYER). Multiple entries can exist; one entry for each element
})


class MLineStyle(DXFObject):
    # Requires AC1021/R2007
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_MLINE_STYLE_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, mline_style_subclass)

    @property
    def AcDbMLineStyle(self):
        return self.tags.subclasses[1]

    def get_elements(self):
        tags = self.AcDbMLineStyle
        try:
            start = tags.tag_index(71)
        except DXFIndexError:
            return
        else:
            collector = None
            for code, value in tags[start+1:]:
                if code == 49:
                    if collector is not None:
                        yield collector
                    collector = {'offset': value}
                elif code == 62:
                    collector['color'] = value
                elif code == 6:
                    collector['linetype'] = value
            if collector is not None:
                yield collector


class MLineStyleManager(ObjectManager):
    def __init__(self, drawing):
        super(MLineStyleManager, self).__init__(drawing, dict_name='ACAD_MLINESTYLE', object_type='MLINESTYLE')
        self.create_required_entries()

    def create_required_entries(self):
        for name in ('STANDARD', ):
            if name not in self.object_dict:
                self.new(name)
