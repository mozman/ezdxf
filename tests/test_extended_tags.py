# coding: utf8
# Created: 30.04.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest
from io import StringIO

from ezdxf.lldxf.tags import Tags, DXFTag
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf import DXFKeyError, DXFValueError
from ezdxf.lldxf.tagwriter import TagWriter
from ezdxf.lldxf.repair import filter_subclass_marker


@pytest.fixture
def xtags1():
    return ExtendedTags.from_text(XTAGS1)


def test_init_appdata(xtags1):
    assert xtags1.get_app_data('{ACAD_XDICTIONARY') is not None


def test_init_with_tags():
    tags = Tags.from_text(XTAGS1)
    xtags = ExtendedTags(tags)
    assert 3 == len(xtags.subclasses)
    assert 1 == len(xtags.xdata)


def test_init_xdata(xtags1):
    assert xtags1.get_xdata('RAK') is not None


def test_init_one_tag():
    xtags = ExtendedTags([DXFTag(0, 'SECTION')])
    assert xtags.noclass[0] == (0, 'SECTION')


def test_getitem(xtags1):
    assert xtags1[0] == xtags1.noclass[0]


def test_appdata_content_count(xtags1):
    xdict = xtags1.get_app_data('{ACAD_XDICTIONARY')
    assert 3 == len(xdict)


def test_appdata_content(xtags1):
    xdict = xtags1.get_app_data('{ACAD_XDICTIONARY')
    assert xdict.get_first_value(360) == "63D5"


def test_tags_skips_appdata_content(xtags1):
    with pytest.raises(DXFValueError):
        xtags1.noclass.get_first_value(360)


def test_xdata_content_count(xtags1):
    rak = xtags1.get_xdata('RAK')
    assert 17 == len(rak)


def test_tags_skips_xdata_content(xtags1):
    with pytest.raises(DXFValueError):
        xtags1.noclass.get_first_value(1000)


def test_copy(xtags1):
    stream = StringIO()
    tagwriter = TagWriter(stream)
    tagwriter.write_tags(xtags1)
    assert XTAGS1 == stream.getvalue()
    stream.close()


def test_getitem_layer(xtags1):
    assert xtags1.noclass[0] == (0, 'LAYER')


def test_getitem_xdict(xtags1):
    assert xtags1.noclass[2] == (102, 0)


def test_getitem_parent(xtags1):
    assert xtags1.noclass[3] == (330, '18')


def test_get_last_item(xtags1):
    assert xtags1.noclass[-1] == (330, '18')


def test_tagscount(xtags1):
    """ apdata counts as one tag and xdata counts as one tag. """
    assert 4 == len(xtags1.noclass)


def test_subclass_AcDbSymbolTableRecord(xtags1):
    subclass = xtags1.get_subclass('AcDbSymbolTableRecord')
    assert 1 == len(subclass)


def test_subclass_AcDbLayerTableRecord(xtags1):
    subclass = xtags1.get_subclass('AcDbLayerTableRecord')
    assert 8 == len(subclass)


def test_clone_is_equal(xtags1):
    clone = xtags1.clone()
    assert xtags1 is not clone
    assert xtags1.appdata is not clone.appdata
    assert xtags1.subclasses is not clone.subclasses
    assert xtags1.xdata is not clone.xdata
    assert list(xtags1) == list(clone)


def test_replace_handle(xtags1):
    xtags1.replace_handle('AA')
    assert 'AA' == xtags1.get_handle()


XTAGS1 = """  0
LAYER
  5
7
102
{ACAD_XDICTIONARY
360
63D5
102
}
330
18
100
AcDbSymbolTableRecord
100
AcDbLayerTableRecord
  2
0
 70
0
 62
7
  6
CONTINUOUS
370
-3
390
8
347
805
1001
RAK
1000
{75-LÄNGENSCHNITT-14
1070
0
1070
7
1000
CONTINUOUS
1071
-3
1071
1
1005
8
1000
75-LÄNGENSCHNITT-14}
1000
{75-LÄNGENSCHNITT-2005
1070
0
1070
7
1000
CONTINUOUS
1071
-3
1071
1
1005
8
1000
75-LÄNGENSCHNITT-2005}
"""


@pytest.fixture
def xtags2():
    return ExtendedTags.from_text(XTAGS2)


def test_xdata_count(xtags2):
    assert 3 == len(xtags2.xdata)


