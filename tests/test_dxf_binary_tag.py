# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from ezdxf.lldxf.types import DXFBinaryTag


def test_init():
    tag = DXFBinaryTag(310, 'FFFF')
    assert tag == (310, b"\xff\xff")

    tag2 = DXFBinaryTag(code=310, value='FFFF')
    assert tag2 == (310, b"\xff\xff")


def test_index_able():
    tag = DXFBinaryTag(310, 'FFFF')
    assert tag[0] == 310
    assert tag[1] == b"\xff\xff"


def test_dxf_str():
    assert DXFBinaryTag(310, 'FFFF').tostring() == "FFFF"
    assert DXFBinaryTag(310, 'FFFF').dxfstr() == "310\nFFFF\n"
