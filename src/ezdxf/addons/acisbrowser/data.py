#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import List, Iterator

from ezdxf.acis.sat import parse_sat
from ezdxf.acis.sab import parse_sab


class AcisData:
    def __init__(self, name: str = "unknown", handle: str = ""):
        self.lines: List[str] = []
        self.name: str = name
        self.handle: str = handle


class BinaryAcisData(AcisData):
    def __init__(self, data: bytes, name: str, handle: str):
        super().__init__(name, handle)


class TextAcisData(AcisData):
    def __init__(self, data: List[str], name: str, handle: str):
        super().__init__(name, handle)
        self.lines = list(data)
