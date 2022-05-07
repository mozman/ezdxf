#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import List, Any, Sequence, Iterator, Tuple, Union
from datetime import datetime
from ezdxf._acis import const
from ezdxf._acis.const import ParsingError, InvalidLinkStructure
from ezdxf._acis.hdr import AcisHeader
from ezdxf._acis.abstract import AbstractEntity, AbstractBuilder, DataLoader

SatRecord = List[str]


class SatEntity(AbstractEntity):
    """Low level representation of an ACIS entity (node)."""

    def __init__(
        self,
        name: str,
        attr_ptr: str = "$-1",
        id: int = -1,
        data: List[Any] = None,
    ):
        self.name = name
        self.attr_ptr = attr_ptr
        self.id = id
        self.data: List[Any] = data if data is not None else []
        self.attributes: "SatEntity" = None  # type: ignore

    def __str__(self):
        return f"{self.name}({self.id})"

    def find_all(self, entity_type: str) -> List["SatEntity"]:
        """Returns a list of all matching ACIS entities of then given type
        referenced by this entity.

        Args:
            entity_type: entity type (name) as string like "body"

        """
        return [
            e
            for e in self.data
            if isinstance(e, SatEntity) and e.name == entity_type
        ]

    def find_first(self, entity_type: str) -> "SatEntity":
        """Returns the first matching ACIS entity referenced by this entity.
        Returns the ``NULL_PTR`` if no entity was found.

        Args:
            entity_type: entity type (name) as string like "body"

        """
        for token in self.data:
            if isinstance(token, SatEntity) and token.name == entity_type:
                return token
        return NULL_PTR

    def parse_values(self, fmt: str) -> Sequence[Any]:
        """Parse only values from entity data, ignores all entities in front
        or between the data values.

        =========== ==============================
        specifier   data type
        =========== ==============================
        ``f``       float values
        ``i``       integer values
        ``b``       boolean values like "forward", "reversed", ...
        ``@``       user string with preceding length encoding
        ``?``       skip (unknown) value
        =========== ==============================

        Args:
            fmt: format specifiers separated by ";"

        """
        return parse_values(self.data, fmt)


def parse_values(data: Sequence[Any], fmt: str) -> Sequence[Any]:
    """Parse only values from entity data, ignores all entities."""
    content = []
    next_is_user_string = False
    specifiers = fmt.split(";")
    specifiers.reverse()
    vector: List[float] = []
    for field in data:
        if isinstance(field, SatEntity):
            next_is_user_string = False
            continue  # ignore all entities

        if next_is_user_string:
            content.append(field)
            next_is_user_string = False
            continue

        if len(specifiers) == 0:
            break
        specifier = specifiers.pop()
        if specifier == "v":  # 3x float
            vector.append(float(field))
            if len(vector) == 3:
                content.append(tuple(vector))
                vector.clear()
            else:
                specifiers.append(specifier)
        elif specifier == "f":  # float
            if field == "I":  # infinity
                field = "inf"
            try:
                content.append(float(field))
            except ValueError:
                raise ParsingError(f"expected a float: '{field}'")
        elif specifier == "i":  # integer
            try:
                content.append(int(field))
            except ValueError:
                raise ParsingError(f"expected an int: '{field}'")
        elif specifier == "b":
            # boolean string specifier like "forward" and "reversed"
            try:
                content.append(const.BOOL_SPECIFIER[field])
            except KeyError:
                raise ParsingError(
                    f"unknown boolean string specifier: '{field}'"
                )
        elif specifier == "@":  # user string with length encoding
            next_is_user_string = True
            # ignor length encoding
            continue
        elif specifier == "?":  # skip value field
            pass
        else:
            raise ParsingError(f"unknown format specifier: {specifier}")
    return content


NULL_PTR = SatEntity("null-ptr", "$-1", -1, tuple())  # type: ignore


def new_entity(
    name: str,
    attributes=NULL_PTR,
    id=-1,
    data: List[Any] = None,
) -> SatEntity:
    """Factory to create new ACIS entities.

    Args:
        name: entity type
        attributes: reference to the entity attributes or :attr:`NULL_PTR`.
        id: unique entity id as integer or -1
        data: generic data container as list

    """
    e = SatEntity(name, "$-1", id, data)
    e.attributes = attributes
    return e


def is_ptr(s: str) -> bool:
    """Returns ``True`` if the string `s` represents an entity pointer."""
    return len(s) > 0 and s[0] == "$"


def resolve_str_pointers(entities: List[SatEntity]) -> List[SatEntity]:
    def ptr(s: str) -> SatEntity:
        num = int(s[1:])
        if num == -1:
            return NULL_PTR
        return entities[num]

    for entity in entities:
        entity.attributes = ptr(entity.attr_ptr)
        entity.attr_ptr = "$-1"
        data = []
        for token in entity.data:
            if is_ptr(token):
                data.append(ptr(token))
            else:
                data.append(token)
        entity.data = data
    return entities


