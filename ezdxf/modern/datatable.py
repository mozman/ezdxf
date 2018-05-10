# Created: 08.04.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals
from .dxfobjects import DXFObject, DefSubclass, DXFAttributes, DXFAttr, none_subclass, ExtendedTags


_DATATABLE_CLS = """0
CLASS
1
DATATABLE
2
AcDbDataTable
3
ObjectDBX Classes
90
0
91
0
280
0
281
0
"""

_DATATABLE_TPL = """0
DATATABLE
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
AcDbDataTable
70
2
90
1
91
1
1
TableName
92
1
2
Column1
93
0
"""


class DataTable(DXFObject):
    """
    Data storage (non-graphical entity), organized as column, rows table.

    Requires DXF version AC1021/R2007

    each column start with
    93              >>> start first column
    column type
    2
    column name
    column type     >>> first row of first column
    value
    ...             >>> rows-times
    ...
    93
    column type     >>> second column
    2
    column name
    column type     >>> first row of second column
    value
    ...             >>> rows-times
    ...

    column types:
    -------------

    undocumented, got info from existing DXF files

    1           entries are integer values (93)
    3           entries are string values (3)

    data types:
    -----------

    71          boolean values
    93          integer value
    40          double value
    3           string value
    10, 20  30  2d point  (30?)
    11, 21, 31  3d point
    331         soft-pointer ID/handle to object value
    360         hard-pointer ownership ID
    340         hard-pointer ID/handle
    330         soft-pointer ID/handle

    """
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_DATATABLE_TPL)
    CLASS = ExtendedTags.from_text(_DATATABLE_CLS)
    DXFATTRIBS = DXFAttributes(
        none_subclass,
        DefSubclass('AcDbDataTable', {
            'version': DXFAttr(70),
            'columns': DXFAttr(90),
            'rows': DXFAttr(91),
            'table_name': DXFAttr(1),
        }),
    )
