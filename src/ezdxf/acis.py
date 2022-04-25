#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import List, Tuple, Union, Sequence
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
                f"{int(self.units_in_mm)} 9.9999999999999995e-007 1e-010",
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

    def set_header(self, header: AcisHeader) -> None:
        self.header = header

    def dump_sat(self) -> List[str]:
        return [""]


def new_tree() -> AcisTree:
    return AcisTree()


def parse_sat_header(data: Sequence[str]) -> Tuple[AcisHeader, Sequence[str]]:
    return AcisHeader(), data


def parse_sat(s: Union[str, Sequence[str]]) -> AcisTree:
    if isinstance(s, str):
        data = s.splitlines()
    else:
        data = s
    if not isinstance(data, Sequence):
        raise TypeError("expected as string or a sequence of strings")
    atree = AcisTree()
    header, data = parse_sat_header(data)
    atree.set_header(header)
    return atree
