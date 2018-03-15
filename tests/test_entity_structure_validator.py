from __future__ import unicode_literals

import pytest

from ezdxf.lldxf.validator import entity_structure_validator
from ezdxf.lldxf.tagger import internal_tag_compiler
from ezdxf import DXFAppDataError, DXFXDataError


def compile(s):
    return list(internal_tag_compiler(s))


def test_valid_tags():
    tags = list(entity_structure_validator(compile(VALID_ENTITY)))
    assert len(tags) == 6


# The structure validator does not know anything about entities, except its basic tag structure
VALID_ENTITY = """0
LINE
102
{APP
40
1
102
}
1001
TEST
1000
STRING
"""


def test_invalid_app_data_without_closing_tag():
    with pytest.raises(DXFAppDataError):
        list(entity_structure_validator(compile(INVALID_APPDATA_NO_CLOSING_TAG)))


INVALID_APPDATA_NO_CLOSING_TAG = """0
LINE
102
{APP
40
1
1001
TEST
1000
STRING
"""


def test_invalid_app_data_without_opening_tag():
    with pytest.raises(DXFAppDataError):
        list(entity_structure_validator(compile(INVALID_APPDATA_NO_OPENING_TAG)))


INVALID_APPDATA_NO_OPENING_TAG = """0
LINE
102
}
40
1
1001
TEST
1000
STRING
"""


def test_invalid_app_data_structure_tag():
    with pytest.raises(DXFAppDataError):
        list(entity_structure_validator(compile(INVALID_APPDATA_STRUCTURE_TAG)))


INVALID_APPDATA_STRUCTURE_TAG = """0
LINE
102
INVALID_APPDATA_STRUCTURE_TAG
40
1
1001
TEST
1000
STRING
"""


def test_xrecord_with_group_code_102():
    tags = list(entity_structure_validator(compile(XRECORD_WITH_GROUP_CODE_102)))
    assert tags[0] == (0, 'XRECORD')


XRECORD_WITH_GROUP_CODE_102 = """0
XRECORD
5
D9B071D01A0CB6A5
102
{ACAD_REACTORS
330
D9B071D01A0CB69D
102
}
330
D9B071D01A0CB69D
100
AcDbXrecord
280
 1
102
ACAD_ROUNDTRIP_PRE2007_TABLESTYLE
90
    4
91
    0
1

92
    4
93
    0
2

94
    4
95
    0
3

"""


def test_xrecord_with_long_closing_tag():
    tags = list(entity_structure_validator(compile(XRECORD_APP_DATA_LONG_CLOSING_TAG)))
    assert tags[0] == (0, 'XRECORD')


XRECORD_APP_DATA_LONG_CLOSING_TAG = """  0
XRECORD
5
2F9
102
{ACAD_REACTORS
330
2FF
102
}
330
2FF
100
AcDbXrecord
280
1
1
AcDb_Thumbnail_Schema
102
{ATTRRECORD
341
2FA
2
AcDbDs::TreatedAsObjectData
280
1
291
1
102
ATTRRECORD}
102
{ATTRRECORD
341
2FB
2
AcDbDs::Legacy
280
1
291
1
102
ATTRRECORD}
2
AcDbDs::ID
280
10
91
8
102
{ATTRRECORD
341
2FC
2
AcDs:Indexable
280
1
291
1
102
ATTRRECORD}
102
{ATTRRECORD
341
2FD
2
AcDbDs::HandleAttribute
280
7
282
1
102
ATTRRECORD}
2
Thumbnail_Data
280
15
91
0
"""


def test_invalid_xdata():
    with pytest.raises(DXFXDataError):
        list(entity_structure_validator(compile(INVALID_XDATA_STRUCTURE_TAG)))


INVALID_XDATA_STRUCTURE_TAG = """0
LINE
40
1
1001
TEST
1000
STRING
1
NO GROUP CODE < 1000 in XDATA SECTION
"""


def test_unbalanced_xdata_list_1():
    with pytest.raises(DXFXDataError):
        list(entity_structure_validator(compile(UNBALANCED_XDATA_LIST_1)))


UNBALANCED_XDATA_LIST_1 = """0
LINE
40
1
1001
TEST
1000
STRING
1002
{
1002
{
1002
}
"""


def test_unbalanced_xdata_list_2():
    with pytest.raises(DXFXDataError):
        list(entity_structure_validator(compile(UNBALANCED_XDATA_LIST_2)))


UNBALANCED_XDATA_LIST_2 = """0
LINE
40
1
1001
TEST
1000
STRING
1002
{
1002
{
1002
}
"""


def test_invalid_xdata_list_nesting():
    with pytest.raises(DXFXDataError):
        list(entity_structure_validator(compile(INVALID_XDATA_LIST_NESTING)))


INVALID_XDATA_LIST_NESTING = """0
LINE
40
1
1001
TEST
1000
STRING
1002
{
1002
}
1002
}
1002
{
"""


BLOCKBASEPOINTPARAMETER_CVIL_3D_2018 = """0
BLOCKBASEPOINTPARAMETER
5
4C25
330
4C23
100
AcDbEvalExpr
90
1
98
33
99
4
100
AcDbBlockElement
300
Base Point
98
33
99
4
1071
0
100
AcDbBlockParameter
280
1
281
0
100
AcDbBlock1PtParameter
1010
-3.108080399920343
1020
-0.9562299080084814
1030
0.0
93
0
170
0
171
0
100
AcDbBlockBasepointParameter
1011
0.0
1021
0.0
1031
0.0
1012
0.0
1022
0.0
1032
0.0
"""


def test_extended_group_code_before_XDATA():
    tags = list(entity_structure_validator(compile(BLOCKBASEPOINTPARAMETER_CVIL_3D_2018)))
    assert tags[0] == (0, 'BLOCKBASEPOINTPARAMETER')
