#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
"""
This module provides helper tools to work with dynamic blocks.

The current state supports only reading information from dynamic blocks, it does not
support the creation of new dynamic blocks nor the modification of them.

"""
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from ezdxf.entities import Insert
from ezdxf.lldxf import const

if TYPE_CHECKING:
    from ezdxf.document import Drawing
    from ezdxf.layouts import BlockLayout

AcDbDynamicBlockGUID = "AcDbDynamicBlockGUID"
AcDbBlockRepBTag = "AcDbBlockRepBTag"


def get_dynamic_block_definition(
    insert: Insert, doc: Optional[Drawing] = None
) -> Optional[BlockLayout]:
    """Returns the dynamic block definition if the given block reference is
    referencing a dynamic block direct or indirect via an anonymous block.
    Returns ``None`` otherwise.
    """
    block: Optional[BlockLayout] = None
    if doc is None:
        doc = insert.doc
    if doc is None:
        return block

    block = doc.blocks.get(insert.dxf.name)
    if block is None:
        return block

    block_record = block.block_record
    # check if block is a dynamic block definition
    if block_record.has_xdata(AcDbDynamicBlockGUID):
        return block

    try:  # check for indirect dynamic block reference
        xdata = block_record.get_xdata(AcDbBlockRepBTag)
    except const.DXFValueError:
        return None  # not a dynamic block reference

    # get handle of dynamic block definition
    handle = xdata.get_first_value(1005, "")
    if handle == "":
        return None  # lost reference to dynamic block definition
    dyn_block_record = doc.entitydb.get(handle)
    if dyn_block_record:
        return doc.blocks.get(dyn_block_record.dxf.name)
    # block record of dynamic block definition not found
    return None
