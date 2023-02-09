# Copyright (c) 2018-2019 Manfred Moitzi
# License: MIT License
import pytest

from ezdxf.lldxf.types import DXFTag, get_xcode_for, is_valid_handle


def test_init():
    tag = DXFTag(1, "text")
    assert tag == (1, "text")

    tag2 = DXFTag(code=2, value="text2")
    assert tag2 == (2, "text2")


def test_immutability():
    tag = DXFTag(1, "text")
    with pytest.raises(AttributeError):
        tag.code = 2
    with pytest.raises(AttributeError):
        tag.value = "string"


def test_equality():
    assert (1, "text") == DXFTag(1, "text"), "should be equal to tuple"
    # Python 2.7 Issue
    assert ((1, "text") != DXFTag(1, "text")) is False

    assert (1, "text") != DXFTag(1, "text2"), "should be not equal to tuple"
    assert DXFTag(1, "text") == (1, "text"), "should be equal to tuple"
    assert DXFTag(1, "text") != (1, "text2"), "should be not equal to tuple"
    assert DXFTag(1, "text") == DXFTag(1, "text")
    assert DXFTag(1, "text") != DXFTag(1, "text2")


def test_index_able():
    tag = DXFTag(1, "text")
    assert tag[0] == 1
    assert tag[1] == "text"


def test_unpack():
    code, value = DXFTag(code=1, value="text")
    assert code == 1
    assert value == "text"


def test_iterable():
    tag = tuple(DXFTag(1, "text"))
    assert tag == (1, "text")


def test_public_attributes():
    tag = DXFTag(1, "text")
    assert tag.code == 1
    assert tag.value == "text"


def test_dxf_str():
    assert DXFTag(1, "text").dxfstr() == "  1\ntext\n"


def test_xcode_for():
    assert get_xcode_for(3) == 1000
    assert get_xcode_for(70) == 1070
    assert get_xcode_for(71) == 1070
    assert get_xcode_for(40) == 1040
    assert get_xcode_for(5) == 1005
    assert get_xcode_for(344) == 1005


def test_is_valid_handle():
    assert (
        is_valid_handle("0") is True
    ), "0 is a valid handle, but not allowed aa key in the entity database"
    assert is_valid_handle("ABBA") is True
    assert is_valid_handle("FEFE") is True
    assert is_valid_handle(None) is False, "None is not a valid handle"
    assert is_valid_handle("X") is False, "Not a valid hex value"
    assert is_valid_handle(1) is False, "Integer is not a valid handle"
    assert is_valid_handle(1.0) is False, "Float is not a valid handle"
