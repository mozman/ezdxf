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
