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


def test_read_bitshort():
    bs = BitStream(b'\xe0')
    assert bs.read_bit_short() == 256  # 11
    assert bs.read_bit_short() == 0  # 10
    bs = BitStream(b'\x00\xff\xff')
    bs.read_bits(6)
    assert bs.read_bit_short() == -1
    assert BitStream(b'\x7f\x00').read_bit_short() == 252


def test_read_modular_chars():
    bs = BitStream(bytes([
        0b11101001, 0b10010111, 0b11100110, 0b00110101,
        0b10000010, 0b00100100,
        0b10000101, 0b01001011,
    ]))
    mc = bs.read_modular_chars()
    assert mc == 112823273
    mc = bs.read_modular_chars()
    assert mc == 4610
    mc = bs.read_modular_chars()
    assert mc == -1413


def test_read_modular_shorts():
    bs = BitStream(bytes([
        0b00110001, 0b11110100, 0b10001101, 0b00000000,
    ]))
    ms = bs.read_modular_shorts()
    assert ms == 4650033


if __name__ == '__main__':
    pytest.main([__file__])
