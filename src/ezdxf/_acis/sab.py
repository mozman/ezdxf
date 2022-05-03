#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import NamedTuple, Any, Sequence, List, Iterator
from datetime import datetime
import struct
from ezdxf._acis.const import ParsingError, DATE_FMT, Tags
from ezdxf._acis.hdr import AcisHeader


class Token(NamedTuple):
    tag: int
    value: Any


class Decoder:
    def __init__(self, data: bytes):
        self.data = data
        self.index: int = 0

    def read_header(self) -> AcisHeader:
        header = AcisHeader()
        signature = self.data[0:15]
        if signature != b"ACIS BinaryFile":
            raise ParsingError("not a SAB file")
        self.index = 15

        header.version = self.read_int()
        header.n_records = self.read_int()
        header.n_entities = self.read_int()
        header.flags = self.read_int()
        header.product_id = self.read_str_tag()
        header.acis_version = self.read_str_tag()
        date = self.read_str_tag()
        header.creation_date = datetime.strptime(date, DATE_FMT)
        header.units_in_mm = self.read_double_tag()
        # tolerances are ignored
        _ = self.read_double_tag()  # res_tol
        _ = self.read_double_tag()  # nor_tol
        return header

    def forward(self, count: int):
        pos = self.index
        self.index += count
        return pos

    def read_byte(self) -> int:
        pos = self.forward(1)
        return self.data[pos]

    def read_bytes(self, count: int) -> bytes:
        pos = self.forward(count)
        return self.data[pos : pos + count]

    def read_int(self) -> int:
        pos = self.forward(4)
        values = struct.unpack_from("<i", self.data, pos)[0]
        return values

    def read_float(self) -> float:
        pos = self.forward(8)
        return struct.unpack_from("<d", self.data, pos)[0]

    def read_floats(self, count: int) -> Sequence[float]:
        pos = self.forward(8 * count)
        return struct.unpack_from(f"<{count}d", self.data, pos)

    def read_str(self, length) -> str:
        text = self.read_bytes(length)
        return text.decode()

    def read_str_tag(self) -> str:
        tag = self.read_byte()
        if tag != Tags.STR:
            raise ParsingError("string tag (7) not found")
        return self.read_str(self.read_byte())

    def read_double_tag(self) -> float:
        tag = self.read_byte()
        if tag != Tags.DOUBLE:
            raise ParsingError("double tag (6) not found")
        return self.read_float()

    def read_record(self) -> List[Token]:
        values: List[Token] = []
        entity_type: List[str] = []
        while True:
            tag = self.read_byte()
            if tag == Tags.INT:
                values.append(Token(tag, self.read_int()))
            elif tag == Tags.DOUBLE:
                values.append(Token(tag, self.read_float()))
            elif tag == Tags.STR:
                values.append(Token(tag, self.read_str(self.read_byte())))
            elif tag == Tags.POINTER:
                values.append(Token(tag, self.read_int()))
            elif tag == Tags.BOOL_FALSE:
                values.append(Token(tag, False))
            elif tag == Tags.BOOL_TRUE:
                values.append(Token(tag, True))
            elif tag == Tags.LONG_STR:
                values.append(Token(tag, self.read_str(self.read_int())))
            elif tag == Tags.ENTITY_TYPE_EX:
                entity_type.append(self.read_str(self.read_byte()))
            elif tag == Tags.ENTITY_TYPE:
                entity_type.append(self.read_str(self.read_byte()))
                values.append(Token(tag, "-".join(entity_type)))
            elif tag == Tags.LOCATION_VEC:
                values.append(Token(tag, self.read_floats(3)))
            elif tag == Tags.DIRECTION_VEC:
                values.append(Token(tag, self.read_floats(3)))
            elif tag == Tags.UNKNOWN_0x15:
                values.append(Token(tag, self.read_int()))
            elif tag == Tags.UNKNOWN_0x17:
                values.append(Token(tag, self.read_float()))
            elif tag == Tags.RECORD_END:
                return values
            else:
                raise ParsingError(
                    f"unknown SAB tag: 0x{tag:x} ({tag}) in entity '{values[0].value}'"
                )

    def read_records(self) -> Iterator[List[Token]]:
        while True:
            try:
                yield self.read_record()
            except IndexError:
                return
