#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import (
    NamedTuple,
    Any,
    Sequence,
    List,
    Iterator,
    Union,
    Iterable,
    cast,
    Tuple,
    TYPE_CHECKING,
)
from datetime import datetime
import struct
from ezdxf._acis.const import (
    ParsingError,
    DATE_FMT,
    Tags,
    DATA_END_MARKERS,
)
from ezdxf._acis.hdr import AcisHeader
from ezdxf._acis.abstract import (
    AbstractEntity,
    DataLoader,
    AbstractBuilder,
    DataExporter,
    EntityExporter,
)
if TYPE_CHECKING:
    from .entities import AcisEntity
    from ezdxf.math import Vec3


class Token(NamedTuple):
    """Named tuple to store tagged value tokens of the SAB format."""

    tag: int
    value: Any

    def __str__(self):
        return f"(0x{self.tag:02x}, {str(self.value)})"


SabRecord = List[Token]


ACIS_SIGNATURE = b"ACIS BinaryFile"  # DXF R2013
ASM_SIGNATURE = b"ASM BinaryFile4"  # DXF R2018
SIGNATURES = [ACIS_SIGNATURE, ASM_SIGNATURE]


class Decoder:
    def __init__(self, data: bytes):
        self.data = data
        self.index: int = 0

    @property
    def has_data(self) -> bool:
        return self.index < len(self.data)

    def read_header(self) -> AcisHeader:
        header = AcisHeader()
        for signature in SIGNATURES:
            if self.data.startswith(signature):
                self.index = len(signature)
                break
        else:
            raise ParsingError("not a SAB file")
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

    def read_record(self) -> SabRecord:
        def entity_name():
            return "-".join(entity_type)

        values: SabRecord = []
        entity_type: List[str] = []
        subtype_level: int = 0
        while True:
            if not self.has_data:
                if values:
                    token = values[0]
                    if token.value in DATA_END_MARKERS:
                        return values
                raise ParsingError("pre-mature end of data")
            tag = self.read_byte()
            if tag == Tags.INT:
                values.append(Token(tag, self.read_int()))
            elif tag == Tags.DOUBLE:
                values.append(Token(tag, self.read_float()))
            elif tag == Tags.STR:
                values.append(Token(tag, self.read_str(self.read_byte())))
            elif tag == Tags.POINTER:
                values.append(Token(tag, self.read_int()))
            elif tag == Tags.BOOL_TRUE:
                values.append(Token(tag, True))
            elif tag == Tags.BOOL_FALSE:
                values.append(Token(tag, False))
            elif tag == Tags.LITERAL_STR:
                values.append(Token(tag, self.read_str(self.read_int())))
            elif tag == Tags.ENTITY_TYPE_EX:
                entity_type.append(self.read_str(self.read_byte()))
            elif tag == Tags.ENTITY_TYPE:
                entity_type.append(self.read_str(self.read_byte()))
                values.append(Token(tag, entity_name()))
                entity_type.clear()
            elif tag == Tags.LOCATION_VEC:
                values.append(Token(tag, self.read_floats(3)))
            elif tag == Tags.DIRECTION_VEC:
                values.append(Token(tag, self.read_floats(3)))
            elif tag == Tags.ENUM:
                values.append(Token(tag, self.read_int()))
            elif tag == Tags.UNKNOWN_0x17:
                values.append(Token(tag, self.read_float()))
            elif tag == Tags.SUBTYPE_START:
                subtype_level += 1
                values.append(Token(tag, subtype_level))
            elif tag == Tags.SUBTYPE_END:
                values.append(Token(tag, subtype_level))
                subtype_level -= 1
            elif tag == Tags.RECORD_END:
                return values
            else:
                raise ParsingError(
                    f"unknown SAB tag: 0x{tag:x} ({tag}) in entity '{values[0].value}'"
                )

    def read_records(self) -> Iterator[SabRecord]:
        while True:
            try:
                if self.has_data:
                    yield self.read_record()
                else:
                    return
            except IndexError:
                return


class SabEntity(AbstractEntity):
    """Low level representation of an ACIS entity (node)."""

    def __init__(
        self,
        name: str,
        attr_ptr: int = -1,
        id: int = -1,
        data: SabRecord = None,
    ):
        self.name = name
        self.attr_ptr = attr_ptr
        self.id = id
        self.data: SabRecord = data if data is not None else []
        self.attributes: "SabEntity" = None  # type: ignore

    def __str__(self):
        return f"{self.name}({self.id})"


NULL_PTR = SabEntity("null-ptr", -1, -1, tuple())  # type: ignore


