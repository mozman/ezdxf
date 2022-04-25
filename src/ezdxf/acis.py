#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import List, Tuple, Union, Sequence, Iterator, Any, Dict
from datetime import datetime
from dataclasses import dataclass, field

__all__ = ["parse_sat", "is_ptr", "new_acis_entity"]

# ACIS versions exported by BricsCAD:
# R2000/AC1015: 400, "ACIS 4.00 NT", text length has no prefix "@"
# R2004/AC1018: 20800 @ "ACIS 208.00 NT", text length has "@" prefix
# R2007/AC1021: 20800 @ "ACIS 208.00 NT", text length has "@" prefix
# R2010/AC1024: 20800 @ "ACIS 208.00 NT", text length has "@" prefix

ACIS_VERSION = {
    400: "ACIS 4.00 NT",
    20800: "ACIS 208.00 NT",
}


class AcisException(Exception):
    pass


class InvalidACISLinkStructure(AcisException):
    pass


class EntityParsingError(AcisException):
    pass


@dataclass
class AcisHeader:
    version: int = 400
    n_records: int = 0  # can be 0
    n_entities: int = 0
    history_flag: int = 0  # 1 if history has been saved
    product_id: str = "ezdxf ACIS Builder"
    acis_version: str = ACIS_VERSION[400]
    creation_date: datetime = field(default_factory=datetime.now)
    units_in_mm: float = 1.0

    def dumps(self) -> List[str]:
        return [
            f"{self.version} {self.n_records} {self.n_entities} {self.history_flag} ",
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
        try:
            self.acis_version = ACIS_VERSION[version]
            self.version = version
        except KeyError:
            raise ValueError(f"invalid ACIS version number {version}")


@dataclass
class Record:
    num: int
    tokens: List[str]


class AcisEntity:
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

    def find_all(self, entity_type) -> Iterator["AcisEntity"]:
        for token in self.data:
            if isinstance(token, AcisEntity) and token.name == entity_type:
                yield token

    def find_first(self, entity_type) -> "AcisEntity":
        for token in self.data:
            if isinstance(token, AcisEntity) and token.name == entity_type:
                return token
        return NULL_PTR

    def find_path(self, path: str) -> "AcisEntity":
        entity = self
        for entity_type in path.split("/"):
            entity = entity.find_first(entity_type)
        return entity

    def parse_data(self, fmt: str) -> Sequence[Any]:
        content = []
        next_is_user_string = False
        fields = fmt.split(";")
        fields.reverse()
        for token in self.data:
            if next_is_user_string:
                content.append(token)
                next_is_user_string = False
                continue
            if isinstance(token, AcisEntity):
                if fields[-1] == token.name:
                    content.append(token)
                    fields.pop()
                # ignore entity if do not match expected types
            else:
                expected = fields.pop()
                if expected == "f":  # float
                    if token == "I":  # infinity
                        token = "inf"
                    try:
                        content.append(float(token))
                    except ValueError:
                        raise EntityParsingError(f"expected a float: '{token}' in {self.name}")
                elif expected == "i":  # integer
                    try:
                        content.append(int(token))
                    except ValueError:
                        raise EntityParsingError(f"expected an int: '{token}' in {self.name}")
                elif expected == "s":  # string const like forward and reversed
                    content.append(token)
                elif expected == "@":  # user string with length encoding
                    next_is_user_string = True
                    # ignor length encoding
                    continue
                elif expected == "?":  # skip unknown field
                    pass
                else:
                    raise ValueError(f"expected field '{expected}' not found")
            if len(fields) == 0:
                break
        return content


NULL_PTR = AcisEntity("null-ptr", "$-1", -1, tuple())  # type: ignore


def new_acis_entity(
    name: str,
    attributes=NULL_PTR,
    id=-1,
    data: List[Any] = None,
) -> AcisEntity:
    e = AcisEntity(name, "$-1", id, data)
    e.attributes = attributes
    return e


def is_ptr(s: str) -> bool:
    return len(s) > 0 and s[0] == "$"


class AcisTree:
    def __init__(self):
        self.header = AcisHeader()
        self.bodies: List[AcisEntity] = []
        self.entities: List[AcisEntity] = []

    def dump_sat(self) -> List[str]:
        data = self.header.dumps()
        data.extend(build_str_records(self.entities, self.header.version))
        data.append("End-of-ACIS-data ")
        return data

    def set_entities(self, entities: List[AcisEntity]) -> None:
        self.bodies = [e for e in entities if e.name == "body"]
        self.entities = entities

    def query(self, func=lambda e: True) -> Iterator[AcisEntity]:
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
            raise InvalidACISLinkStructure(
                f"entity {str(e)} not in record storage"
            )

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


def _parse_header_str(s: str) -> Iterator[str]:
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
        header.history_flag = int(tokens[3])
    except (IndexError, ValueError):
        pass
    tokens = list(_parse_header_str(data[1]))
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


def _merge_record_strings(data: Sequence[str]) -> Iterator[str]:
    current_line = ""
    for line in data:
        if line.startswith("End-of-ACIS-data") or line.startswith(
            "Begin-of-ACIS-History-Data"
        ):
            return
        current_line += line
        if current_line[-1] == "#":
            yield current_line
            current_line = ""
        elif current_line[-1] != " ":
            current_line += " "


def parse_records(data: Sequence[str]) -> List[Record]:
    num = 0
    records: List[Record] = []
    for line in _merge_record_strings(data):
        tokens = line.split()
        first_token = tokens[0].strip()
        if first_token.startswith("-"):
            num = -int(first_token)
            tokens.pop(0)
        # remove end of record marker "#"
        records.append(Record(num, tokens[:-1]))
        num += 1
    return records


def build_entities(
    records: Sequence[Record], version: int
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


def parse_sat(s: Union[str, Sequence[str]]) -> AcisTree:
    data: Sequence[str]
    if isinstance(s, str):
        data = s.splitlines()
    else:
        data = s
    if not isinstance(data, Sequence):
        raise TypeError("expected as string or a sequence of strings")
    atree = AcisTree()
    header, data = parse_sat_header(data)
    atree.header = header
    records = parse_records(data)
    entities = build_entities(records, header.version)
    atree.set_entities(resolve_str_pointers(entities))
    return atree
