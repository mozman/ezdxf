#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.lldxf import const
from ezdxf.math import Vec3
from ezdxf.lldxf.tags import Tags
from ezdxf.urecord import (
    parse_items,
    compile_user_record,
    parse_binary_data,
    BinaryRecord,
)


class TestFlatRecord:
    @pytest.fixture
    def tags(self):
        return Tags.from_text(FLAT_RECORD)

    def test_parse_all(self, tags):
        data = parse_items(tags)
        assert len(data) == 4

    def test_parse_str(self, tags):
        data = parse_items(tags)[0]
        assert data == "MyString"
        assert type(data) == str

    def test_parse_float(self, tags):
        data = parse_items(tags)[1]
        assert data == 3.1415
        assert type(data) is float

    def test_parse_int(self, tags):
        data = parse_items(tags)[2]
        assert data == 255
        assert type(data) is int

    def test_parse_vec3(self, tags):
        data = parse_items(tags)[3]
        assert data == (7, 8, 9)
        assert type(data) is Vec3


def test_top_level_list():
    tags = Tags.from_text(LIST1)
    data = parse_items(tags)
    assert data == ["MyString", ["ListItem1"], "Tail"]


def test_nested_list_inside_list():
    tags = Tags.from_text(LIST2)
    data = parse_items(tags)
    assert data == ["MyString", ["ListItem1", ["ListItem2"]], "Tail"]


def test_top_level_dict():
    tags = Tags.from_text(DICT1)
    data = parse_items(tags)
    assert data == ["MyString", {"Key1": "Value1"}, "Tail"]


def test_nested_dict_as_dict_value():
    tags = Tags.from_text(DICT2)
    data = parse_items(tags)
    assert data == ["MyString", {"Key1": {"Key2": "Value2"}}, "Tail"]


def test_nested_list_as_dict_value():
    tags = Tags.from_text(DICT_LIST)
    data = parse_items(tags)
    assert data == ["MyString", {"Key": ["ListItem"]}, "Tail"]


def test_nested_dict_inside_list():
    tags = Tags.from_text(LIST_DICT)
    data = parse_items(tags)
    assert data == [
        "MyString",
        ["ListItem1", {"Key": "Value"}, "ListItem2"],
        "Tail",
    ]


def test_missing_open_tag_raises_dxf_structure_error():
    tags = Tags.from_text("1\nListItem1\n302\n]")
    with pytest.raises(const.DXFStructureError):
        parse_items(tags)


def test_missing_close_tag_raises_dxf_structure_error():
    tags = Tags.from_text("302\n[\n1\nListItem1")
    with pytest.raises(const.DXFStructureError):
        parse_items(tags)


def test_invalid_group_code_raises_value_error():
    tags = Tags.from_text("5\ninvalid\n")
    with pytest.raises(ValueError):
        parse_items(tags)


class TestCompileData:
    def test_compile_empty_data(self):
        tags = compile_user_record("TEST", [])
        assert tags[0] == (2, "TEST")
        assert len(tags) == 1

    @pytest.mark.parametrize(
        "value",
        [
            "MyString",
            257,
            3.1415,
            Vec3(5, 6, 7),
        ],
        ids=["str", "int", "float", "Vec3"],
    )
    def test_compile_simple_types(self, value):
        tags = compile_user_record("TEST", [value])
        assert parse_items(tags[1:]) == [value]

    @pytest.mark.parametrize(
        "struct",
        [
            [1, 2, 3],  # simple flat list
            [{"key": "value"}],  # top level structure has to be a list!
            ["head", [1, 2, 3], "tail"],  # nested list
            ["head", {"key": "value"}, "tail"],  # nested dict
            ["head", {"key": [1, 2, 3]}, "tail"],  # list as dict value
            ["head", [1, 2, {"key": "value"}], "tail"],  # dict inside a list
        ],
        ids=[
            "flat list",
            "flat dict",
            "nested list",
            "nested dict",
            "list as dict value",
            "dict inside a list",
        ],
    )
    def test_compile_complex_structures(self, struct):
        tags = compile_user_record("TEST", struct)
        assert parse_items(tags[1:]) == struct


def test_parse_binary_data():
    assert (
        parse_binary_data(Tags.from_text(BINARY_DATA))
        == b"0123456789\xab\xba" * 2
    )


class TestBinaryRecord:
    def test_to_str(self):
        record = BinaryRecord()
        record.data = b"\xfe\xfe"
        assert str(record) == "FEFE"


FLAT_RECORD = """1
MyString
40
3.1415
90
255
10
7
20
8
30
9
"""

LIST1 = """1
MyString
302
[
1
ListItem1
302
]
1
Tail
"""

LIST2 = """1
MyString
302
[
1
ListItem1
302
[
1
ListItem2
302
]
302
]
1
Tail
"""

DICT1 = """1
MyString
302
{
1
Key1
1
Value1
302
}
1
Tail
"""

DICT2 = """1
MyString
302
{
1
Key1
302
{
1
Key2
1
Value2
302
}
302
}
1
Tail
"""

DICT_LIST = """1
MyString
302
{
1
Key
302
[
1
ListItem
302
]
302
}
1
Tail
"""

LIST_DICT = """1
MyString
302
[
1
ListItem1
302
{
1
Key
1
Value
302
}
1
ListItem2
302
]
1
Tail
"""

BINARY_DATA = """160
24
310
30313233343536373839ABBA
310
30313233343536373839ABBA
"""

if __name__ == "__main__":
    pytest.main([__file__])
