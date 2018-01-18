# Created: 30.04.2014, 2018 rewritten for pytest
# Copyright (C) 2014, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from ezdxf.tools.compressedstring import CompressedString


def test_init():
    assert 'compressed data' == str(CompressedString(""))


def test_decompress():
    cs = CompressedString('test')
    assert 'compressed data' == str(cs)
    assert 'test' == cs.decompress()


def test_compress_big_string():
    s = "123456789" * 1000
    cs = CompressedString(s)
    assert s == cs.decompress()
    assert len(s) > len(cs)


def test_return_type():
    s = "123456789" * 10
    result = CompressedString(s).decompress()
    assert type(s) == type(result)


def test_non_ascii_chars():
    s = "12345äöüß6789" * 10
    result = CompressedString(s).decompress()
    assert s == result
    assert type(s) == type(result)
