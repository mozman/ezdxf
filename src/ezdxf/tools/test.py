#  Copyright (c) 2011-2021, Manfred Moitzi
# License: MIT License
from typing import Sequence, TYPE_CHECKING, Iterable, List, Set
from ezdxf.lldxf.tagger import internal_tag_compiler

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFTag, EntityDB, ExtendedTags, DXFEntity


def compile_tags_without_handles(text: str) -> Iterable["DXFTag"]:
    return (
        tag for tag in internal_tag_compiler(text) if tag.code not in (5, 105)
    )


def normlines(text: str) -> Sequence[str]:
    lines = text.split("\n")
    return [line.strip() for line in lines]


def load_section(text: str, name: str) -> List["ExtendedTags"]:
    from ezdxf.lldxf.loader import load_dxf_structure

    dxf = load_dxf_structure(
        internal_tag_compiler(text), ignore_missing_eof=True
    )
    return dxf[name]  # type: ignore


def load_entities(text: str, name: str):
    from ezdxf.lldxf.loader import load_dxf_structure, load_dxf_entities

    dxf = load_dxf_structure(
        internal_tag_compiler(text), ignore_missing_eof=True
    )
    return load_dxf_entities(dxf[name])  # type: ignore


def parse_hex_dump(txt: str) -> bytes:
    b = bytearray()
    lines = txt.split("\n")
    for line in lines:
        if line == "":
            continue
        data = [int(v, 16) for v in line.strip().split(" ")]
        assert data[0] == len(b)
        b.extend(data[1:])
    return b