class SatDataLoader(DataLoader):
    def __init__(self, data: List[Any], version: int):
        self.version = version
        self.data = data
        self.index = 0

    def has_data(self) -> bool:
        return self.index <= len(self.data)

    def read_int(self) -> int:
        entry = self.data[self.index]
        try:
            value = int(entry)
        except ValueError:
            raise ParsingError(f"expected integer, got {entry}")
        self.index += 1
        return value

    def read_double(self) -> float:
        entry = self.data[self.index]
        if entry == "I":
            return float("inf")
        try:
            value = float(entry)
        except ValueError:
            raise ParsingError(f"expected double, got {entry}")
        self.index += 1
        return value

    def read_vec3(self) -> Tuple[float, float, float]:
        x = self.read_double()
        y = self.read_double()
        z = self.read_double()
        return x, y, z

    def read_bool(self, true: str, false: str) -> bool:
        value = self.data[self.index]
        if value == true:
            self.index += 1
            return True
        elif value == false:
            self.index += 1
            return False
        raise ParsingError(
            f"expected bool string '{true}' or '{false}', got {value}"
        )

    def read_str(self) -> str:
        value = self.data[self.index]
        if self.version < const.Features.AT or value.startswith("@"):
            self.index += 2
            return self.data[self.index-1]
        raise ParsingError(f"expected string, got {value}")

    def read_ptr(self) -> AbstractEntity:
        entity = self.data[self.index]
        if isinstance(entity, AbstractEntity):
            self.index += 1
            return entity
        raise ParsingError(f"expected pointer, got {type(entity)}")


class SatBuilder(AbstractBuilder):
    """Low level data structure to manage ACIS SAT data files."""

    def __init__(self):
        self.header = AcisHeader()
        self.bodies: List[SatEntity] = []
        self.entities: List[SatEntity] = []

    def dump_sat(self) -> List[str]:
        """Returns the text representation of the ACIS file as list of strings
        without line endings.

        Raise:
            InvalidLinkStructure: referenced ACIS entity is not stored in
                the :attr:`entities` storage

        """
        data = self.header.dumps()
        data.extend(build_str_records(self.entities, self.header.version))
        data.append(const.END_OF_ACIS_DATA + " ")
        return data

    def set_entities(self, entities: List[SatEntity]) -> None:
        """Reset entities and bodies list. (internal API)"""
        self.bodies = [e for e in entities if e.name == "body"]
        self.entities = entities


def build_str_records(entities: List[SatEntity], version: int) -> Iterator[str]:
    def ptr_str(e: SatEntity) -> str:
        if e is NULL_PTR:
            return "$-1"
        try:
            return f"${entities.index(e)}"
        except ValueError:
            raise InvalidLinkStructure(f"entity {str(e)} not in record storage")

    for entity in entities:
        tokens = [entity.name]
        tokens.append(ptr_str(entity.attributes))
        if version >= 700:
            tokens.append(str(entity.id))
        for data in entity.data:
            if isinstance(data, SatEntity):
                tokens.append(ptr_str(data))
            else:
                tokens.append(str(data))
        tokens.append("#")
        yield " ".join(tokens)


def parse_header_str(s: str) -> Iterator[str]:
    num = ""
    collect = 0
    token = ""
    for c in s.rstrip():
        if collect > 0:
            token += c
            collect -= 1
            if collect == 0:
                yield token
                token = ""
        elif c == "@":
            continue
        elif c in "0123456789":
            num += c
        elif c == " " and num:
            collect = int(num)
            num = ""


def parse_header(data: Sequence[str]) -> Tuple[AcisHeader, Sequence[str]]:
    header = AcisHeader()
    tokens = data[0].split()
    header.version = int(tokens[0])
    try:
        header.n_records = int(tokens[1])
        header.n_entities = int(tokens[2])
        header.flags = int(tokens[3])
    except (IndexError, ValueError):
        pass
    tokens = list(parse_header_str(data[1]))
    try:
        header.product_id = tokens[0]
        header.acis_version = tokens[1]
    except IndexError:
        pass

    if len(tokens) > 2:
        try:  # Sat Jan  1 10:00:00 2022
            header.creation_date = datetime.strptime(tokens[2], const.DATE_FMT)
        except ValueError:
            pass
    tokens = data[2].split()
    try:
        header.units_in_mm = float(tokens[0])
    except (IndexError, ValueError):
        pass
    return header, data[3:]


def _filter_records(data: Sequence[str]) -> Iterator[str]:
    for line in data:
        if line.startswith(const.END_OF_ACIS_DATA) or line.startswith(
            const.BEGIN_OF_ACIS_HISTORY_DATA
        ):
            return
        yield line


def merge_record_strings(data: Sequence[str]) -> Iterator[str]:
    merged_data = " ".join(_filter_records(data))
    for record in merged_data.split("#"):
        record = record.strip()
        if record:
            yield record


def parse_records(data: Sequence[str]) -> List[SatRecord]:
    expected_seq_num = 0
    records: List[SatRecord] = []
    for line in merge_record_strings(data):
        tokens: SatRecord = line.split()
        first_token = tokens[0].strip()
        if first_token.startswith("-"):
            num = -int(first_token)
            if num != expected_seq_num:
                raise ParsingError(
                    "non-continuous sequence numbers not supported"
                )
            tokens.pop(0)
        records.append(tokens)
        expected_seq_num += 1
    return records


def build_entities(
    records: Sequence[SatRecord], version: int
) -> List[SatEntity]:
    entities: List[SatEntity] = []
    for record in records:
        name = record[0]
        attr = record[1]
        id_ = -1
        if version >= 700:
            id_ = int(record[2])
            data = record[3:]
        else:
            data = record[2:]
        entities.append(SatEntity(name, attr, id_, data))
    return entities


def parse_sat(s: Union[str, Sequence[str]]) -> SatBuilder:
    """Returns the :class:`SatBuilder` for the ACIS SAT file content given as
    string or list of strings.

    Raises:
        ParsingError: invalid or unsupported ACIS data structure

    """
    data: Sequence[str]
    if isinstance(s, str):
        data = s.splitlines()
    else:
        data = s
    if not isinstance(data, Sequence):
        raise TypeError("expected as string or a sequence of strings")
    builder = SatBuilder()
    header, data = parse_header(data)
    builder.header = header
    records = parse_records(data)
    entities = build_entities(records, header.version)
    builder.set_entities(resolve_str_pointers(entities))
    return builder
