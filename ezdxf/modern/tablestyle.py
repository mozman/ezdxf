# Created: 10.04.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals
from .dxfobjects import DXFObject, DefSubclass, DXFAttributes, DXFAttr, none_subclass, ExtendedTags
from .object_manager import ObjectManager

_TABLESTYLE_CLS = """0
CLASS
1
TABLESTYLE
2
AcDbTableStyle
3
ObjectDBX Classes
90
4095
91
0
280
0
281
0
"""

_TABLESTYLE_TPL = """0
TABLESTYLE
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
AcDbTableStyle
280
0
3
Standard
70
0
71
0
40
1.5
41
1.5
280
0
281
0
"""


tablestyle_subclass = DefSubclass('AcDbTableStyle', {
    'version': DXFAttr(280),  # 0 = 2010
    'name': DXFAttr(3),  # Table style description (string; 255 characters maximum)
    'flow_direction': DXFAttr(7),  # FlowDirection (integer):
    # 0 = Down
    # 1 = Up
    'flags': DXFAttr(7),  # Flags (bit-coded)
    'horizontal_cell_margin': DXFAttr(40),  # Horizontal cell margin (real; default = 0.06)
    'vertical_cell_margin': DXFAttr(41),  # Vertical cell margin (real; default = 0.06)
    'suppress_title': DXFAttr(280),  # Flag for whether the title is suppressed: 0/1 = not suppressed/suppressed
    'suppress_column_header': DXFAttr(281),  # Flag for whether the column heading is suppressed: 0/1 = not suppressed/suppressed
    # The following group codes are repeated for every cell in the table
    #   7: Text style name (string; default = STANDARD)
    # 140: Text height (real)
    # 170: Cell alignment (integer)
    #  62: Text color (integer; default = BYBLOCK)
    #  63: Cell fill color (integer; default = 7)
    # 283: Flag for whether background color is enabled (default = 0): 0/1 = disabled/enabled
    #  90: Cell data type
    #  91: Cell unit type
    # 274-279: Lineweight associated with each border type of the cell (default = kLnWtByBlock)
    # 284-289: Flag for visibility associated with each border type of the cell (default = 1): 0/1 = Invisible/Visible
    # 64-69: Color value associated with each border type of the cell (default = BYBLOCK)
})


class TableStyle(DXFObject):
    """
    Every ACAD_TABLE has its own table style.

    Requires DXF version AC1021/R2007
    """
    TEMPLATE = ExtendedTags.from_text(_TABLESTYLE_TPL)
    CLASS = ExtendedTags.from_text(_TABLESTYLE_CLS)
    DXFATTRIBS = DXFAttributes(none_subclass, tablestyle_subclass)


class TableStyleManager(ObjectManager):
    def __init__(self, drawing):
        super(TableStyleManager, self).__init__(drawing, dict_name='ACAD_TABLESTYLE', object_type='TABLESTYLE')
