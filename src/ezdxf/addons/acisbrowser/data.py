#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import List, Iterator

from ezdxf.acis.sab import parse_sab


class AcisData:
    def __init__(self, name: str = "unknown", handle: str = ""):
        self.lines: List[str] = []
        self.name: str = name
        self.handle: str = handle


class BinaryAcisData(AcisData):
    def __init__(self, data: bytes, name: str, handle: str):
        super().__init__(name, handle)
        self.lines = list(make_sab_records(data))


class TextAcisData(AcisData):
    def __init__(self, data: List[str], name: str, handle: str):
        super().__init__(name, handle)
        self.lines = list(data)


def make_sab_records(data: bytes) -> Iterator[str]:
    builder = parse_sab(data)
    builder.reset_ids()
    for entity in builder.entities:
        content = [str(entity)]
        content.append(str(entity.attributes))
        for tag in entity.data:
            content.append(str(tag.value))
        yield " ".join(content)
