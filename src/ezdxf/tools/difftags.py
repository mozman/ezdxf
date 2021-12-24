#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Tuple, Iterator
from difflib import SequenceMatcher
import enum
from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.types import DXFVertex, DXFTag

__all__ = ["diff_tags", "OpCode"]

# https://docs.python.org/3/library/difflib.html


class OpCode(enum.Enum):
    replace = enum.auto()
    delete = enum.auto()
    insert = enum.auto()
    equal = enum.auto()


Operation = Tuple[OpCode, int, int, int, int]

CONVERT = {
    "replace": OpCode.replace,
    "delete": OpCode.delete,
    "insert": OpCode.insert,
    "equal": OpCode.equal,
}


def convert_opcodes(opcodes) -> Iterator[Operation]:
    for tag, i1, i2, j1, j2 in opcodes:
        yield CONVERT[tag], i1, i2, j1, j2


def round_tags(tags: Tags, ndigits: int) -> Iterator[DXFTag]:
    for tag in tags:
        if isinstance(tag, DXFVertex):
            yield DXFVertex(tag.code, (round(d, ndigits) for d in tag.value))
        elif isinstance(tag.value, float):
            yield DXFTag(tag.code, round(tag.value, ndigits))  # type: ignore
        else:
            yield tag


def diff_tags(a: Tags, b: Tags, ndigits: int = None) -> Iterator[Operation]:
    if ndigits is not None:
        a = Tags(round_tags(a, ndigits))
        b = Tags(round_tags(b, ndigits))

    sequencer = SequenceMatcher(a=a, b=b)
    return convert_opcodes(sequencer.get_opcodes())
