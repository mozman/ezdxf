# Created: 08.04.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals
from .dxfobjects import ExtendedTags, DXFAttr, DefSubclass, DXFAttributes
from .dxfobjects import none_subclass, DXFObject
_SUN_CLS = """0
CLASS
1
SUN
2
AcDbSun
3
SCENEOE
90
1153
91
0
280
0
281
0
"""

_SUN_TPL = """0
SUN
5
0
330
0
100
AcDbSun
90
1
290
1
63
7
421
16777215
40
1.0
291
1
91
2456922
92
43200
292
0
70
0
71
256
280
1
"""

sun_subclass = DefSubclass('AcDbSun', {
    'version': DXFAttr(90),
    'status': DXFAttr(290),
    'color': DXFAttr(63),
    'true_color': DXFAttr(421),
    'intensity': DXFAttr(40),
    'shadows': DXFAttr(291),
    'julian_day': DXFAttr(91),
    'time': DXFAttr(92),  # Time (in seconds past midnight)
    'daylight_savings_time': DXFAttr(292),
    'shadow_type': DXFAttr(70),  # Shadow type 0 = Ray traced shadows; 1 = Shadow maps
    'shadow_map_size': DXFAttr(71),
    'shadow_softness': DXFAttr(280),
})


class Sun(DXFObject):
    # Requires AC1021/R2007
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_SUN_TPL)
    CLASS = ExtendedTags.from_text(_SUN_CLS)
    DXFATTRIBS = DXFAttributes(none_subclass, sun_subclass)


