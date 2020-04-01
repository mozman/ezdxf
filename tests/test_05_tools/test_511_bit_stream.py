# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.tools.binarydata import BitStream, EndOfBufferError


def test_read_bit():
    data = b'\xaa'
    bs = BitStream(data)
    assert bs.read_bit() == 1
    assert bs.read_bit() == 0
    assert bs.read_bit() == 1
    assert bs.read_bit() == 0
    assert bs.read_bit() == 1
    assert bs.read_bit() == 0
    assert bs.read_bit() == 1
    assert bs.read_bit() == 0
    with pytest.raises(EndOfBufferError):
        _ = bs.read_bit()


def test_read_bits():
    data = b'\x0f\x0f'
    bs = BitStream(data)
    assert bs.read_bits(4) == 0
    assert bs.read_bits(2) == 3
    assert bs.read_bits(3) == 6
    assert bs.read_bits(4) == 1
    assert bs.read_bits(3) == 7


def test_read_unsigned_byte():
    data = b'\x0f\x0f'
    bs = BitStream(data)
    assert bs.read_bits(4) == 0
    assert bs.read_unsigned_byte() == 0xf0


def test_read_signed_byte():
    data = b'\x0f\xf0'
    bs = BitStream(data)
    assert bs.read_bits(4) == 0
    assert bs.read_signed_byte() == -1


def test_read_unsigned_short():
    # little endian!
    data = b'\x0c\xda\xb0'
    bs = BitStream(data)
    assert bs.read_bits(4) == 0
    assert bs.read_unsigned_short() == 0xabcd
    assert bs.read_bits(4) == 0


def test_read_aligned_unsigned_short():
    # little endian!
    data = b'\x00\xcd\xab'
    bs = BitStream(data)
    assert bs.read_unsigned_byte() == 0
    assert bs.read_unsigned_short() == 0xabcd


def test_read_unsigned_long():
    # little endian!
    data = b'\x00\x0e\xfc\xda\xb0'
    bs = BitStream(data)
    assert bs.read_bits(4) == 0
    assert bs.read_unsigned_long() == 0xabcdef00
    assert bs.read_bits(4) == 0


def test_read_aligned_unsigned_long():
    # little endian!
    data = b'\x00\xef\xcd\xab'
    bs = BitStream(data)
    assert bs.read_unsigned_long() == 0xabcdef00


if __name__ == '__main__':
    pytest.main([__file__])