def test_tags_count(xtags2):
    """ 3 xdata chunks and two 'normal' tag. """
    assert 2 == len(xtags2.noclass)


def test_xdata3_tags(xtags2):
    xdata = xtags2.get_xdata('XDATA3')
    assert xdata[0] == (1001, 'XDATA3')
    assert xdata[1] == (1000, 'TEXT-XDATA3')
    assert xdata[2] == (1070, 2)
    assert xdata[3] == (1070, 3)


def test_new_data(xtags2):
    xtags2.new_xdata('NEWXDATA', [(1000, 'TEXT')])
    assert xtags2.has_xdata('NEWXDATA') is True

    xdata = xtags2.get_xdata('NEWXDATA')
    assert xdata[0] == (1001, 'NEWXDATA')
    assert xdata[1] == (1000, 'TEXT')


def test_set_new_data(xtags2):
    xtags2.new_xdata('NEWXDATA', tags=[(1000, "Extended Data String")])
    assert xtags2.has_xdata('NEWXDATA') is True

    xdata = xtags2.get_xdata('NEWXDATA')
    assert (1001, 'NEWXDATA') == xdata[0]
    assert (1000, "Extended Data String") == xdata[1]


def test_append_xdata(xtags2):
    xdata = xtags2.get_xdata('MOZMAN')
    assert 4 == len(xdata)

    xdata.append(DXFTag(1000, "Extended Data String"))
    xdata = xtags2.get_xdata('MOZMAN')
    assert 5 == len(xdata)

    assert DXFTag(1000, "Extended Data String") == xdata[4]


XTAGS2 = """  0
LAYER
  5
7
1001
RAK
1000
TEXT-RAK
1070
1
1070
1
1001
MOZMAN
1000
TEXT-MOZMAN
1070
2
1070
2
1001
XDATA3
1000
TEXT-XDATA3
1070
2
1070
3
"""


@pytest.fixture
def xtags3():
    return ExtendedTags.from_text(SPECIALCASE_TEXT)


def test_read_tags(xtags3):
    subclass2 = xtags3.get_subclass('AcDbText')
    assert (100, 'AcDbText') == subclass2[0]


def test_read_tags_2(xtags3):
    subclass2 = xtags3.get_subclass('AcDbText')
    assert (100, 'AcDbText') == subclass2[0]
    assert (1, 'Title:') == subclass2[3]


def test_read_tags_3(xtags3):
    subclass2 = xtags3.get_subclass('AcDbText', 3)
    assert (100, 'AcDbText') == subclass2[0]
    assert (73, 2) == subclass2[1]


def test_key_error(xtags3):
    with pytest.raises(DXFKeyError):
        xtags3.get_subclass('AcDbText', pos=4)


def test_skip_empty_subclass(xtags3):
    xtags3.subclasses[1] = Tags()  # create empty subclass
    subclass2 = xtags3.get_subclass('AcDbText')
    assert (100, 'AcDbText') == subclass2[0]


SPECIALCASE_TEXT = """  0
TEXT
5
8C9
330
6D
100
AcDbEntity
8
0
100
AcDbText
10
4.30
20
1.82
30
0.0
40
0.125
1
Title:
41
0.85
7
ARIALNARROW
100
AcDbText
73
2
"""

ACAD_REACTORS = '{ACAD_REACTORS'


@pytest.fixture
def xtags4():
    return ExtendedTags.from_text(NO_REACTORS)


def test_get_not_existing_reactor(xtags4):
    with pytest.raises(DXFValueError):
        xtags4.get_app_data(ACAD_REACTORS)


def test_new_reactors(xtags4):
    xtags4.new_app_data(ACAD_REACTORS)
    assert (102, 0) == xtags4.noclass[-1]  # code = 102, value = index in appdata list


def test_append_not_existing_reactors(xtags4):
    xtags4.new_app_data(ACAD_REACTORS, [DXFTag(330, 'DEAD')])
    reactors = xtags4.get_app_data_content(ACAD_REACTORS)
    assert 1 == len(reactors)
    assert DXFTag(330, 'DEAD') == reactors[0]


def test_append_to_existing_reactors(xtags4):
    xtags4.new_app_data(ACAD_REACTORS, [DXFTag(330, 'DEAD')])
    reactors = xtags4.get_app_data_content(ACAD_REACTORS)
    reactors.append(DXFTag(330, 'DEAD2'))
    xtags4.set_app_data_content(ACAD_REACTORS, reactors)

    reactors = xtags4.get_app_data_content(ACAD_REACTORS)
    assert DXFTag(330, 'DEAD') == reactors[0]
    assert DXFTag(330, 'DEAD2') == reactors[1]


