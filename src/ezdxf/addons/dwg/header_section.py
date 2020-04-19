# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import Dict
from abc import abstractmethod
import struct

from ezdxf.tools.binarydata import BitStream

from .const import *
from .crc import crc8
from .fileheader import FileHeader
from .header_parser import parse_header


def load_header_section(specs: FileHeader, data: Bytes, crc_check=False):
    if specs.version <= ACAD_2000:
        return DwgHeaderSectionR2000(specs, data, crc_check)
    else:
        return DwgHeaderSectionR2004(specs, data, crc_check)


class DwgSectionLoader:
    def __init__(self, specs: FileHeader, data: Bytes, crc_check=False):
        self.specs = specs
        self.crc_check = crc_check
        self.data = self.load_data_section(data)

    @abstractmethod
    def load_data_section(self, data: Bytes) -> Bytes:
        ...


class DwgHeaderSectionR2000(DwgSectionLoader):
    def load_data_section(self, data: Bytes) -> Bytes:
        if self.specs.version > ACAD_2000:
            raise DwgVersionError(self.specs.version)
        seeker, section_size = self.specs.sections[HEADER_ID]
        return data[seeker:seeker + section_size]

    def load_header_vars(self) -> Dict:
        data = self.data
        sentinel = data[:16]
        if sentinel != b'\xCF\x7B\x1F\x23\xFD\xDE\x38\xA9\x5F\x7C\x68\xB8\x4E\x6D\x33\x5F':
            raise DwgCorruptedHeaderSection('Sentinel for start of HEADER section not found.')
        index = 16
        size = struct.unpack_from('<L', data, index)[0]
        index += 4
        bs = BitStream(data[index: index + size], dxfversion=self.specs.version, encoding=self.specs.encoding)
        hdr_vars = parse_header(bs)
        index += size
        if self.crc_check:
            check = struct.unpack_from('<H', data, index)[0]
            # CRC of data from end of sentinel until start of crc value
            crc = crc8(data[16:-18], seed=0xc0c1)
            if check != crc:
                raise CRCError('CRC error in header section.')
        sentinel = data[-16:]
        if sentinel != b'\x30\x84\xE0\xDC\x02\x21\xC7\x56\xA0\x83\x97\x47\xB1\x92\xCC\xA0':
            raise DwgCorruptedHeaderSection('Sentinel for end of HEADER section not found.')
        return hdr_vars


class DwgHeaderSectionR2004(DwgHeaderSectionR2000):
    def load_data(self, data: Bytes) -> Bytes:
        raise NotImplementedError()
