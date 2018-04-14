# Created: 08.04.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals
from .dxfobjects import ExtendedTags, DXFAttr, DefSubclass, DXFAttributes
from .dxfobjects import none_subclass, DXFObject

_FIELD_CLS = """0
CLASS
1
FIELD
2
AcDbField
3
ObjectDBX Classes
90
1152
91
0
280
0
281
0
"""

_FIELD_TPL = """0
FIELD
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
AcDbField
1
_text
2

90
0
"""

field_subclass = DefSubclass('AcDbField', {
    'evaluator_id': DXFAttr(1),
    'field_code': DXFAttr(2),
    'field_code_overflow': DXFAttr(3),  # Overflow of field code string
    'n_child_fields': DXFAttr(90),  # Number of child fields
    # 360:  Child field ID (AcDbHardOwnershipId); repeats for number of children
    #  97:  Number of object IDs used in the field code
    # 331:  Object ID used in the field code (AcDbSoftPointerId); repeats for the number of object IDs used in the field code
    #  93:  Number of the data set in the field
    #   6:  Key string for the field data; a key-field pair is repeated for the number of data sets in the field
    #   7:  Key string for the evaluated cache; this key is hard-coded as ACFD_FIELD_VALUE
    #  90:  Data type of field value
    #  91:  Long value (if data type of field value is long)
    # 140:  Double value (if data type of field value is double)
    # 330:  ID value, AcDbSoftPointerId (if data type of field value is ID)
    #  92:  Binary data buffer size (if data type of field value is binary)
    # 310:  Binary data (if data type of field value is binary)
    # 301:  Format string
    #   9:  Overflow of Format string
    #  98:  Length of format string

})


class Field(DXFObject):
    # Requires AC1021/R2007
    TEMPLATE = ExtendedTags.from_text(_FIELD_TPL)
    CLASS = ExtendedTags.from_text(_FIELD_CLS)
    DXFATTRIBS = DXFAttributes(none_subclass, field_subclass)


