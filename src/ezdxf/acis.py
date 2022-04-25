#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import List, Tuple, Union, Sequence, Iterator, Any, Dict
from datetime import datetime
from dataclasses import dataclass, field

__all__ = ["parse_sat", "is_ptr"]

# ACIS versions exported by BricsCAD:
# R2000/AC1015: 400, "ACIS 4.00 NT", text length has no prefix "@"
# R2004/AC1018: 20800 @ "ACIS 208.00 NT", text length has "@" prefix
# R2007/AC1021: 20800 @ "ACIS 208.00 NT", text length has "@" prefix
# R2010/AC1024: 20800 @ "ACIS 208.00 NT", text length has "@" prefix

ACIS_VERSION = {
    400: "ACIS 4.00 NT",
    20800: "ACIS 208.00 NT",
}


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

    def dumps(self) -> str:
        return "\n".join(
            [
                f"{self.version} {self.n_records} {self.n_entities} {self.history_flag} ",
                self._header_str(),
                f"{self.units_in_mm:g} 9.9999999999999995e-007 1e-010",
            ]
        )

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
    def __init__(self, name: str, attr_ptr: str, id_: int, data: Sequence[Any]):
        self.name = name
        self.attr_ptr = attr_ptr
        self.id = id_
        self.data = data


NULL_PTR = AcisEntity("null-ptr", "$-1", -1, tuple())


def is_ptr(s: str) -> bool:
    return len(s) and s[0] == "$"


class AcisTree:
    def __init__(self):
        self.header = AcisHeader()
        self.bodies: List[AcisEntity] = []
        self.entities: Dict[int, AcisEntity] = {}

    def dump_sat(self) -> List[str]:
        return [""]

    def set_entities(self, entities: Dict[int, AcisEntity]) -> None:
        self.bodies = [e for e in entities.values() if e.name == "body"]
        self.entities = entities

    def ptr(self, s: str) -> AcisEntity:
        if is_ptr(s):
            return self.entities[int(s[1:])]
        raise ValueError(f"not a pointer: {s}")


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
        if len(line) == 0:
            continue
        if line.startswith("End-of-ACIS-data") or line.startswith(
            "Begin-of-ACIS-History-Data"
        ):
            break
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
        if first_token.endswith("="):
            num = int(first_token[:-1])
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
    atree.set_entities(entities)
    return atree
