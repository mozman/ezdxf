# Copyright (c) 2019-2021 Manfred Moitzi
# License: MIT License

import pytest
import copy
from ezdxf.math import Vec3
from ezdxf.lldxf.const import DXFValueError, DXFStructureError, DXFTypeError
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.lldxf.types import dxftag
from ezdxf.lldxf.tags import (
    Tags,
    find_begin_and_end_of_encoded_xdata_tags,
    NotFoundException,
)
from ezdxf.entities.xdata import XData, XDataUserDict, XDataUserList
from ezdxf.lldxf.repair import filter_invalid_xdata_group_codes


class TagWriter:
    """Mockup"""

    def __init__(self):
        self.tags = []

    def write_tags(self, tags):
        self.tags.append(tags)


@pytest.fixture
def xdata():
    xtags = ExtendedTags.from_text(
        """0
DXFENTITY
1001
MOZMAN
1000
DataStr1
1000
DataStr2
1040
3.14
1001
ACAD
1000
AutoDesk
1000
Revit"""
    )
    return XData(xtags.xdata)


def test_empty_xdata():
    xdata = XData()
    assert len(xdata) == 0
    tagwriter = TagWriter()
    xdata.export_dxf(tagwriter)
    assert len(tagwriter.tags) == 0


def test_add_data(xdata):
    assert "XXX" not in xdata
    xdata.add("XXX", [(1000, "Extended Data String")])
    assert "XXX" in xdata


def test_get_data(xdata):
    assert "MOZMAN" in xdata
    tags = xdata.get("MOZMAN")
    assert len(tags) == 4
    assert tags[0] == (1001, "MOZMAN")
    assert tags[1] == (1000, "DataStr1")
    assert tags[2] == (1000, "DataStr2")
    assert tags[3] == (1040, 3.14)

    with pytest.raises(DXFValueError):
        _ = xdata.get("XXX")


def test_replace_xdata(xdata):
    assert len(xdata) == 2
    xdata.add("MOZMAN", [(1000, "XXX")])
    assert len(xdata) == 2, "replace existing XDATA"

    tags = xdata.get("MOZMAN")
    assert tags[0] == (1001, "MOZMAN")
    assert tags[1] == (1000, "XXX")


def test_discard_xdata(xdata):
    assert len(xdata) == 2
    xdata.discard("MOZMAN")
    assert len(xdata) == 1
    assert "MOZMAN" not in xdata
    # ignore none existing appids
    xdata.discard("xxx")
    assert len(xdata) == 1


def test_cloning(xdata):
    xdata2 = copy.deepcopy(xdata)
    assert len(xdata2) == 2

    assert "MOZMAN" in xdata2
    tags = xdata2.get("MOZMAN")
    assert len(tags) == 4
    assert tags[0] == (1001, "MOZMAN")
    assert tags[1] == (1000, "DataStr1")
    assert tags[2] == (1000, "DataStr2")
    assert tags[3] == (1040, 3.14)
    xdata2.discard("MOZMAN")
    assert "MOZMAN" in xdata
    assert "MOZMAN" not in xdata2


def test_dxf_export(xdata):
    tagwriter = TagWriter()
    xdata.export_dxf(tagwriter)
    result = tagwriter.tags
    assert len(result) == 2
    # appids in original order
    assert result[0][0] == (1001, "MOZMAN")
    assert result[1][0] == (1001, "ACAD")


def test_has_xdata_list(xdata):
    assert xdata.has_xlist("ACAD", "DSTYLE") is False


def test_get_xlist_exception(xdata):
    with pytest.raises(DXFValueError):
        _ = xdata.get_xlist("ACAD", "DSTYLE")


def test_set_xdata_list(xdata):
    xdata.set_xlist("ACAD", "DSTYLE", [(1070, 1), (1000, "String")])
    data = xdata.get_xlist("ACAD", "DSTYLE")
    assert len(data) == 5
    assert data == [
        (1000, "DSTYLE"),
        (1002, "{"),
        (1070, 1),
        (1000, "String"),
        (1002, "}"),
    ]
    # add another list to ACAD
    xdata.set_xlist("ACAD", "MOZMAN", [(1070, 2), (1000, "mozman")])
    data = xdata.get_xlist("ACAD", "MOZMAN")
    assert len(data) == 5
    assert data == [
        (1000, "MOZMAN"),
        (1002, "{"),
        (1070, 2),
        (1000, "mozman"),
        (1002, "}"),
    ]
    data = xdata.get("ACAD")
    assert len(data) == 10 + 3


