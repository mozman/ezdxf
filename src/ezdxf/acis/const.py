#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import enum

ACIS_VERSION = {
    400: "ACIS 4.00 NT",
    700: "ACIS 32.0 NT",
    20800: "ACIS 208.00 NT",
    21800: "ACIS 218.00 NT",
}
MIN_EXPORT_VERSION = 700
DATE_FMT = "%a %b %d %H:%M:%S %Y"
END_OF_ACIS_DATA_SAT = "End-of-ACIS-data"
END_OF_ACIS_DATA_SAB = b"0x0e03End0x0e02of0x0e04ACIS0x0d04data"
END_OF_ASM_DATA_SAT = "End-of-ASM-data"
END_OF_ASM_DATA_SAB = b"0x0e03End0x0e02of0x0e03ASM0x0d04data"
BEGIN_OF_ACIS_HISTORY_DATA = "Begin-of-ACIS-History-data"
END_OF_ACIS_HISTORY_DATA = "End-of-ACIS-History-data"
DATA_END_MARKERS = (
    END_OF_ACIS_DATA_SAT,
    BEGIN_OF_ACIS_HISTORY_DATA,
    END_OF_ASM_DATA_SAT,
)
NULL_PTR_NAME = "null-ptr"
NONE_ENTITY_NAME = "none-entity"
NOR_TOL = 1e-10
RES_TOL = 9.9999999999999995e-7

BOOL_SPECIFIER = {
    "forward": True,
    "forward_v": True,
    "reversed": False,
    "reversed_v": False,  # ???
    "single": True,
    "double": False,
}

ACIS_SIGNATURE = b"ACIS BinaryFile"  # DXF R2013
ASM_SIGNATURE = b"ASM BinaryFile4"  # DXF R2018
SIGNATURES = [ACIS_SIGNATURE, ASM_SIGNATURE]


def is_valid_export_version(version: int):
    return version >= MIN_EXPORT_VERSION and version in ACIS_VERSION


class Tags(enum.IntEnum):
    NO_TYPE = 0x00
    BYTE = 0x01  # not used in files!
    CHAR = 0x02  # not used in files!
    SHORT = 0x03  # not used in files!
    INT = 0x04  # 32-bit signed integer
    FLOAT = 0x05  # not used in files!
    DOUBLE = 0x06  # 64-bit double precision floating point value
    STR = 0x07  # count is the following 8-bit uchar
    STR2 = 0x08  # not used in files!
    STR3 = 0x09  # not used in files!

    # bool value for reversed, double, I - depends on context
    BOOL_TRUE = 0x0A

    # bool value forward, single, forward_v - depends on context
    BOOL_FALSE = 0x0B
    POINTER = 0x0C
    ENTITY_TYPE = 0x0D
    ENTITY_TYPE_EX = 0x0E
    SUBTYPE_START = 0x0F
    SUBTYPE_END = 0x10
    RECORD_END = 0x11
    LITERAL_STR = 0x12  # count ia a 32-bit uint, see transform entity
    LOCATION_VEC = 0x13  # vector (3 doubles)
    DIRECTION_VEC = 0x14  # vector (3 doubles)

    # Enumeration are stored as strings in SAT and ints in SAB.
    # It's not possible to translate SAT enums (strings) to SAB enums (int) and
    # vice versa without knowing the implementation details. Each enumeration
    # is specific to the class where it is used.
    ENUM = 0x15
    # 0x16: ???
    UNKNOWN_0x17 = 0x17  # double


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


class ExportError(AcisException):
    pass


class EndOfAcisData(AcisException):
    pass


class Features:
    LAW_SPL = 400
    CONE_SCALING = 400
    LOFT_LAW = 400
    REF_MIN_UV_GRID = 400
    VBLEND_AUTO = 400
    BL_ENV_SF = 400
    ELLIPSE_OFFSET = 500
    TOL_MODELING = 500
    APPROX_SUMMARY = 500
    TAPER_SCALING = 500
    LAZY_B_SPLINE = 500
    DM_MULTI_SURF = 500
    GA_COPY_ACTION = 600
    DM_MULTI_SURF_COLOR = 600
    RECAL_SKIN_ERROR = 520
    TAPER_U_RULED = 600
    DM_60 = 600
    LOFT_PCURVE = 600
    EELIST_OWNER = 600
    ANNO_HOOKED = 700
    PATTERN = 700
    ENTITY_TAGS = 700
    AT = 700
    NET_LAW = 700
    STRINGLESS_HISTORY = 700
