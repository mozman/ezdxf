# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
# Created: 2020-04-01
from typing import Dict
import struct

from ezdxf.drawing import Drawing
from ezdxf.tools.binarydata import BitStream
from ezdxf.tools import codepage
from ezdxf.sections.headervars import HEADER_VAR_MAP

from ezdxf.sections.header import HeaderSection
from ezdxf.sections.classes import ClassesSection
from ezdxf.sections.tables import TablesSection
from ezdxf.sections.blocks import BlocksSection
from ezdxf.sections.entities import EntitySection
from ezdxf.sections.objects import ObjectsSection
from ezdxf.sections.acdsdata import AcDsDataSection
from ezdxf.entities import DXFClass

from .const import *
from . import header
from .crc import crc8, crc32

__all__ = ['readfile', 'load', 'FileHeader']


def readfile(filename: str) -> 'Drawing':
    data = open(filename, 'rb').read()
    return load(data)


def load(data: bytes) -> Drawing:
    doc = DwgDocument(data)
    return doc.doc


codepage_to_encoding = {
    37: 'cp874',  # Thai,
    38: 'cp932',  # Japanese
    39: 'gbk',  # UnifiedChinese
    40: 'cp949',  # Korean
    41: 'cp950',  # TradChinese
    28: 'cp1250',  # CentralEurope
    29: 'cp1251',  # Cyrillic
    30: 'cp1252',  # WesternEurope
    32: 'cp1253',  # Greek
    33: 'cp1254',  # Turkish
    34: 'cp1255',  # Hebrew
    35: 'cp1256',  # Arabic
    36: 'cp1257',  # Baltic
}

FILE_HEADER_MAGIC = {
    3: 0xa598,
    4: 0x8101,
    5: 0x3cc4,
    6: 0x8461,
}


class FileHeader:
    def __init__(self, data: bytes, crc_check=False):
        self.crc_check = crc_check
        if len(data) < 6:
            raise DwgVersionError('Not a DWG file.')
        ver = data[:6].decode(errors='ignore')
        if ver not in SUPPORTED_VERSIONS:
            raise DwgVersionError(f'Not a DWG file or unsupported DWG version, signature: {ver}.')
        self.version: str = ver
        codepage: int = struct.unpack_from('<h', data, 0x13)[0]
        self.encoding = codepage_to_encoding.get(codepage, 'cp1252')
        self.maintenance_release_version = data[0xB]
        self.sections = dict()
        if self.version in [ACAD_13, ACAD_14, ACAD_2000]:
            self.acad_13_14_15(data)

    def acad_13_14_15(self, data: bytes):
        index = 0x15
        section_count: int = struct.unpack_from('<L', data, index)[0]
        index += 4
        fmt = '<BLL'
        record_size = struct.calcsize(fmt)
        for record in range(section_count):
            # 0: HEADER_ID
            # 1: CLASSES_ID
            # 2: OBJECTS_ID
            num, seeker, size = struct.unpack_from(fmt, data, index)
            index += record_size
            self.sections[num] = (seeker, size)

        if self.crc_check:
            # CRC from first byte of file until start of crc value
            check = crc8(data[:index], seed=0) ^ FILE_HEADER_MAGIC[len(self.sections)]
            crc = struct.unpack_from('<H', data, index)[0]
            if crc != check:
                raise CRCError('CRC error in file header.')

        index += 2
        sentinel = data[index: index + SENTINEL_SIZE]
        if sentinel != b'\x95\xA0\x4E\x28\x99\x82\x1A\xE5\x5E\x41\xE0\x5F\x9D\x3A\x4D\x00':
            raise DwgCorruptedFileHeader('Corrupted DXF R13/14/2000 file header.')

    def print(self):
        print(f'DWG version: {self.version}')
        print(f'encoding: {self.encoding}')
        print(f'Records: {len(self.sections)}')
        print('Header: seeker {0[0]} size: {0[1]}'.format(self.sections[0]))
        print('Classes: seeker {0[0]} size: {0[1]}'.format(self.sections[1]))
        print('Objects: seeker {0[0]} size: {0[1]}'.format(self.sections[2]))


