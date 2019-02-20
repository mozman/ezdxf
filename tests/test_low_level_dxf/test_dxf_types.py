# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from ezdxf.lldxf.types import DXFTag, get_xcode_for


def test_init():
    tag = DXFTag(1, 'text')
    assert tag == (1, 'text')

    tag2 = DXFTag(code=2, value='text2')
    assert tag2 == (2, 'text2')


def test_equality():
    assert (1, 'text') == DXFTag(1, 'text'), 'should be equal to tuple'
    # Python 2.7 Issue
    assert ((1, 'text') != DXFTag(1, 'text')) is False

    assert (1, 'text') != DXFTag(1, 'text2'), 'should be not equal to tuple'
    assert DXFTag(1, 'text') == (1, 'text'), 'should be equal to tuple'
    assert DXFTag(1, 'text') != (1, 'text2'), 'should be not equal to tuple'
    assert DXFTag(1, 'text') == DXFTag(1, 'text')
    assert DXFTag(1, 'text') != DXFTag(1, 'text2')


def test_index_able():
    tag = DXFTag(1, 'text')
    assert tag[0] == 1
    assert tag[1] == 'text'


def test_unpack():
    code, value = DXFTag(code=1, value='text')
    assert code == 1
    assert value == 'text'


def test_iterable():
    tag = tuple(DXFTag(1, 'text'))
    assert tag == (1, 'text')


def test_public_attributes():
    tag = DXFTag(1, 'text')
    assert tag.code == 1
    assert tag.value == 'text'


def test_dxf_str():
    assert DXFTag(1, 'text').dxfstr() == "  1\ntext\n"


def test_xcode_for():
    assert get_xcode_for(3) == 1000
    assert get_xcode_for(70) == 1070
    assert get_xcode_for(71) == 1070
    assert get_xcode_for(40) == 1040
    assert get_xcode_for(5) == 1005
    assert get_xcode_for(344) == 1005

