#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import List, Tuple, Union, Sequence


__all__ = ["parse_sat", "new_tree"]


class AcisHeader:
    pass


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
