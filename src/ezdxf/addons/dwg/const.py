# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import Union

ACAD_13 = 'AC1012'
ACAD_14 = 'AC1014'
ACAD_2000 = 'AC1015'
ACAD_2004 = 'AC1018'
ACAD_2007 = 'AC1021'
ACAD_2010 = 'AC1024'
ACAD_2013 = 'AC1027'
ACAD_2018 = 'AC1032'
ACAD_LATEST = ACAD_2018

SUPPORTED_VERSIONS = [ACAD_13, ACAD_14, ACAD_2000]
HEADER_ID = 0
CLASSES_ID = 1
OBJECTS_ID = 2
SENTINEL_SIZE = 16

Bytes = Union[bytes, bytearray, memoryview]


class DwgError(Exception):
    pass


class DwgObjectError(DwgError):
    pass


class DwgVersionError(DwgError):
    pass


class DwgCorruptedFileHeader(DwgError):
    pass


class DwgCorruptedClassesSection(DwgError):
    pass


class DwgCorruptedHeaderSection(DwgError):
    pass


class DwgCorruptedTableSection(DwgError):
    pass


class CRCError(DwgError):
    pass


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

DXF_LINE_WIDTH = {
    0: 0,
    1: 5,
    2: 9,
    3: 13,
    4: 15,
    5: 18,
    6: 20,
    7: 25,
    8: 30,
    9: 35,
    10: 40,
    11: 50,
    12: 53,
    13: 60,
    14: 70,
    15: 80,
    16: 90,
    17: 100,
    18: 106,
    19: 120,
    20: 140,
    21: 158,
    22: 200,
    23: 211,
    29: -1,  # BYLAYER
    30: -2,  # BYBLOCK
    31: -3,  # DEFAULT
}
