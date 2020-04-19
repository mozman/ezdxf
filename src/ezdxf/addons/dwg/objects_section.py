# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import Dict, Iterable, Tuple
import struct

from ezdxf.tools.binarydata import BitStream
from .const import *
from .fileheader import FileHeader
from .header_section import DwgSectionLoader
from .crc import crc8


class ObjectsMapR2000(DwgSectionLoader):
    def load_data_section(self, data: Bytes) -> Bytes:
        if self.specs.version > ACAD_2000:
            raise DwgVersionError(self.specs.version)
        seeker, section_size = self.specs.sections[OBJECTS_ID]
        return data[seeker:seeker + section_size]

    def handles(self) -> Iterable[Tuple[str, int]]:
        section_start = 0
        handle = 0
        location = 0
        # Big endian order!
        size = struct.unpack_from('>H', self.data, section_start)[0]
        # size includes 2 bytes for size itself!
        while size != 2:
            end_of_data = section_start + size
            bs = BitStream(self.data[section_start+2: section_start + size])
            while bs.has_data:
                handle += bs.read_unsigned_modular_chars()
                location += bs.read_signed_modular_chars()
                # R2000: location is absolute file location
                # R2004+ : location is relative to AcDb:Objects logical section
                # starting with offset 0 at the beginning of this logical section.
                yield f'{handle:X}', location

            if self.crc_check:
                # Big endian!
                check = struct.unpack_from('>H', self.data, end_of_data)[0]
                crc = crc8(self.data[section_start: end_of_data], seed=0xc0c1)
                if check != crc:
                    raise CRCError('CRC error in objects map section.')
            section_start = end_of_data + 2  # crc
            # Big endian order!
            size = struct.unpack_from('>H', self.data, section_start)[0]


class ObjectsMapR2004(ObjectsMapR2000):
    def load_data(self, data: Bytes) -> Bytes:
        raise NotImplementedError()


def load_objects_map(specs: FileHeader, data: Bytes, crc_check=False):
    if specs.version <= ACAD_2000:
        return ObjectsMapR2000(specs, data, crc_check)
    else:
        return ObjectsMapR2004(specs, data, crc_check)
