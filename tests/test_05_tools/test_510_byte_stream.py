# Copyright (c) 2020, Manfred Moitzi
# License: MIT License

import pytest
import struct
from ezdxf.tools.binarydata import ByteStream


def test_init():
    bs = ByteStream(b'ABCDABC\x00')
    assert bs.index == 0
    assert len(bs.buffer) == 8


def test_read_ps():
    bs = ByteStream(b'ABCDABC\x00')
    s = bs.read_ps()
    assert s == 'ABCDABC'
    assert bs.index == 8
    assert bs.has_data is False


def test_read_ps_align():
    bs = ByteStream(b'ABCD\x00')
    s = bs.read_ps()
    assert s == 'ABCD'
    assert bs.index == 8
    assert bs.has_data is False


def test_read_pus():
    bs = ByteStream(b'A\x00B\x00C\x00D\x00\x00\x00')
    s = bs.read_pus()
    assert s == 'ABCD'
    assert bs.index == 12
    assert bs.has_data is False


def test_read_doubles():
    data = struct.pack('3d', 1.0, 2.0, 3.0)
    bs = ByteStream(data)
    x = bs.read_struct('d')[0]
    y = bs.read_struct('d')[0]
    z = bs.read_struct('d')[0]
    assert (x, y, z) == (1.0, 2.0, 3.0)
    assert bs.index == 24
    assert bs.has_data is False


if __name__ == '__main__':
    pytest.main([__file__])
