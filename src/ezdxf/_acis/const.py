#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import enum

ACIS_VERSION = {
    400: "ACIS 4.00 NT",
    700: "ACIS 32.0 NT",
    20800: "ACIS 208.00 NT",
}


class Flags(enum.IntFlag):
    HAS_HISTORY = 1


class AcisException(Exception):
    pass


class InvalidLinkStructure(AcisException):
    pass


class ParsingError(AcisException):
    pass
