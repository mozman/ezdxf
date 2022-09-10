#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Optional, Iterable, Tuple
import sys

from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.tagger import tag_compiler
from ezdxf.tools.rawloader import raw_structure_loader
from ezdxf.tools.difftags import diff_tags, print_diff


def main(filename1: str, filename2: str, handle: str):
    doc1 = raw_structure_loader(filename1)
    doc2 = raw_structure_loader(filename2)
    try:
        a, b = get_entities(doc1, doc2, handle)
    except ValueError as e:
        print(str(e))
        sys.exit(1)
    print_diff(a, b, diff_tags(a, b, ndigits=6))


def get_entities(doc1, doc2, handle: str) -> Tuple[Tags, Tags]:
    a = entity_tags(doc1["ENTITIES"], handle)
    b = entity_tags(doc2["ENTITIES"], handle)
    if a is None or b is None:
        raise ValueError(f"Entity #{handle} not present in both files")
    return a, b


def entity_tags(entities: Iterable[Tags], handle: str) -> Optional[Tags]:
    def get_handle(tags: Tags):
        try:
            return tags.get_handle()
        except ValueError:
            return "0"

    for e in entities:
        if get_handle(e) == handle:
            return Tags(tag_compiler(iter(e)))
    return None


FILE1 = r"C:\Users\manfred\Desktop\Outbox\bottom_line_R2013.dxf"
FILE2 = r"C:\Users\manfred\Desktop\Outbox\bottom_line_brics.dxf"
HANDLE = "8A"

if __name__ == "__main__":
    main(FILE1, FILE2, HANDLE)
