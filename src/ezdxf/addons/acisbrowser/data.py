#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import List


class AcisData:
    def __init__(self, name: str = "unknown"):
        self.lines: List[str] = []
        self.name: str = name


class BinaryAcisData(AcisData):
    def __init__(self, data: bytes, name: str):
        super().__init__(name)


class TextAcisData(AcisData):
    def __init__(self, data: List[str], name: str):
        super().__init__(name)
        self.lines = list(data)
