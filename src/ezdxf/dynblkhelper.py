#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
"""
This module provides helper tools to work with dynamic blocks.

The current state supports only reading information from dynamic blocks, it does not
support creation of new dynamic blocks nor the modification of them.

"""
from __future__ import annotations
from ezdxf.entities import Insert
from ezdxf.lldxf import const


def is_dynamic_block_reference(insert: Insert) -> bool:
    """Returns ``True`` if the given block reference is referencing a dynamic block
    direct or indirect via an anonymous block.
    """
    return bool(get_dynamic_block_name(insert))


def get_dynamic_block_name(insert: Insert) -> str:
    """Returns the name of the dynamic Block if the given block reference is referencing
    a dynamic block direct or indirect via an anonymous block.
    """

    doc = insert.doc
    if doc is None:
        return ""
    block = insert.block()
    if block is None:
        return ""
    block_record = block.block_record
    if block_record.has_xdata("AcDbDynamicBlockGUID"):
        return block_record.dxf.name

    try:
        xdata = block_record.get_xdata("AcDbBlockRepBTag")
    except const.DXFValueError:
        return ""
    handle = xdata.get_first_value(1005, "")
    if handle == "":
        return ""
    dyn_block_record = doc.entitydb.get(handle)
    if dyn_block_record:
        return dyn_block_record.dxf.name
    return ""





