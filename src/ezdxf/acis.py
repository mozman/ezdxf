#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import List, Tuple, Union, Sequence, Iterator
from datetime import datetime
from dataclasses import dataclass, field

__all__ = ["parse_sat", "new_tree"]

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


class AcisNode:
    pass


class AcisTree(AcisNode):
    def __init__(self):
        self.header = AcisHeader()
        self.bodies: List[AcisNode] = []

    def dump_sat(self) -> List[str]:
        return [""]


def new_tree() -> AcisTree:
    return AcisTree()


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
    return atree
