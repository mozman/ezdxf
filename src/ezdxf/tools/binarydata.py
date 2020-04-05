# Created: 03.05.2014
# Copyright (c) 2014-2020, Manfred Moitzi
# License: MIT License
import sys
from typing import Iterable, Any, Sequence, Union, Tuple
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

    def read_long(self):
        return self.read_struct('L')[0]

    def read_signed_long(self):
        return self.read_struct('l')[0]

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


class BitStream:
    """ Process little endian binary data organized as bit stream. """

    # Created for DWG bit stream decoding
    def __init__(self, buffer: bytes, dxfversion='AC1015', encoding='cp1252'):
        self.buffer: bytes = buffer
        self.bit_index: int = 0
        self.dxfversion = dxfversion
        self.encoding = encoding

    @property
    def has_data(self) -> bool:
        return self.bit_index >> 3 < len(self.buffer)

    def align(self, count=4) -> int:
        """ Align to byte border. """
        byte_index = self.bit_index >> 3
        modulo = byte_index % count
        if modulo:
            byte_index += count - modulo
        return byte_index << 3

    def read_bit(self) -> int:
        """ Read one bit from buffer. """
        index = self.bit_index
        self.bit_index += 1
        try:
            return 1 if self.buffer[index >> 3] & (0x80 >> (index & 7)) else 0
        except IndexError:
            raise EndOfBufferError('Unexpected end of buffer.')

    def read_bits(self, count) -> int:
        """ Read `count` bits from buffer. """
        index = self.bit_index
        buffer = self.buffer
        next_bit_index = index + count  # index of next bit after reading `count` bits

        if (next_bit_index - 1) >> 3 > len(buffer):  # not enough data to read all bits
            raise EndOfBufferError('Unexpected end of buffer.')
        self.bit_index = next_bit_index

        test_bit = 0x80 >> (index & 7)
        test_byte_index = index >> 3
        value = 0
        test_byte = buffer[test_byte_index]
        while count > 0:
            value <<= 1
            if test_byte & test_bit:
                value |= 1
            count -= 1
            test_bit >>= 1
            if not test_bit and count:
                test_bit = 0x80
                test_byte_index += 1
                test_byte = buffer[test_byte_index]
        return value

    def read_unsigned_byte(self) -> int:
        """ Read an unsigned byte (8 bit) from buffer. """
        return self.read_bits(8)

    def read_signed_byte(self) -> int:
        """ Read a signed byte (8 bit) from buffer. """
        value = self.read_bits(8)
        if value & 0x80:
            # 2er complement
            return -((~value & 0xff) + 1)

    def read_aligned_bytes(self, count: int) -> Sequence[int]:
        buffer = self.buffer
        start_index = self.bit_index >> 3
        end_index = start_index + count
        if end_index <= len(buffer):
            self.bit_index += count << 3
            return buffer[start_index: end_index]
        else:
            raise EndOfBufferError('Unexpected end of buffer.')

    def read_unsigned_short(self) -> int:
        """ Read an unsigned short (16 bit) from buffer. """
        if self.bit_index & 7:
            s1 = self.read_bits(8)
            s2 = self.read_bits(8)
        else:  # aligned data
            s1, s2 = self.read_aligned_bytes(2)
        return (s2 << 8) + s1

    def read_signed_short(self) -> int:
        """ Read a signed short (16 bit) from buffer. """
        value = self.read_unsigned_short()
        if value & 0x8000:
            # 2er complement
            return -((~value & 0xffff) + 1)

    def read_unsigned_long(self) -> int:
        """ Read an unsigned long (32 bit) from buffer. """
        if self.bit_index & 7:
            read_bits = self.read_bits
            l1 = read_bits(8)
            l2 = read_bits(8)
            l3 = read_bits(8)
            l4 = read_bits(8)
        else:  # aligned data
            l1, l2, l3, l4 = self.read_aligned_bytes(4)
        return (l4 << 24) + (l3 << 16) + (l2 << 8) + l1

    def read_signed_long(self) -> int:
        """ Read a signed long (32 bit) from buffer. """
        value = self.read_unsigned_long()
        if value & 0x80000000:
            # 2er complement
            return -((~value & 0xffffffff) + 1)

    def read_float(self) -> float:
        if self.bit_index & 7:
            read_bits = self.read_bits
            data = bytes(read_bits(8) for _ in range(8))
        else:  # aligned data
            data = bytes(self.read_aligned_bytes(8))
        return struct.unpack('<d', data)[0]

    def read_3_bits(self) -> int:
        bit = self.read_bit()
        if bit:  # 1
            bit = self.read_bit()
            if bit:  # 11
                bit = self.read_bit()
                if bit:
                    return 7  # 111
                else:
                    return 6  # 110
            return 2  # 10
        else:
            return 0  # 0

    def read_bit_short(self, count=1) -> Union[int, Sequence[int]]:
        def _read():
            bits = self.read_bits(2)
            if bits == 0:
                return self.read_signed_short()
            elif bits == 1:
                return self.read_unsigned_byte()
            elif bits == 2:
                return 0
            else:
                return 256

        if count == 1:
            return _read()
        else:
            return tuple(_read() for _ in range(count))

    def read_bit_long(self, count: int = 1) -> Union[int, Sequence[int]]:
        def _read():
            bits = self.read_bits(2)
            if bits == 0:
                return self.read_signed_long()
            elif bits == 1:
                return self.read_unsigned_byte()
            elif bits == 2:
                return 0
            else:  # not used!
                return 256  # ???

        if count == 1:
            return _read()
        else:
            return tuple(_read() for _ in range(count))

    def read_raw_double(self, count: int = 1) -> Union[float, Sequence[float]]:
        if count == 1:
            return self.read_float()
        else:
            return tuple(self.read_float() for _ in range(count))

    def read_bit_double(self, count: int = 1) -> Union[float, Sequence[float]]:
        def _read():
            bits = self.read_bits(2)
            if bits == 0:
                return self.read_float()
            elif bits == 1:
                return 1.0
            elif bits == 2:
                return 0.0
            else:  # not used!
                return 0.0

        if count == 1:
            return _read()
        else:
            return tuple(_read() for _ in range(count))

    def read_bit_double_default(self, count: int = 1, default=0.0) -> Union[float, Sequence[float]]:
        data = struct.pack('<d', default)

        def _read():
            bits = self.read_bits(2)
            if bits == 0:
                return default
            elif bits == 1:
                _data = bytes(self.read_unsigned_byte() for _ in range(4)) + data[4:]
                return struct.unpack('<d', _data)
            elif bits == 2:
                _data = bytearray(data)
                _data[4] = self.read_unsigned_byte()
                _data[5] = self.read_unsigned_byte()
                _data[0] = self.read_unsigned_byte()
                _data[1] = self.read_unsigned_byte()
                _data[2] = self.read_unsigned_byte()
                _data[3] = self.read_unsigned_byte()
                return struct.unpack('<d', _data)
            else:
                return self.read_float()

        if count == 1:
            return _read()
        else:
            return tuple(_read() for _ in range(count))

    def read_bit_extrusion(self) -> Tuple[float, float, float]:
        if self.read_bit():
            return 0.0, 0.0, 1.0
        else:
            return self.read_bit_double(3)

    def read_bit_thickness(self, dxfversion='AC1015') -> float:
        if dxfversion >= 'AC1015':
            if self.read_bit():
                return 0.0
        return self.read_bit_double()

    def read_cm_color(self) -> int:
        return self.read_bit_short()

    def read_text(self) -> str:
        length = self.read_bit_short()
        data = bytes(self.read_unsigned_byte() for _ in range(length))
        return data.decode(encoding=self.encoding)

    def read_text_unicode(self) -> str:
        # Unicode text is read from the "string stream" within the object data,
        # see the main Object description section for details.
        length = self.read_bit_short()
        data = bytes(self.read_unsigned_byte() for _ in range(length * 2))
        return data.decode(encoding='utf16')

    def read_text_variable(self) -> str:
        if self.dxfversion < 'AC1018':  # R2004
            return self.read_text()
        else:
            return self.read_text_unicode()

    def read_cm_color_cms(self) -> Tuple[int, str, str]:
        _ = self.read_bit_short()  # index always 0
        color_name = ''
        book_name = ''
        rgb = self.read_bit_long()
        rc = self.read_unsigned_byte()
        if rc & 1:
            color_name = self.read_text_variable()
        if rc & 2:
            book_name = self.read_text_variable()
        return rgb, color_name, book_name

    def read_cm_color_enc(self):
        flags_and_index = self.read_bit_short()
        flags = flags_and_index >> 8
        index = flags_and_index & 0xff
        if flags:
            rgb = None
            color_handle = None
            transparency_type = None
            transparency = None
            if flags & 0x80:
                rgb = self.read_bit_short() & 0x00ffffff
            if flags & 0x40:
                color_handle = self.read_handle()
            if flags & 0x20:
                data = self.read_bit_long()
                transparency_type = data >> 24
                transparency = data & 0xff
            return rgb, color_handle, transparency_type, transparency
        else:
            return index

    def read_handle(self, reference=0) -> Tuple[int, int]:
        code = self.read_bits(4)
        counter = self.read_bits(4)
        if code < 6:
            handle = 0
            while counter:
                handle = handle << 8 + self.read_unsigned_byte()
                counter -= 1
            return code, handle
        elif code == 6:
            return code, reference + 1
        elif code == 7:
            return code, reference - 1
        else:
            offset = 0
            while counter:
                offset = offset << 8 + self.read_unsigned_byte()
                counter -= 1
            if code == 10:
                return code, reference + offset
            if code == 12:
                return code, reference - offset