class DwgDocument:
    def __init__(self, data: bytes, crc_check=False):
        self.data: bytes = data
        self.crc_check = crc_check
        self.specs = FileHeader(data, crc_check=crc_check)
        self.doc: Drawing = self._setup_doc()
        # Store DXF object types by class number (500+):
        self.dxf_object_types: Dict[int, str] = dict()

    def _setup_doc(self) -> Drawing:
        doc = Drawing(dxfversion=self.specs.version)
        doc.encoding = self.specs.encoding
        doc.header = HeaderSection.new()

        # Setup basic header variables not stored in the header section of the DWG file.
        doc.header['$ACADVER'] = self.specs.version
        doc.header['$ACADMAINTVER'] = self.specs.maintenance_release_version
        doc.header['$DWGCODEPAGE'] = codepage.tocodepage(self.specs.encoding)

        doc.classes = ClassesSection(doc)
        # doc.tables = TablesSection(doc)
        # doc.blocks = BlocksSection(doc)
        # doc.entities = EntitySection(doc)
        # doc.objects = ObjectsSection(doc)
        # doc.acdsdata = AcDsDataSection(doc)
        return doc

    def load(self):
        self.load_header()
        self.load_classes()
        self.load_objects()

    def load_header(self) -> None:
        hdr_vars = self.load_header_vars()
        self.set_header_vars(hdr_vars)

    def set_header_vars(self, hdr_vars: Dict):
        pass

    def load_header_vars(self) -> Dict:
        data = self.header_data()
        sentinel = data[:16]
        if sentinel != b'\xCF\x7B\x1F\x23\xFD\xDE\x38\xA9\x5F\x7C\x68\xB8\x4E\x6D\x33\x5F':
            raise DwgCorruptedHeaderSection('Sentinel for start of HEADER section not found.')
        index = 16
        size = struct.unpack_from('<L', data, index)[0]
        index += 4
        bs = BitStream(data[index: index + size], dxfversion=self.specs.version, encoding=self.specs.encoding)
        hdr_vars = header.parse(bs)
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

    def header_data(self) -> bytes:
        if self.specs.version <= ACAD_2000:
            seeker, section_size = self.specs.sections[HEADER_ID]
            return self.data[seeker:seeker + section_size]
        else:
            return bytes()

    def load_classes(self) -> None:
        if self.specs.version <= ACAD_2000:
            self.classes_R2000()
        else:
            self.classes_R2004()

    def load_objects(self) -> None:
        pass

    def classes_R2000(self) -> None:
        seeker, section_size = self.specs.sections[CLASSES_ID]
        sentinel = self.data[seeker: seeker + SENTINEL_SIZE]
        if sentinel != b'\x8D\xA1\xC4\xB8\xC4\xA9\xF8\xC5\xC0\xDC\xF4\x5F\xE7\xCF\xB6\x8A':
            raise DwgCorruptedClassesSection('Sentinel for start of CLASSES section not found.')

        bs = BitStream(
            self.data[seeker + SENTINEL_SIZE: seeker + section_size],
            dxfversion=self.specs.version,
            encoding=self.specs.encoding,
        )
        class_data_size = bs.read_unsigned_long()  # data size in bytes
        end_index = (3 + class_data_size) << 3

        while bs.bit_index < end_index:
            class_num = bs.read_bit_short()
            dxfattribs = {
                'flags': bs.read_bit_short(),  # version?
                'app_name': bs.read_text(),
                'cpp_class_name': bs.read_text(),
                'name': bs.read_text(),
                'was_a_proxy': bs.read_bit(),
                'is_an_entity': int(bs.read_bit_short() == 0x1f2),
            }
            dxfclass = DXFClass.new(dxfattribs=dxfattribs)
            self.doc.classes.register(dxfclass)
            self.dxf_object_types[class_num] = dxfclass.dxf.name

        # Ignore crc for the sake of speed.
        # _index = index + (20 + class_data_size)
        # crc = struct.unpack_from('<h', self.data, index)
        _index = seeker + (SENTINEL_SIZE + 6 + class_data_size)
        sentinel = self.data[_index: _index + SENTINEL_SIZE]
        if sentinel != b'\x72\x5E\x3B\x47\x3B\x56\x07\x3A\x3F\x23\x0B\xA0\x18\x30\x49\x75':
            raise DwgCorruptedClassesSection('Sentinel for end of CLASSES section not found.')

    def classes_R2004(self) -> None:
        pass
