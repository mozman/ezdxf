#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
from typing import Optional, Iterable

from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.tagger import tag_compiler
from ezdxf.tools.rawloader import raw_structure_loader
from ezdxf.tools.difftags import diff_tags, print_diff, OpCode

FILE1 = r"C:\Users\mozman\Desktop\Outbox\906_polylines.dxf"
FILE2 = r"C:\Users\mozman\Desktop\Outbox\906_copy.dxf"


def get_handle(tags: Tags):
    try:
        return tags.get_handle()
    except ValueError:
        return "0"


def cmp_section(sec1, sec2):
    for e1 in sec1:
        handle = get_handle(e1)
        if handle is None or handle == "0":
            continue
        e2 = entity_tags(sec2, handle)
        if e2 is None:
            print(f"entity handle #{handle} not found in second file")
            continue
        e1 = Tags(tag_compiler(iter(e1)))
        a, b = e2, e1
        diff = list(diff_tags(a, b, ndigits=6))
        has_diff = any(op.opcode != OpCode.equal for op in diff)
        if has_diff:
            print("-"*79)
            print(f"comparing {e1.dxftype()}(#{handle})")
            print_diff(a, b, diff)


def cmp_dxf_files(filename1: str, filename2: str):
    doc1 = raw_structure_loader(filename1)
    doc2 = raw_structure_loader(filename2)
    for section in ["TABLES", "BLOCKS", "ENTITIES", "OBJECTS"]:
        cmp_section(doc1[section], doc2[section])


def entity_tags(entities: Iterable[Tags], handle: str) -> Optional[Tags]:
    for e in entities:
        if get_handle(e) == handle:
            return Tags(tag_compiler(iter(e)))
    return None


if __name__ == "__main__":
    cmp_dxf_files(FILE1, FILE2)
