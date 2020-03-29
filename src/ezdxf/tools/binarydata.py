# Created: 03.05.2014
# Copyright (c) 2014-2020, Manfred Moitzi
# License: MIT License
import sys
from typing import Iterable, Any
from array import array
import struct


def hex_strings_to_bytes(data: Iterable[str]) -> bytes:
    """ Returns multiple hex strings `data` as bytes. """
    byte_array = array('B')
    for hexstr in data:
        byte_array.extend(int(hexstr[index:index + 2], 16) for index in range(0, len(hexstr), 2))
    return byte_array.tobytes()


def hexstr_to_bytes(data: str) -> bytes:
    """ Returns hex string `data` as bytes. """
    byte_array = array('B', (int(data[index:index + 2], 16) for index in range(0, len(data), 2)))
    return byte_array.tobytes()


def int_to_hexstr(data: int) -> str:
    """ Returns integer `data` as plain hex string. """
    return "%0.2X" % data


def bytes_to_hexstr(data: bytes) -> str:
    """ Returns `data` bytes as plain hex string. """
    return ''.join(int_to_hexstr(byte) for byte in data)


NULL_NULL = b'\x00\x00'


class EndOfBufferError(EOFError):
    pass


class ByteStream:
    """ Process little endian binary data organized as bytes, data is padded to 4 byte boundaries by default.
    """

    # Created for Proxy Entity Graphic decoding
    def __init__(self, buffer: bytes, align: int = 4):
        self.buffer: bytes = buffer
        self.index: int = 0
        self._not_native_little_endian: bool = sys.byteorder != 'little'
        self._align: int = align

    @property
    def has_data(self) -> bool:
        return self.index < len(self.buffer)

    def align(self, index: int) -> int:
        modulo = index % self._align
        return index + self._align - modulo if modulo else index

    def read_struct(self, fmt: str) -> Any:
        """ Read data defined by a struct format string. Insert little endian format character '<' as
        first character, if machine has native big endian byte order.
        """
        if not self.has_data:
            raise EndOfBufferError('Unexpected end of buffer.')

        if self._not_native_little_endian:
            fmt = '<' + fmt

        result = struct.unpack_from(fmt, self.buffer, offset=self.index)
        self.index = self.align(self.index + struct.calcsize(fmt))
        return result

    def read_float(self):
        return self.read_struct('d')[0]

    def read_vertex(self):
        return self.read_struct('3d')

    def read_padded_string(self, encoding: str = 'utf_8') -> str:
        """ PS: Padded String. This is a string, terminated with a zero byte. The file’s text encoding (code page)
        is used to encode/decode the bytes into a string.
        """
        buffer = self.buffer
        for end_index in range(self.index, len(buffer)):
            if buffer[end_index] == 0:
                start_index = self.index
                self.index = self.align(end_index + 1)
                return buffer[start_index:end_index].decode(encoding)
        raise EndOfBufferError('Unexpected end of buffer, did not detect terminating zero byte.')

    def read_padded_unicode_string(self) -> str:
        """ PUS: Padded Unicode String. The bytes are encoded using Unicode encoding. The bytes consist of
        byte pairs and the string is terminated by 2 zero bytes.
        """
        buffer = self.buffer
        for end_index in range(self.index, len(buffer), 2):
            if buffer[end_index:end_index + 2] == NULL_NULL:
                start_index = self.index
                self.index = self.align(end_index + 2)
                return buffer[start_index:end_index].decode('utf_16_le')
        raise EndOfBufferError('Unexpected end of buffer, did not detect terminating zero bytes.')
