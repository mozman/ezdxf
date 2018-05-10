# Created: 09.04.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals
from .graphics import ExtendedTags, DXFAttr, DefSubclass, DXFAttributes
from .graphics import none_subclass, entity_subclass, ModernGraphicEntity

_ACAD_TABLE_CLS = """0
CLASS
1
ACAD_TABLE
2
AcDbTable
3
ObjectDBX Classes
90
1025
91
0
280
0
281
1
"""

_ACAD_TABLE_TPL = """  0
ACAD_TABLE
5
0
330
0
100
AcDbEntity
8
0
100
AcDbBlockReference
2
*T1
10
0.0
20
0.0
30
0.0
100
AcDbTable
280
0
342
0
343
0
11
1.0
21
0.0
31
0.0
90
22
91
4
92
5
93
0
94
0
95
0
96
0
"""

block_reference_subclass = DefSubclass('AcDbBlockReference', {
    'block_name': DXFAttr(2),  # Block name; an anonymous block begins with a *T value
    'insert': DXFAttr(10, xtype='Point3D'),  # Insertion point
})

table_subclass = DefSubclass('AcDbTable', {
    'version': DXFAttr(280),  # Table data version number: 0 = 2010
    'table_style_id': DXFAttr(342),  # Hard pointer ID of the TABLESTYLE object
    'block_record': DXFAttr(343),  # Hard pointer ID of the owning BLOCK record
    'horizontal_direction': DXFAttr(11),  # Horizontal direction vector
    'table_value': DXFAttr(90),  # Flag for table value (unsigned integer)
    'n_rows': DXFAttr(91),  # Number of rows
    'n_cols': DXFAttr(92),  # Number of columns
    'override_flag': DXFAttr(93),  # Flag for an override
    'border_color_override_flag': DXFAttr(94),  # Flag for an override of border color
    'border_lineweight_override_flag': DXFAttr(95),  # Flag for an override of border lineweight
    'border_visibility_override_flag': DXFAttr(96),  # Flag for an override of border visibility
    # 141: Row height; this value is repeated, 1 value per row
    # 142: Column height; this value is repeated, 1 value per column
    # for every cell:
    #      171: Cell type; this value is repeated, 1 value per cell:
    #           1 = text type
    #           2 = block type
    #      172: Cell flag value; this value is repeated, 1 value per cell
    #      173: Cell merged value; this value is repeated, 1 value per cell
    #      174: Boolean flag indicating if the autofit option is set for the cell; this value is repeated, 1 value per cell
    #      175: Cell border width (applicable only for merged cells); this value is repeated, 1 value per cell
    #      176: Cell border height (applicable for merged cells); this value is repeated, 1 value per cell
    #       91: Cell override flag; this value is repeated, 1 value per cell (from AutoCAD 2007)
    #      178: Flag value for a virtual edge
    #      145: Rotation value (real; applicable for a block-type cell and a text-type cell)
    #      344: Hard pointer ID of the FIELD object. This applies only to a text-type cell. If the text in the cell
    #           contains one or more fields, only the ID of the FIELD object is saved. The text string
    #           (group codes 1 and 3) is ignored
    #        1: Text string in a cell. If the string is shorter than 250 characters, all characters appear in code 1.
    #           If the string is longer than 250 characters, it is divided into chunks of 250 characters. The chunks are
    #           contained in one or more code 2 codes. If code 2 codes are used, the last group is a code 1 and is
    #           shorter than 250 characters. This value applies only to text-type cells and is repeated, 1 value per cell
    #        2: Text string in a cell, in 250-character chunks; optional. This value applies only to text-type cells and
    #           is repeated, 1 value per cell
    #      340: Hard-pointer ID of the block table record. This value applies only to block-type cells and is repeated,
    #           1 value per cell
    #      144: Block scale (real). This value applies only to block-type cells and is repeated, 1 value per cell
    #      176: Number of attribute definitions in the block table record (applicable only to a block-type cell)
    #      for every ATTDEF:
    #           331: Soft pointer ID of the attribute definition in the block table record, referenced by group code 179
    #                (applicable only for a block-type cell). This value is repeated once per attribute definition
    #           300: Text string value for an attribute definition, repeated once per attribute definition and applicable
    #                only for a block-type cell
    #        7: Text style name (string); override applied at the cell level
    #      140: Text height value; override applied at the cell level
    #      170: Cell alignment value; override applied at the cell level
    #       64: Value for the color of cell content; override applied at the cell level
    #       63: Value for the background (fill) color of cell content; override applied at the cell level
    #       69: True color value for the top border of the cell; override applied at the cell level
    #       65: True color value for the right border of the cell; override applied at the cell level
    #       66: True color value for the bottom border of the cell; override applied at the cell level
    #       68: True color value for the left border of the cell; override applied at the cell level
    #      279: Lineweight for the top border of the cell; override applied at the cell level
    #      275: Lineweight for the right border of the cell; override applied at the cell level
    #      276: Lineweight for the bottom border of the cell; override applied at the cell level
    #      278: Lineweight for the left border of the cell; override applied at the cell level
    #      283: Boolean flag for whether the fill color is on; override applied at the cell level
    #      289: Boolean flag for the visibility of the top border of the cell; override applied at the cell level
    #      285: Boolean flag for the visibility of the right border of the cell; override applied at the cell level
    #      286: Boolean flag for the visibility of the bottom border of the cell; override applied at the cell level
    #      288: Boolean flag for the visibility of the left border of the cell; override applied at the cell level
    #       70: Flow direction; override applied at the table entity level
    #       40: Horizontal cell margin; override applied at the table entity level
    #       41: Vertical cell margin; override applied at the table entity level
    #      280: Flag for whether the title is suppressed; override applied at the table entity level
    #      281: Flag for whether the header row is suppressed; override applied at the table entity level
    #        7: Text style name (string); override applied at the table entity level. There may be one entry for each cell type
    #      140: Text height (real); override applied at the table entity level. There may be one entry for each cell type
    #      170: Cell alignment (integer); override applied at the table entity level. There may be one entry for each cell type
    #       63: Color value for cell background or for the vertical, left border of the table; override applied at the
    #           table entity level. There may be one entry for each cell type
    #       64: Color value for cell content or for the horizontal, top border of the table; override applied at the
    #           table entity level. There may be one entry for each cell type
    #       65: Color value for the horizontal, inside border lines; override applied at the table entity level
    #       66: Color value for the horizontal, bottom border lines; override applied at the table entity level
    #       68: Color value for the vertical, inside border lines; override applied at the table entity level
    #       69: Color value for the vertical, right border lines; override applied at the table entity level
    #      283: Flag for whether background color is enabled (default = 0); override applied at the table entity level.
    #           There may be one entry for each cell type: 0/1 = Disabled/Enabled
    #      274-279: Lineweight for each border type of the cell (default = kLnWtByBlock); override applied at the table
    #               entity level. There may be one group for each cell type
    #      284-289: Flag for visibility of each border type of the cell (default = 1); override applied at the table
    #               entity level. There may be one group for each cell type: 0/1 = Invisible/Visible
    #  97: Standard/title/header row data type
    #  98: Standard/title/header row unit type
    #   4: Standard/title/header row format string
    #
    # AutoCAD 2007 and before:
    # 177: Cell override flag value (before AutoCAD 2007)
    #  92: Extended cell flags (from AutoCAD 2007), COLLISION: group code also used by n_cols
    # 301: Text string in a cell. If the string is shorter than 250 characters, all characters appear in code 302. If
    #      the string is longer than 250 characters, it is divided into chunks of 250 characters. The chunks are
    #      contained in one or more code 303 codes. If code 393 codes are used, the last group is a code 1 and is
    #      shorter than 250 characters. This value applies only to text-type cells and is repeated,
    #      1 value per cell (from AutoCAD 2007)
    # 302: Text string in a cell, in 250-character chunks; optional. This value applies only to text-type cells and is
    #      repeated, 302 value per cell (from AutoCAD 2007)
    #
    # REMARK from Autodesk:
    # Group code 178 is a flag value for a virtual edge. A virtual edge is used when a grid line is shared by two cells.
    # For example, if a table contains one row and two columns and it contains cell A and cell B, the central grid line
    # contains the right edge of cell A and the left edge of cell B. One edge is real, and the other edge is virtual.
    # The virtual edge points to the real edge; both edges have the same set of properties, including color, lineweight,
    # and visibility.
})


class ACADTable(ModernGraphicEntity):
    __slots__ = ()
    # Requires AC1024/R2010
    TEMPLATE = ExtendedTags.from_text(_ACAD_TABLE_TPL)
    CLASS = ExtendedTags.from_text(_ACAD_TABLE_CLS)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, block_reference_subclass, table_subclass)

    @property
    def AcDbTable(self):
        return self.tags.subclasses[3]