NO_REACTORS = """  0
TEXT
  5
8C9
330
6D
100
AcDbEntity
  8
0
100
AcDbText
 10
4.30
 20
1.82
 30
0.0
 40
0.125
  1
Title:
 41
0.85
  7
ARIALNARROW
"""


def test_repair_leica_disto_files():
    tags = ExtendedTags(filter_subclass_marker(Tags.from_text(LEICA_DISTO_TAGS)))
    assert 9 == len(tags.noclass)
    assert 1 == len(tags.subclasses)


LEICA_DISTO_TAGS = """0
LINE
100
AcDbEntity
8
LEICA_DISTO_3D
62
256
6
ByLayer
5
75
100
AcDbLine
10
0.819021
20
-0.633955
30
-0.273577
11
0.753216
21
-0.582009
31
-0.276937
39
0
210
0
220
0
230
1
"""


def test_group_code_1000_outside_XDATA():
    tags = ExtendedTags(Tags.from_text(BLOCKBASEPOINTPARAMETER_CVIL_3D_2018))
    assert tags.dxftype() == 'BLOCKBASEPOINTPARAMETER'
    assert len(tags.subclasses) == 6
    block_base_point_parameter = tags.get_subclass('AcDbBlockBasepointParameter')
    assert len(block_base_point_parameter) == 3
    assert block_base_point_parameter[0] == (100, 'AcDbBlockBasepointParameter')
    assert block_base_point_parameter[1] == (1011, (0., 0., 0.))
    assert block_base_point_parameter[2] == (1012, (0., 0., 0.))

    block_element = tags.get_subclass('AcDbBlockElement')
    assert block_element[4] == (1071, 0)

    stream = StringIO()
    tagwriter = TagWriter(stream)
    tagwriter.write_tags(tags)
    lines = stream.getvalue()
    stream.close()
    assert len(lines.split('\n')) == len(BLOCKBASEPOINTPARAMETER_CVIL_3D_2018.split('\n'))


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


def test_xrecord_with_group_code_102():
    tags = ExtendedTags(Tags.from_text(XRECORD_WITH_GROUP_CODE_102))
    assert tags.dxftype() == 'XRECORD'
    assert len(tags.appdata) == 1
    assert tags.noclass[2] == (102, 0)  # 0 == index in appdata list
    assert tags.appdata[0][0] == (102, '{ACAD_REACTORS')

    xrecord = tags.get_subclass('AcDbXrecord')
    assert xrecord[2] == (102, 'ACAD_ROUNDTRIP_PRE2007_TABLESTYLE')
    assert len(list(tags)) * 2 + 1 == len(XRECORD_WITH_GROUP_CODE_102.split('\n'))  # +1 == appending '\n'


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
    tags = ExtendedTags(Tags.from_text(XRECORD_APP_DATA_LONG_CLOSING_TAG))
    assert tags.dxftype() == 'XRECORD'
    assert len(tags.appdata) == 5

    attr_rec = tags.appdata[4]
    assert attr_rec[0] == (102, '{ATTRRECORD')
    assert attr_rec[1] == (341, '2FD')
    assert len(list(tags)) * 2 + 1 == len(XRECORD_APP_DATA_LONG_CLOSING_TAG.split('\n'))  # +1 == appending '\n'

    # test USUAL_102_TAG_INSIDE_APP_DATA
    attr_rec = tags.appdata[1]
    assert attr_rec[0] == (102, '{ATTRRECORD')
    assert attr_rec[1] == (341, '2FA')
    assert attr_rec[2] == (102, 'USUAL_102_TAG_INSIDE_APP_DATA')

    # test USUAL_102_TAG_OUTSIDE_APP_DATA
    xrecord = tags.get_subclass('AcDbXrecord')
    assert xrecord[4] == (102, 'USUAL_102_TAG_OUTSIDE_APP_DATA')

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
102
USUAL_102_TAG_INSIDE_APP_DATA
2
AcDbDs::TreatedAsObjectData
280
1
291
1
102
ATTRRECORD}
102
USUAL_102_TAG_OUTSIDE_APP_DATA
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