class SabDataLoader(DataLoader):
    def __init__(self, data: SabRecord, version: int):
        self.version = version
        self.data = data
        self.index = 0

    def has_data(self) -> bool:
        return self.index <= len(self.data)

    def read_int(self, skip_sat: int = None) -> int:
        token = self.data[self.index]
        if token.tag == Tags.INT:
            self.index += 1
            return cast(int, token.value)
        raise ParsingError(f"expected int token, got {token}")

    def read_double(self) -> float:
        token = self.data[self.index]
        if token.tag == Tags.DOUBLE:
            self.index += 1
            return cast(float, token.value)
        raise ParsingError(f"expected double token, got {token}")

    def read_interval(self) -> float:
        finite = self.read_bool("F", "I")
        if finite:
            return self.read_double()
        return float("inf")

    def read_vec3(self) -> Tuple[float, float, float]:
        token = self.data[self.index]
        if token.tag in (Tags.LOCATION_VEC, Tags.DIRECTION_VEC):
            self.index += 1
            return cast(Tuple[float, float, float], token.value)
        raise ParsingError(f"expected vector token, got {token}")

    def read_bool(self, true: str, false: str) -> bool:
        token = self.data[self.index]
        if token.tag == Tags.BOOL_TRUE:
            self.index += 1
            return True
        elif token.tag == Tags.BOOL_FALSE:
            self.index += 1
            return False
        raise ParsingError(f"expected bool token, got {token}")

    def read_str(self) -> str:
        token = self.data[self.index]
        if token.tag in (Tags.STR, Tags.LITERAL_STR):
            self.index += 1
            return cast(str, token.value)
        raise ParsingError(f"expected str token, got {token}")

    def read_ptr(self) -> AbstractEntity:
        token = self.data[self.index]
        if token.tag == Tags.POINTER:
            self.index += 1
            return cast(AbstractEntity, token.value)
        raise ParsingError(f"expected pointer token, got {token}")


class SabBuilder(AbstractBuilder):
    """Low level data structure to manage ACIS SAB data files."""

    def __init__(self):
        self.header = AcisHeader()
        self.bodies: List[SabEntity] = []
        self.entities: List[SabEntity] = []

    def dump_sab(self) -> bytearray:
        """Returns the SAB representation of the ACIS file as bytearray."""
        self.reorder_records()
        self.header.n_entities = len(self.bodies)
        self.header.n_records = 0  # is always 0

        return bytearray(b"")

    def set_entities(self, entities: List[SabEntity]) -> None:
        """Reset entities and bodies list. (internal API)"""
        self.bodies = [e for e in entities if e.name == "body"]
        self.entities = entities


class SabExporter(EntityExporter[SabEntity]):
    def make_record(self, entity: AcisEntity) -> SabEntity:
        record = SabEntity(entity.type, id=entity.id)
        self.exported_entities[id(entity)] = record
        return record

    def export(self, entity: AcisEntity) -> SabEntity:
        try:
            return self.exported_entities[id(entity)]
        except KeyError:
            pass
        record = self.make_record(entity)
        if not entity.attributes.is_none:
            record.attributes = self.export(entity.attributes)
        entity.export(SabDataExporter(self, record.data))
        return record

    def dump_sab(self) -> bytearray:
        builder = SabBuilder()
        builder.header = self.header
        builder.set_entities(list(self.exported_entities.values()))
        return builder.dump_sab()


def build_entities(
    records: Iterable[SabRecord], version: int
) -> Iterator[SabEntity]:
    for record in records:
        name = record[0].value
        if name in DATA_END_MARKERS:
            yield SabEntity(name)
            return
        attr = record[1].value
        id_ = -1
        if version >= 700:
            id_ = record[2].value
            data = record[3:]
        else:
            data = record[2:]
        yield SabEntity(name, attr, id_, data)


def resolve_pointers(entities: List[SabEntity]) -> List[SabEntity]:
    def ptr(num: int) -> SabEntity:
        if num == -1:
            return NULL_PTR
        return entities[num]

    for entity in entities:
        entity.attributes = ptr(entity.attr_ptr)
        entity.attr_ptr = -1
        for index, token in enumerate(entity.data):
            if token.tag == Tags.POINTER:
                entity.data[index] = Token(token.tag, ptr(token.value))
    return entities


def parse_sab(b: Union[bytes, bytearray, Sequence[bytes]]) -> SabBuilder:
    """Returns the :class:`SabBuilder` for the ACIS :term:`SAB` file content
    given as string or list of strings.

    Raises:
        ParsingError: invalid or unsupported ACIS data structure

    """
    data: bytes
    if isinstance(b, (bytes, bytearray)):
        data = b
    else:
        data = b"".join(b)
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("expected bytes, bytearray or a sequence of bytes")
    builder = SabBuilder()
    decoder = Decoder(data)
    builder.header = decoder.read_header()
    entities = list(
        build_entities(decoder.read_records(), builder.header.version)
    )
    builder.set_entities(resolve_pointers(entities))
    return builder


class SabDataExporter(DataExporter):
    def __init__(self, exporter: SabExporter, data: SabRecord):
        self.version = exporter.version
        self.exporter = exporter
        self.data = data

    def write_int(self, value: int, skip_sat=False) -> None:
        """There are sometimes additional int values in SAB files which are
        not present in SAT files, maybe reference counters e.g. vertex, coedge.
        """
        pass

    def write_double(self, value: float) -> None:
        pass

    def write_interval(self, value: float) -> None:
        pass

    def write_vec3(self, value: Vec3) -> None:
        pass

    def write_bool(self, value: bool, true: str, false: str) -> None:
        pass

    def write_str(self, value: str) -> None:
        pass

    def write_literal_str(self, value: str) -> None:
        pass

    def write_ptr(self, value: AcisEntity) -> None:
        pass
