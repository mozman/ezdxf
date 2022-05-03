#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import enum

ACIS_VERSION = {
    400: "ACIS 4.00 NT",
    700: "ACIS 32.0 NT",
    20800: "ACIS 208.00 NT",
}

DATE_FMT = "%a %b %d %H:%M:%S %Y"
END_OF_ACIS_DATA = "End-of-ACIS-data"
BEGIN_OF_ACIS_HISTORY_DATA = "Begin-of-ACIS-History-Data"
END_OF_ACIS_HISTORY_DATA = "End-of-ACIS-History-Data"
DATA_END_MARKERS = (END_OF_ACIS_DATA, BEGIN_OF_ACIS_HISTORY_DATA)


class Tags(enum.IntEnum):
    INT = 0x04
    DOUBLE = 0x06
    STR = 0x07
    BOOL_FALSE = 0x0A  # reversed, double - meaning depends on context
    BOOL_TRUE = 0x0B  # forward, single, forward_v, I - meaning depends on context
    POINTER = 0x0C
    ENTITY_TYPE = 0x0D
    ENTITY_TYPE_EX = 0x0E
    RECORD_END = 0x11
    LONG_STR = 0x12  # following int4 = count ? see transform
    LOCATION_VEC = 0x13  # vector (3 doubles)
    DIRECTION_VEC = 0x14  # vector (3 doubles)
    UNKNOWN = 0x15

# entity type structure:
# 0x0D 0x04 (char count of) "body" = SAT "body"
# 0x0E 0x05 "plane" 0x0D 0x07 "surface" = SAT "plane-surface"
# 0x0E 0x06 "ref_vt" 0x0E 0x03 "eye" 0x0D 0x06 "attrib" = SAT "ref_vt-eye-attrib"


class Flags(enum.IntFlag):
    HAS_HISTORY = 1


class AcisException(Exception):
    pass


class InvalidLinkStructure(AcisException):
    pass


class ParsingError(AcisException):
    pass


class EndOfAcisData(AcisException):
    pass
