#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
#  Work in progress, should be released in v0.18
"""
Block Reference Management Tools
================================

The package `ezdxf` is not designed as a CAD library and does not automatically
monitor all internal changes. This enables faster entity processing at the cost
of an unknown state of the DXF document.

In order to carry out precise BLOCK reference management, i.e. to handle
dependencies or to delete unused BLOCK definition, the block reference status
(counter) must be acquired explicitly by the package user.

This follows more the C++ zero-overhead principle:

    What you don't use, you don't pay for.

All block reference management structures must be explicitly recreated each time
the document content is changed. This is not very efficient, but it is safe.

.. warning::

    And even with all this careful approach, it is always possible to destroy a
    DXF document by deleting an absolutely necessary block definition.

Always remember that `ezdxf` is not intended or suitable as a basis for a CAD
application!

"""
from typing import TYPE_CHECKING, Dict, Iterable, List
from collections import Counter

from ezdxf.lldxf.types import POINTER_CODES
from ezdxf.entities import DXFEntity, BlockRecord
from ezdxf.protocols import referenced_blocks

if TYPE_CHECKING:
    from ezdxf.eztypes import Drawing
    from ezdxf.sections.tables import BlockRecordTable

""" 
Where are block references located:

- HEADER SECTION: $DIMBLK, $DIMBLK1, $DIMBLK2, $DIMLDRBLK 
- DIMENSION - arrows referenced in the associated anonymous BLOCK, covered by 
  the INSERT entities in that BLOCK
- ACAD_TABLE - has an anonymous BLOCK representation, covered by the 
  INSERT entities in that BLOCK

Entity specific block references, returned by the "ReferencedBlocks" protocol:
- INSERT: "name"
- DIMSTYLE: "dimblk", "dimblk1", "dimblk2", "dimldrblk"
- LEADER: DIMSTYLE override "dimldrblk" - has no anonymous BLOCK representation 
- MLEADER: arrows, blocks - has no anonymous BLOCK representation
- MLEADERSTYLE: arrows

Possible unknown or undocumented block references:
- DXFTagStorage - all handle group codes
- XDATA - only group code 1005
- APPDATA - all handle group codes
- XRECORD - all handle group codes

Contains no block references as far as known:
- DICTIONARY: can only references DXF objects like XRECORD or DICTIONARYVAR
- Extension Dictionary is a DICTIONARY object
- REACTORS - used for object messaging, a reactor does not establish 
  a block reference

Block references are stored as handles to the BLOCK_RECORD entity!

Testing DXF documents with missing BLOCK definitions:

- INSERT without an existing BLOCK definition does NOT crash AutoCAD/BricsCAD
- HEADER variables $DIMBLK, $DIMBLK2, $DIMBLK2 and $DIMLDRBLK can reference 
  non existing blocks without crashing AutoCAD/BricsCAD  

"""

BlockIndex = Dict[str, BlockRecord]
Handles = Iterable[str]


class BlockReferenceCounter:
    def __init__(self, doc: "Drawing"):
        # mapping: handle -> BlockRecord entity
        self._block_index = make_block_index(doc.block_records)

        # mapping: handle -> reference count
        self._counter = count_references(
            doc.entitydb.values(), self._block_index
        )

    def __len__(self) -> int:
        return len(self._counter)

    def __getitem__(self, item: str) -> int:
        return self._counter[item]


def make_block_index(block_records: "BlockRecordTable") -> BlockIndex:
    block_index: BlockIndex = dict()
    for block_record in block_records:
        assert isinstance(block_record, BlockRecord)
        if block_record.is_block_layout:
            block_index[block_record.dxf.handle] = block_record
    return block_index


def count_references(
    entities: Iterable[DXFEntity], block_index: BlockIndex
) -> Counter:
    def update(handles: Iterable[str]):
        # only count references to existing blocks:
        counter.update(h for h in handles if h in block_index)

    counter: Counter = Counter()
    for entity in entities:
        update(generic_handles(entity))
        update(referenced_blocks(entity))
    return counter


def generic_handles(entity: DXFEntity) -> Handles:
    def xdata_handles() -> Iterable[str]:
        for tags in entity.xdata.data.values():  # type: ignore
            for code, value in tags:
                if code == 1005:
                    yield value

    def appdata_handles() -> Iterable[str]:
        for tags in entity.appdata.data.values():  # type: ignore
            for code, value in tags:
                if code in POINTER_CODES:
                    yield value

    handles: List[str] = []
    if entity.xdata is not None:
        handles.extend(xdata_handles())
    if entity.appdata is not None:
        handles.extend(appdata_handles())
    return handles
