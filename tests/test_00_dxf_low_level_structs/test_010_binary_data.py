# Copyright (c) 2014-2019, Manfred Moitzi
# License: MIT License
from binascii import unhexlify
from ezdxf.tools.binarydata import hex_strings_to_bytes
from ezdxf.tools.binarydata import int_to_hexstr, bytes_to_hexstr


def test_hexstr_to_bytes():
    assert unhexlify('FFFF') == b"\xff\xff"


def test_hexstr_data_to_bytes_1():
    assert hex_strings_to_bytes(['FFFF']) == b"\xff\xff"


def test_hexstr_data_to_bytes_2():
    assert hex_strings_to_bytes(['F0F0', '1A1C']) == b"\xF0\xF0\x1A\x1C"


def test_byte_to_hexstr():
    assert int_to_hexstr(65535) == 'FFFF'


def test_bytes_to_hexstr():
    assert bytes_to_hexstr(b"\xff\xff") == 'FFFF'