def test_discard_xdata_list(xdata):
    xdata.set_xlist("ACAD", "DSTYLE", [(1070, 1), (1000, "String")])
    xdata_list = xdata.get_xlist("ACAD", "DSTYLE")
    assert len(xdata_list) == 5
    xdata.discard_xlist("ACAD", "DSTYLE")
    with pytest.raises(DXFValueError):
        _ = xdata.get_xlist("ACAD", "DSTYLE")

    xdata.discard_xlist("ACAD", "DSTYLE")


def test_replace_xdata_list(xdata):
    xdata.set_xlist("ACAD", "DSTYLE", [(1070, 1), (1000, "String")])
    xdata_list = xdata.get_xlist("ACAD", "DSTYLE")
    assert len(xdata_list) == 5
    assert xdata_list == [
        (1000, "DSTYLE"),
        (1002, "{"),
        (1070, 1),
        (1000, "String"),
        (1002, "}"),
    ]
    xdata.set_xlist(
        "ACAD", "DSTYLE", [(1070, 2), (1000, "mozman"), (1000, "data")]
    )
    xdata_list = xdata.get_xlist("ACAD", "DSTYLE")
    assert len(xdata_list) == 6
    assert xdata_list == [
        (1000, "DSTYLE"),
        (1002, "{"),
        (1070, 2),
        (1000, "mozman"),
        (1000, "data"),
        (1002, "}"),
    ]
    # replace not existing list -> append list
    xdata.replace_xlist("ACAD", "MOZMAN", [(1070, 3), (1000, "new")])
    xdata_list = xdata.get_xlist("ACAD", "MOZMAN")
    assert len(xdata_list) == 5
    assert xdata_list == [
        (1000, "MOZMAN"),
        (1002, "{"),
        (1070, 3),
        (1000, "new"),
        (1002, "}"),
    ]
    data = xdata.get("ACAD")
    assert len(data) == 6 + 5 + 3


def test_poyline_with_xdata():
    xdata = XData(
        ExtendedTags(
            filter_invalid_xdata_group_codes(
                Tags.from_text(POLYLINE_WITH_INVALID_XDATA)
            )
        ).xdata
    )
    assert len(xdata) == 2
    assert len(xdata.get("AVE_ENTITY_MATERIAL")) == 27


def test_group_tags_poyline_with_xdata():
    tags = Tags.from_text(POLYLINE_WITH_INVALID_XDATA)
    assert len(tags) == 49
    tags2 = list(filter_invalid_xdata_group_codes(tags))
    assert len(tags2) == 41


POLYLINE_WITH_INVALID_XDATA = """  0
POLYLINE
  5
2A
  8
T-POLYFACE-3DS
 62
     3
 66
     1
 10
0.0
 20
0.0
 30
0.0
 70
    64
 71
     8
 72
    12
1001
AVE_FINISH
1002
{
1070
     0
1005
0
1002
}
1001
AVE_ENTITY_MATERIAL
1002
{
1000

1002
{
1071
        0
1070
     0
1070
     0
1002
{
1070
     0
1070
     0
1070
     0
1040
0.0
1002
}
1070
     0
1070
     0
1002
{
1002
}
1002
}
1002
{
1002
}
1002
{
1002
}
1011
0.0
1021
0.0
1031
0.0
1021
0.0
1031
0.0
1011
1.0
1021
0.0
1031
0.0
1021
0.0
1031
0.0
1011
0.0
1021
0.0
1031
0.0
1021
1.0
1031
0.0
1011
0.0
1021
0.0
1031
0.0
1021
0.0
1031
1.0
1002
}
"""

COLUMNS_SPEC = """1001
ACAD
1000
ACAD_MTEXT_COLUMN_INFO_BEGIN
1000
ACAD_MTEXT_COLUMN_INFO_END
"""

WITHOUT_END_TAG = """1000
ACAD_MTEXT_COLUMN_INFO_BEGIN
"""

WITHOUT_BEGIN_TAG = """1000
ACAD_MTEXT_COLUMN_INFO_END
"""


class TestEncodedXDATATags:
    def test_find_begin_and_end_of_column_info(self):
        start, end = find_begin_and_end_of_encoded_xdata_tags(
            "ACAD_MTEXT_COLUMN_INFO", Tags.from_text(COLUMNS_SPEC)
        )
        assert start, end == (1, 3)

    def test_raise_exception_if_not_found(self):
        with pytest.raises(NotFoundException):
            find_begin_and_end_of_encoded_xdata_tags(
                "MOZMAN", Tags.from_text(COLUMNS_SPEC)
            )

    def test_raise_exception_without_end_tag(self):
        with pytest.raises(DXFStructureError):
            find_begin_and_end_of_encoded_xdata_tags(
                "ACAD_MTEXT_COLUMN_INFO", Tags.from_text(WITHOUT_END_TAG)
            )

    def test_raise_exception_without_begin_tag(self):
        with pytest.raises(DXFStructureError):
            find_begin_and_end_of_encoded_xdata_tags(
                "ACAD_MTEXT_COLUMN_INFO", Tags.from_text(WITHOUT_BEGIN_TAG)
            )


