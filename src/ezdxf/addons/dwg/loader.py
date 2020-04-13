# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
# Created: 2020-04-01
from typing import Dict
import struct

from ezdxf.lldxf.loader import SectionDict
from ezdxf.lldxf.types import DXFTag, DXFVertex, DXFBinaryTag
from ezdxf.lldxf.tags import Tags
from ezdxf.drawing import Drawing
from ezdxf.tools.binarydata import BitStream

from .const import *

__all__ = ['readfile', 'load', 'Document', 'FileHeader']


def readfile(filename: str) -> 'Drawing':
    data = open(filename, 'rb').read()
    return load(data)


def load(data: bytes) -> Drawing:
    doc = Document(data)
    doc.load()
    return Drawing.from_section_dict(doc.sections)


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


class FileHeader:
    def __init__(self, data: bytes):
        if len(data) < 6:
            raise DwgVersionError('Not a DWG file.')
        ver = data[:6].decode(errors='ignore')
        if ver not in SUPPORTED_VERSIONS:
            raise DwgVersionError(f'Not a DWG file or unsupported DWG version, signature: {ver}.')
        self.version: str = ver
        self.encoding: str = 'cp1252'
        self.sections = dict()

        if self.version in [ACAD_13, ACAD_14, ACAD_2000]:
            self.acad_13_14_15(data)

    def acad_13_14_15(self, data: bytes):
        codepage: int = struct.unpack_from('<h', data, 0x13)[0]
        self.encoding = codepage_to_encoding.get(codepage, 'cp1252')
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
        # skip crc
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


class Document:
    def __init__(self, data: bytes):
        self.data: bytes = data
        self.specs = FileHeader(data)
        # Store DXF object types by class number (500+):
        self.dxf_object_types: Dict[int, str] = dict()
        self.sections: SectionDict = {
            'HEADER': [
                Tags([
                    DXFTag(0, 'SECTION'),
                    DXFTag(2, 'HEADER'),
                ])
            ],
            'CLASSES': [
                Tags([
                    DXFTag(0, 'SECTION'),
                    DXFTag(2, 'CLASSES'),
                ])
            ],
            'TABLES': [
                Tags([
                    DXFTag(0, 'SECTION'),
                    DXFTag(2, 'TABLES'),
                ])
            ],
            'BLOCKS': [
                Tags([
                    DXFTag(0, 'SECTION'),
                    DXFTag(2, 'BLOCKS'),
                ])
            ],
            'ENTITIES': [
                Tags([
                    DXFTag(0, 'SECTION'),
                    DXFTag(2, 'ENTITIES'),
                ])
            ],
            'OBJECTS': [
                Tags([
                    DXFTag(0, 'SECTION'),
                    DXFTag(2, 'OBJECTS'),
                ])
            ],
        }

    def load(self):
        self.load_header()
        self.load_classes()
        self.load_objects()

    def load_header(self) -> None:
        pass

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
            raise DwgCorruptedClassesSection('Sentinel for start of section not found.')

        cls_tag = DXFTag(0, 'CLASS')
        classes = self.sections['CLASSES']
        bs = BitStream(
            self.data[seeker + SENTINEL_SIZE: seeker + section_size],
            dxfversion=self.specs.version,
            encoding=self.specs.encoding,
        )
        class_data_size = bs.read_unsigned_long()  # data size in bytes
        end_index = (3 + class_data_size) << 3

        while bs.bit_index < end_index:
            class_num = bs.read_bit_short()
            flags = bs.read_bit_short()  # version?
            app_name = bs.read_text()
            cpp_class_name = bs.read_text()
            class_dxf_name = bs.read_text()
            was_a_zombie = bs.read_bit()
            item_class_id = bs.read_bit_short()
            # print((class_num, flags, app_name, class_dxf_name, cpp_class_name, was_a_zombie, item_class_id))
            classes.append(Tags([
                cls_tag,
                DXFTag(1, class_dxf_name),
                DXFTag(2, cpp_class_name),
                DXFTag(3, app_name),
                DXFTag(90, flags),
                DXFTag(280, was_a_zombie),
                DXFTag(281, 1 if item_class_id == 0x1f2 else 0)
            ]))
            self.dxf_object_types[class_num] = class_dxf_name

        # Ignore crc for the sake of speed.
        # _index = index + (20 + class_data_size)
        # crc = struct.unpack_from('<h', self.data, index)
        _index = seeker + (SENTINEL_SIZE + 6 + class_data_size)
        sentinel = self.data[_index: _index + SENTINEL_SIZE]
        if sentinel != b'\x72\x5E\x3B\x47\x3B\x56\x07\x3A\x3F\x23\x0B\xA0\x18\x30\x49\x75':
            raise DwgCorruptedClassesSection('Sentinel for end of section not found.')

    def classes_R2004(self) -> None:
        pass
