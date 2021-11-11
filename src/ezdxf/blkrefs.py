#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
#  Work in progress, should be released in v0.18
"""
Block Reference Management
==========================

The package `ezdxf` is not designed as a CAD library and does not automatically
monitor all internal changes. This enables faster entity processing at the cost
of an unknown state of the DXF document.

In order to carry out precise BLOCK reference management, i.e. to handle
dependencies or to delete unused BLOCK definition, the block reference status
(counter) must be acquired explicitly by the package user.
All block reference management structures must be explicitly recreated each time
the document content is changed. This is not very efficient, but it is safe.

.. warning::

    And even with all this careful approach, it is always possible to destroy a
    DXF document by deleting an absolutely necessary block definition.

Always remember that `ezdxf` is not intended or suitable as a basis for a CAD
application!

.. versionadded:: 0.18

"""
from typing import TYPE_CHECKING, Dict, Iterable, List
from collections import Counter

from ezdxf.lldxf.types import POINTER_CODES
from ezdxf.entities import DXFEntity, BlockRecord, XRecord, DXFTagStorage
from ezdxf.protocols import referenced_blocks

if TYPE_CHECKING:
    from ezdxf.eztypes import Drawing, Tags
    from ezdxf.sections.tables import BlockRecordTable

__all__ = ["BlockReferenceCounter"]

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
    """
    Counts all block references in a DXF document.

    Check if a block is referenced by any entity or any resource (DIMSYTLE,
    MLEADERSTYLE) in a DXF document::

        import ezdxf
        from ezdxf.blkrefs import BlockReferenceCounter

        doc = ezdxf.readfile("your.dxf")
        counter = BlockReferenceCounter(doc)
        count = counter.by_name("XYZ")
        print(f"Block 'XYZ' if referenced {count} times.")

    """

    def __init__(self, doc: "Drawing"):
        self._doc = doc
        # mapping: handle -> BlockRecord entity
        self._block_index = make_block_index(doc.block_records)

        # mapping: handle -> reference count
        self._counter = count_references(
            doc.entitydb.values(), self._block_index
        )
        self._counter.update(header_section_handles(doc))

    def __len__(self) -> int:
        """Returns the count of block definitions used by the DXF document."""
        return len(self._counter)

    def __getitem__(self, handle: str) -> int:
        """Returns the block reference count for a given BLOCK_RECORD handle."""
        return self._counter[handle]

    def by_name(self, block_name: str) -> int:
        """Returns the block reference count for a given block name."""
        handle = ""
        block = self._doc.blocks.get(block_name, None)
        if block is not None:
            handle = block.block_record.dxf.handle
        return self._counter[handle]


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
        # add handles stored in XDATA and APP data
        update(generic_handles(entity))
        # add entity specific block references
        update(referenced_blocks(entity))
        # special entity types storing arbitrary raw DXF tags:
        if isinstance(entity, XRecord):
            update(all_pointer_handles(entity.tags))
        elif isinstance(entity, DXFTagStorage):
            # XDATA and APP data is already done!
            for tags in entity.xtags.subclasses[1:]:
                update(all_pointer_handles(tags))
            # ignore embedded objects: special objects for MTEXT and ATTRIB
    return counter


def generic_handles(entity: DXFEntity) -> Handles:
    handles: List[str] = []
    if entity.xdata is not None:
        for tags in entity.xdata.data.values():
            handles.extend(value for code, value in tags if code == 1005)
    if entity.appdata is not None:
        for tags in entity.appdata.data.values():
            handles.extend(all_pointer_handles(tags))
    return handles


def all_pointer_handles(tags: "Tags") -> Iterable[str]:
    return (value for code, value in tags if code in POINTER_CODES)


def header_section_handles(doc: "Drawing") -> Handles:
    header = doc.header
    for var_name in ("$DIMBLK", "$DIMBLK1", "$DIMBLK2", "$DIMLDRBLK"):
        blk_name = header.get(var_name, None)
        if blk_name is not None:
            block = doc.blocks.get(blk_name, None)
            if block is not None:
                yield block.block_record.dxf.handle