LIST1 = """1001
EZDXF
1000
DefaultList
1002
{
1000
VALUE
1000
CONTENT
1002
}
"""

USER_LIST = """1001
MyAppID
1000
MyUserList
1002
{
1000
VALUE
1000
CONTENT
1002
}
"""


class TestXDataUserList:
    @pytest.fixture
    def list1(self):
        return Tags.from_text(LIST1)

    @pytest.fixture
    def user_list(self):
        return Tags.from_text(USER_LIST)

    def test_load_not_existing_list(self):
        xlist = XDataUserList(XData())
        assert len(xlist) == 0

    def test_load_existing_list(self, list1):
        xlist = XDataUserList(XData([list1]))
        assert len(xlist) == 2
        assert xlist[0] == "VALUE"
        assert xlist[1] == "CONTENT"

    def test_load_user_list(self, user_list):
        xlist = XDataUserList(
            XData([user_list]), name="MyUserList", appid="MyAppID"
        )
        assert len(xlist) == 2
        assert xlist[0] == "VALUE"
        assert xlist[1] == "CONTENT"

    def test_list_like_getitem_interface(self, list1):
        xlist = XDataUserList(XData([list1]))
        assert len(xlist) == 2
        assert xlist[-1] == "CONTENT"
        assert xlist[:] == ["VALUE", "CONTENT"]

    def test_list_like_setitem_interface(self, list1):
        xlist = XDataUserList(XData([list1]))
        xlist[0] = 15
        assert xlist[0] == 15

    def test_list_like_insert_interface(self, list1):
        xlist = XDataUserList(XData([list1]))
        xlist.insert(0, 17)
        assert xlist[0] == 17
        assert len(xlist) == 3

    def test_list_like_delitem_interface(self, list1):
        xlist = XDataUserList(XData([list1]))
        del xlist[0]
        assert len(xlist) == 1
        assert xlist[0] == "CONTENT"

    def test_commit_creates_valid_XDATA(self):
        xlist = XDataUserList()
        xlist.extend(["String", Vec3(1, 2, 3), 3.1415, 256])
        xlist.commit()
        tags = xlist.xdata.get("EZDXF")
        assert tags == [
            dxftag(1001, "EZDXF"),
            dxftag(1000, "DefaultList"),
            dxftag(1002, "{"),
            dxftag(1000, "String"),
            dxftag(1010, (1, 2, 3)),
            dxftag(1040, 3.1415),
            dxftag(1071, 256),
            dxftag(1002, "}"),
        ]

    def test_commit_replaces_existing_XDATA(self, list1):
        xlist = XDataUserList(XData([list1]))
        xlist.clear()
        xlist.extend(["String", Vec3(1, 2, 3), 3.1415, 256])
        xlist.commit()
        tags = xlist.xdata.get("EZDXF")
        assert tags == [
            dxftag(1001, "EZDXF"),
            dxftag(1000, "DefaultList"),
            dxftag(1002, "{"),
            dxftag(1000, "String"),
            dxftag(1010, (1, 2, 3)),
            dxftag(1040, 3.1415),
            dxftag(1071, 256),
            dxftag(1002, "}"),
        ]

    def test_modify_existing_XDATA(self, list1):
        xlist = XDataUserList(XData([list1]))
        xlist[0] = 3.1415
        xlist[1] = 256
        xlist.commit()
        tags = xlist.xdata.get("EZDXF")
        assert tags == [
            dxftag(1001, "EZDXF"),
            dxftag(1000, "DefaultList"),
            dxftag(1002, "{"),
            dxftag(1040, 3.1415),
            dxftag(1071, 256),
            dxftag(1002, "}"),
        ]

    def test_modify_existing_user_list(self, user_list):
        xlist = XDataUserList(
            XData([user_list]), name="MyUserList", appid="MyAppID"
        )
        xlist[0] = 3.1415
        xlist[1] = 256
        xlist.commit()
        tags = xlist.xdata.get("MyAppID")
        assert tags == [
            dxftag(1001, "MyAppID"),
            dxftag(1000, "MyUserList"),
            dxftag(1002, "{"),
            dxftag(1040, 3.1415),
            dxftag(1071, 256),
            dxftag(1002, "}"),
        ]

    def test_context_manager_interface(self):
        xdata = XData()
        with XDataUserList(xdata) as xlist:
            xlist.extend(["String", Vec3(1, 2, 3), 3.1415, 256])

        tags = xdata.get("EZDXF")
        assert tags == [
            dxftag(1001, "EZDXF"),
            dxftag(1000, "DefaultList"),
            dxftag(1002, "{"),
            dxftag(1000, "String"),
            dxftag(1010, (1, 2, 3)),
            dxftag(1040, 3.1415),
            dxftag(1071, 256),
            dxftag(1002, "}"),
        ]

    @pytest.mark.parametrize("char", ["\n", "\r"])
    def test_invalid_line_break_characters_raise_exception(self, char):
        xlist = XDataUserList()
        xlist.append(char)
        with pytest.raises(DXFValueError):
            xlist.commit()

    def test_too_long_string_raise_exception(self):
        # The XDATA limit for group code 1000 is 255 characters
        xlist = XDataUserList()
        xlist.append("0123456789" * 26)
        with pytest.raises(DXFValueError):
            xlist.commit()


