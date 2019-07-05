# Copyright (c) 2014-2019, Manfred Moitzi
# License: MIT License
from ezdxf.tools.binarydata import hexstr_data_to_bytes


def test_hexstr_data_to_bytes_1():
    assert hexstr_data_to_bytes(['FFFF']) == b"\xff\xff"


def test_hexstr_data_to_bytes_2():
    assert hexstr_data_to_bytes(['F0F0', '1A1C']) == b"\xF0\xF0\x1A\x1C"
