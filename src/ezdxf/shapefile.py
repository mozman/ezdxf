#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

"""
This module provides support for fonts stored as SHX and SHP files.
(SHP is not the GIS file format!)

The documentation about the SHP file format can be found at Autodesk:
https://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-DE941DB5-7044-433C-AA68-2A9AE98A5713

"""
from typing import Dict, Sequence, Iterable, Iterator
import enum


class ShapeFileException(Exception):
    pass


class UnsupportedShapeFile(ShapeFileException):
    pass


class InvalidFontDefinition(ShapeFileException):
    pass


class InvalidShapeRecord(ShapeFileException):
    pass


class FileStructureError(ShapeFileException):
    pass


class FontEmbedding(enum.IntEnum):
    ALLOWED = 0
    DISALLOWED = 1
    READONLY = 2


class FontEncoding(enum.IntEnum):
    UNICODE = 0
    PACKED_MULTIBYTE_1 = 1
    SHAPE_FILE = 2


class FontMode(enum.IntEnum):
    HORIZONTAL = 0
    VERTICAL = 2


class Symbol:
    def __init__(self, number: int, name: str):
        self.number = number
        self.name = name
        self.data: Sequence[int] = []


class ShapeFile:
    def __init__(
        self,
        name: str,
        size: int,
        above: int,
        below: int,
        mode=FontMode.HORIZONTAL,
        encoding=FontEncoding.UNICODE,
        embed=FontEmbedding.ALLOWED,
    ):
        self.symbols: Dict[int, Symbol] = dict()
        self.name = name
        self.size = size
        self.above = above
        self.below = below
        self.mode = mode
        self.encoding = encoding
        self.embed = embed

    @staticmethod
    def from_str_record(record: Sequence[str]):
        if len(record) == 2:
            try:
                spec, size, name = record[0].split(",")
            except ValueError:
                raise InvalidFontDefinition()
            assert spec == "*UNIFONT"

            try:
                above, below, mode, encoding, embed, end = record[1].split(",")
            except ValueError:
                raise InvalidFontDefinition()
            assert int(end) == 0

            return ShapeFile(
                name,
                int(size),
                int(above),
                int(below),
                FontMode(int(mode)),
                FontEncoding(int(encoding)),
                FontEmbedding(int(embed)),
            )

    def parse_str_records(self, records: Iterable[Sequence[str]]) -> None:
        for record in records:
            if len(record) < 2:
                raise InvalidShapeRecord()
            # ignore second value: defbytes
            number, _, name = split_record(record[0])
            int_num = int(number[1:], 16)
            symbol = Symbol(int_num, name)
            data = "".join(record[1:])
            symbol.data = tuple(parse_codes(split_record(data)))
            if symbol.data[-1] == 0:
                self.symbols[int_num] = symbol
            else:
                raise FileStructureError(
                    f"file structure error at symbol <{record[0]}>"
                )


def split_record(record: str) -> Sequence[str]:
    return tuple(s.strip() for s in record.split(","))


def parse_codes(codes: Iterable[str]) -> Iterator[int]:
    for code in codes:
        code = code.strip("()")
        yield int(code, 16)


def shp_loads(data: str) -> ShapeFile:
    records = _parse_string_records(data)
    try:
        font_definition = records.pop("*UNIFONT")
    except KeyError:
        raise UnsupportedShapeFile()
    shp = ShapeFile.from_str_record(font_definition)
    shp.parse_str_records(records.values())
    return shp


def shp_dumps(shapefile: ShapeFile) -> str:
    return ""


def shx_loadb(data: bytes) -> ShapeFile:
    return ShapeFile("", 0, 0, 0)


def shx_dumpb(shapefile: ShapeFile) -> bytes:
    return b""


def _parse_string_records(data: str) -> Dict[str, Sequence[str]]:
    records: Dict[str, Sequence[str]] = dict()
    name = None
    lines = []
    for line in _filter_comments(data.split("\n")):
        if line.startswith("*"):
            if name is not None:
                records[name] = tuple(lines)
            name = line.split(",")[0].strip()
            lines = [line]
        else:
            lines.append(line)

    if name is not None:
        records[name] = tuple(lines)
    return records


def _filter_comments(lines: Iterable[str]) -> Iterator[str]:
    for line in lines:
        line = line.strip()
        line = line.split(";")[0]
        if line:
            yield line