DICT1 = """1001
EZDXF
1000
DefaultDict
1002
{
1000
Key0
1000
StringValue
1000
Float
1040
3.1415
1002
}
"""

USER_DICT = """1001
MyAppID
1000
MyUserDict
1002
{
1000
MyKey
1000
MyString
1000
Int
1071
65535
1002
}
"""


class TestXDataUserDict:
    @pytest.fixture
    def dict1(self):
        return Tags.from_text(DICT1)

    @pytest.fixture
    def user_dict(self):
        return Tags.from_text(USER_DICT)

    def test_load_not_existing_dict(self):
        xdict = XDataUserDict(XData())
        assert len(xdict) == 0

    def test_load_existing_dict(self, dict1):
        xdict = XDataUserDict(XData([dict1]))
        assert len(xdict) == 2
        assert xdict["Key0"] == "StringValue"
        assert xdict["Float"] == 3.1415

    def test_load_user_dict(self, user_dict):
        xdict = XDataUserDict(
            XData([user_dict]), name="MyUserDict", appid="MyAppID"
        )
        assert len(xdict) == 2
        assert xdict["MyKey"] == "MyString"
        assert xdict["Int"] == 65535

    def test_dict_like_interface(self, dict1):
        xdict = XDataUserDict(XData([dict1]))
        assert len(xdict) == 2
        assert "Key0" in xdict
        assert list(xdict.keys()) == ["Key0", "Float"]
        assert list(xdict.values()) == ["StringValue", 3.1415]

    def test_dict_like_setitem_interface(self):
        xdict = XDataUserDict()
        xdict["Test"] = 17
        assert len(xdict) == 1
        assert "Test" in xdict

    @pytest.mark.parametrize("data", [0, 3.14, (1, 1), Vec3()])
    def test_setitem_accepts_only_strings(self, data):
        xdict = XDataUserDict()
        with pytest.raises(DXFTypeError):
            xdict[data] = "abc"

    def test_dict_like_del_interface(self, dict1):
        xdict = XDataUserDict(XData([dict1]))
        del xdict["Key0"]
        assert len(xdict) == 1
        xdict.clear()
        assert len(xdict) == 0

    def test_discard_non_existing_key(self):
        xdict = XDataUserDict()
        xdict.discard("XXX")
        assert len(xdict) == 0

    def test_commit_creates_valid_XDATA(self):
        xdict = XDataUserDict()
        xdict["Key0"] = "StringValue"
        xdict["Float"] = 3.1415
        xdict.commit()
        tags = xdict.xdata.get("EZDXF")
        assert tags == [
            dxftag(1001, "EZDXF"),
            dxftag(1000, "DefaultDict"),
            dxftag(1002, "{"),
            dxftag(1000, "Key0"),
            dxftag(1000, "StringValue"),
            dxftag(1000, "Float"),
            dxftag(1040, 3.1415),
            dxftag(1002, "}"),
        ]

    def test_context_manager_interface(self):
        xdata = XData()
        with XDataUserDict(xdata) as xdict:
            xdict["Key1"] = 256
            xdict["Key2"] = "Value2"

        tags = xdata.get("EZDXF")
        assert tags == [
            dxftag(1001, "EZDXF"),
            dxftag(1000, "DefaultDict"),
            dxftag(1002, "{"),
            dxftag(1000, "Key1"),
            dxftag(1071, 256),
            dxftag(1000, "Key2"),
            dxftag(1000, "Value2"),
            dxftag(1002, "}"),
        ]

    def test_update_from_dict(self):
        xdict = XDataUserDict()
        xdict.update({"a": 1, "b": "str"})
        assert xdict["a"] == 1
        assert xdict["b"] == "str"

    def test_update_supports_only_string_keys(self):
        xdict = XDataUserDict()
        with pytest.raises(DXFTypeError):
            xdict.update({0: 1})


if __name__ == "__main__":
    pytest.main([__file__])
