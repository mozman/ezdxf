#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from dataclasses import dataclass
from typing import List, Any, Sequence, Dict, Iterator, Tuple, Union
from datetime import datetime
from ezdxf._acis.const import *
from ezdxf._acis.hdr import AcisHeader


@dataclass
class SatRecord:
    num: int
    tokens: List[str]


class SatEntity:
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

    def find_path(self, path: str) -> "SatEntity":
        """Returns the last ACIS entity referenced by an `path`.
        The `path` describes the path to the entity starting form the current
        entity like "lump/shell/face". This is equivalent to::

            face = entity.find_first("lump").find_first("shell").find_first("face")

        Returns ``NULL_PTR`` if no entity could be found or if the path is
        invalid.

        Args:
            path: entity types divided by "/" like "lump/shell/face"

        """
        entity = self
        for entity_type in path.split("/"):
            entity = entity.find_first(entity_type)
        return entity

    def find_entities(self, names: str) -> List["SatEntity"]:
        """Find multiple entities of different types. Returns the first
        entity of each type. If a type doesn't exist a ``NULL_PTR`` is
        returned for this type::

            coedge, edge = coedge.find_entities("coedge;edge")

        Returns the first coedge and the first edge in the current coedge.
        If no edge entity exist, the edge variable is the ``NULL_PTR``.

        Args:
            names: entity type list as string, separator is ";"

        """
        return [self.find_first(name) for name in names.split(";")]

    def parse_values(self, fmt: str) -> Sequence[Any]:
        """Parse only values from entity data, ignores all entities in front
        or between the data values.

        =========== ==============================
        specifier   data type
        =========== ==============================
        ``f``       float values
        ``i``       integer values
        ``s``       string constants like "forward"
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
        if specifier == "f":  # float
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
        elif specifier == "s":  # string const like forward and reversed
            content.append(field)
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


def new_acis_entity(
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


def resolve_str_pointers(entities: Dict[int, SatEntity]) -> List[SatEntity]:
    def ptr(s: str) -> SatEntity:
        if is_ptr(s):
            num = int(s[1:])
            if num == -1:
                return NULL_PTR
            return entities[num]
        raise ValueError(f"not a pointer: {s}")

    for entity in entities.values():
        entity.attributes = ptr(entity.attr_ptr)
        entity.attr_ptr = "$-1"
        data = []
        for token in entity.data:
            if is_ptr(token):
                data.append(ptr(token))
            else:
                data.append(token)
        entity.data = data
    return [e for _, e in sorted(entities.items())]


class AcisBuilder:
    """Low level data structure to manage ACIS data files."""

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
        data.append(END_OF_ACIS_DATA + " ")
        return data

    def set_entities(self, entities: List[SatEntity]) -> None:
        """Reset entities and bodies list. (internal API)"""
        self.bodies = [e for e in entities if e.name == "body"]
        self.entities = entities

    def query(self, func=lambda e: True) -> Iterator[SatEntity]:
        """Yields all entities as :class:`RawEntity` for which the given
        function returns ``True`` e.g. query all "point" entities::

            points = list(acis_builder.query(lambda e: e.name == "point"))

        """
        return filter(func, self.entities)


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
            header.creation_date = datetime.strptime(tokens[2], DATE_FMT)
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
        if line.startswith(END_OF_ACIS_DATA) or line.startswith(
            BEGIN_OF_ACIS_HISTORY_DATA
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
    num = 0
    records: List[SatRecord] = []
    for line in merge_record_strings(data):
        tokens = line.split()
        first_token = tokens[0].strip()
        if first_token.startswith("-"):
            num = -int(first_token)
            tokens.pop(0)
        records.append(SatRecord(num, tokens))
        num += 1
    return records


def build_entities(
    records: Sequence[SatRecord], version: int
) -> Dict[int, SatEntity]:
    entities = {}
    for record in records:
        name = record.tokens[0]
        attr = record.tokens[1]
        id_ = -1
        if version >= 700:
            id_ = int(record.tokens[2])
            data = record.tokens[3:]
        else:
            data = record.tokens[2:]
        entities[record.num] = SatEntity(name, attr, id_, data)
    return entities


def parse_sat(s: Union[str, Sequence[str]]) -> AcisBuilder:
    """Returns the :class:`AcisBuilder` for the ACIS SAT file content given as
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
    atree = AcisBuilder()
    header, data = parse_header(data)
    atree.header = header
    records = parse_records(data)
    entities = build_entities(records, header.version)
    atree.set_entities(resolve_str_pointers(entities))
    return atree
