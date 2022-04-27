#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import List, Tuple, Union, Sequence, Iterator, Any, Dict
from datetime import datetime
from dataclasses import dataclass, field
from ezdxf._acis.const import *

# ACIS versions exported by BricsCAD:
# R2000/AC1015: 400, "ACIS 4.00 NT", text length has no prefix "@"
# R2004/AC1018: 20800 @ "ACIS 208.00 NT", text length has "@" prefix ??? wierd
# R2007/AC1021: 700 @ "ACIS 32.0 NT", text length has "@" prefix
# R2010/AC1024: 700 @ "ACIS 32.0 NT", text length has "@" prefix

# A test showed that R2000 files that contains ACIS v700/32.0 or v20800/208.0
# data can be opened by Autodesk TrueView, BricsCAD and Allplan, so exporting
# only v700/32.0 for all DXF versions should be OK!
# test script: exploration/acis/transplant_acis_data.py


@dataclass
class AcisHeader:
    """Represents an ACIS file header."""

    version: int = 400
    n_records: int = 0  # can be 0
    n_entities: int = 0
    flags: int = 0
    product_id: str = "ezdxf ACIS Builder"
    acis_version: str = ACIS_VERSION[400]
    creation_date: datetime = field(default_factory=datetime.now)
    units_in_mm: float = 1.0

    def dumps(self) -> List[str]:
        """Returns the file header as list of strings."""
        return [
            f"{self.version} {self.n_records} {self.n_entities} {self.flags} ",
            self._header_str(),
            f"{self.units_in_mm:g} 9.9999999999999995e-007 1e-010 ",
        ]

    def _header_str(self) -> str:
        p_len = len(self.product_id)
        a_len = len(self.acis_version)
        date = self.creation_date.ctime()
        if self.version > 400:
            return f"@{p_len} {self.product_id} @{a_len} {self.acis_version} @{len(date)} {date} "
        else:
            return f"{p_len} {self.product_id} {a_len} {self.acis_version} {len(date)} {date} "

    def set_version(self, version: int) -> None:
        """Sets the ACIS version as an integer value and updates the version
        string accordingly.
        """
        try:
            self.acis_version = ACIS_VERSION[version]
            self.version = version
        except KeyError:
            raise ValueError(f"invalid ACIS version number {version}")


@dataclass
class RawRecord:
    num: int
    tokens: List[str]


class AcisEntity:
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
        self.attributes: "AcisEntity" = None  # type: ignore

    def __str__(self):
        return f"{self.name}({self.id})"

    def find_all(self, entity_type: str) -> List["AcisEntity"]:
        """Returns a list of all matching ACIS entities of then given type
        referenced by this entity.

        Args:
            entity_type: entity type (name) as string like "body"

        """
        return [
            e
            for e in self.data
            if isinstance(e, AcisEntity) and e.name == entity_type
        ]

    def find_first(self, entity_type: str) -> "AcisEntity":
        """Returns the first matching ACIS entity referenced by this entity.
        Returns the ``NULL_PTR`` if no entity was found.

        Args:
            entity_type: entity type (name) as string like "body"

        """
        for token in self.data:
            if isinstance(token, AcisEntity) and token.name == entity_type:
                return token
        return NULL_PTR

    def find_path(self, path: str) -> "AcisEntity":
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

    def find_entities(self, names: str) -> List["AcisEntity"]:
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
        if isinstance(field, AcisEntity):
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


NULL_PTR = AcisEntity("null-ptr", "$-1", -1, tuple())  # type: ignore


def new_acis_entity(
    name: str,
    attributes=NULL_PTR,
    id=-1,
    data: List[Any] = None,
) -> AcisEntity:
    """Factory to create new ACIS entities.

    Args:
        name: entity type
        attributes: referenece to the entity attributes or :attr:`NULL_PTR`.
        id: unique entity id as integer or -1
        data: generic data container as list

    """
    e = AcisEntity(name, "$-1", id, data)
    e.attributes = attributes
    return e


def is_ptr(s: str) -> bool:
    """Returns ``True`` if the string `s` represents an entity pointer."""
    return len(s) > 0 and s[0] == "$"


class AcisBuilder:
    """Low level data structure to manage ACIS data files."""

    def __init__(self):
        self.header = AcisHeader()
        self.bodies: List[AcisEntity] = []
        self.entities: List[AcisEntity] = []

    def dump_sat(self) -> List[str]:
        """Returns the text representation of the ACIS file as list of strings
        without line endings.

        Raise:
            InvalidLinkStructure: referenced ACIS entity is not stored in
                the :attr:`entities` storage

        """
        data = self.header.dumps()
        data.extend(build_str_records(self.entities, self.header.version))
        data.append("End-of-ACIS-data ")
        return data

    def set_entities(self, entities: List[AcisEntity]) -> None:
        """Reset entities and bodies list. (internal API)"""
        self.bodies = [e for e in entities if e.name == "body"]
        self.entities = entities

    def query(self, func=lambda e: True) -> Iterator[AcisEntity]:
        """Yields all entities as :class:`AcisEntity` for which the given
        function returns ``True`` e.g. query all "point" entities::

            points = list(acis_builder.query(lambda e: e.name == "point"))

        """
        return filter(func, self.entities)


def build_str_records(
    entities: List[AcisEntity], version: int
) -> Iterator[str]:
    def ptr_str(e: AcisEntity) -> str:
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
            if isinstance(data, AcisEntity):
                tokens.append(ptr_str(data))
            else:
                tokens.append(str(data))
        tokens.append("#")
        yield " ".join(tokens)


def resolve_str_pointers(entities: Dict[int, AcisEntity]) -> List[AcisEntity]:
    def ptr(s: str) -> AcisEntity:
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


def parse_sat_header(data: Sequence[str]) -> Tuple[AcisHeader, Sequence[str]]:
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
            header.creation_date = datetime.strptime(
                tokens[2], "%a %b %d %H:%M:%S %Y"
            )
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
        if line.startswith("End-of-ACIS-data") or line.startswith(
            "Begin-of-ACIS-History-Data"
        ):
            return
        yield line


def merge_record_strings(data: Sequence[str]) -> Iterator[str]:
    # Found special cases:
    # ...  copy @7 bdm_uid 55 #torus-surface $-1 -1 $-1  ...
    # in a single line!
    current_line = ""
    for line in _filter_records(data):
        current_line += line
        if current_line[-1] == "#":
            yield current_line
            current_line = ""
        elif current_line[-1] != " ":
            current_line += " "


def parse_records(data: Sequence[str]) -> List[RawRecord]:
    num = 0
    records: List[RawRecord] = []
    for line in merge_record_strings(data):
        tokens = line.split()
        first_token = tokens[0].strip()
        if first_token.startswith("-"):
            num = -int(first_token)
            tokens.pop(0)
        # remove end of record marker "#"
        if "#" in tokens[-1]:
            tokens.pop()
        records.append(RawRecord(num, tokens))
        num += 1
    return records


def build_entities(
    records: Sequence[RawRecord], version: int
) -> Dict[int, AcisEntity]:
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
        entities[record.num] = AcisEntity(name, attr, id_, data)
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
    header, data = parse_sat_header(data)
    atree.header = header
    records = parse_records(data)
    entities = build_entities(records, header.version)
    atree.set_entities(resolve_str_pointers(entities))
    return atree
