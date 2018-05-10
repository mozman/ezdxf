# Created: 08.04.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals
from .graphics import ExtendedTags, DXFAttr, DefSubclass, DXFAttributes
from .graphics import none_subclass, entity_subclass, ModernGraphicEntity
from .image import image_subclass
from .dxfobjects import DXFObject

_WIPEOUT_CLS = """0
CLASS
1
WIPEOUT
2
AcDbWipeout
3
WipeOut|Product Desc: Object Enabler for WipeOut entity | Company: Autodesk, Inc. | WEB Address: www.autodesk.com
90
2175
91
1
280
0
281
1
"""

_WIPEOUT_TPL = """0
WIPEOUT
5
0
330
0
100
AcDbEntity
8
0
100
AcDbWipeout
90
0
10
0.0
20
0.0
30
0.0
11
0.0
21
0.0
31
0.0
12
0.0
22
0.0
32
0.0
13
1.0
23
1.0
340
0
70
7
280
1
281
50
282
50
283
0
360
0
71
1
92
2
"""

wipeout_subclass = image_subclass._replace(name='AcDbWipeout')


class Wipeout(ModernGraphicEntity):
    # Requires AC1021/R2007
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_WIPEOUT_TPL)
    CLASS = ExtendedTags.from_text(_WIPEOUT_CLS)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, wipeout_subclass)

    def destroy(self):
        return


_WIPEOUT_VARIABLES_CLS = """0
CLASS
1
WIPEOUTVARIABLES
2
AcDbWipeoutVariables
3
"WipeOut|Product Desc:     WipeOut Dbx Application|Company:          Autodesk, Inc.|WEB Address:      www.autodesk.com"
90
0
91
1
280
0
281
0
"""

_WIPEOUT_VARIABLES_TPL = """0
WIPEOUTVARIABLES
5
0
102
{ACAD_REACTORS
102
}
330
0
100
AcDbWipeoutVariables
70
0
"""


class WipeoutVariables(DXFObject):
    TEMPLATE = ExtendedTags.from_text(_WIPEOUT_VARIABLES_TPL)
    CLASS = ExtendedTags.from_text(_WIPEOUT_VARIABLES_CLS)
    DXFATTRIBS = DXFAttributes(
        none_subclass,
        DefSubclass('AcDbWipeoutVariables', {
            'frame': DXFAttr(70, default=0),  # Display-image-frame flag: 0 = No frame; 1 = Display frame
        }),
    )
