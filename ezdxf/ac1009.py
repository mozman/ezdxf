#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: dxf engine for R12/AC1009
# Created: 11.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

"""
File Sections
=============

The DXF file is subdivided into four editable sections, plus the END
OF FILE marker. File separator groups are used to delimit these file
sections. The following is an example of a void DXF file with only
the section markers and table headers present:

   0            (Begin HEADER section)
  SECTION
   2
  HEADER
               <<<<Header variable items go here>>>>
  0
  ENDSEC       (End HEADER section)
   0           (Begin TABLES section)
  SECTION
   2
  TABLES
   0
  TABLE
   2
  VPORT
   70
  (viewport table maximum item count)
               <<<<viewport table items go here>>>>
  0
  ENDTAB
  0
  TABLE
  2
  APPID, DIMSTYLE, LTYPE, LAYER, STYLE, UCS, VIEW, or VPORT
  70
  (Table maximum item count)
               <<<<Table items go here>>>>
  0
  ENDTAB
  0
  ENDSEC       (End TABLES section)
  0            (Begin BLOCKS section)
  SECTION
  2
  BLOCKS
               <<<<Block definition entities go here>>>>
  0
  ENDSEC       (End BLOCKS section)
  0            (Begin ENTITIES section)
  SECTION
  2
  ENTITIES
               <<<<Drawing entities go here>>>>
  0
  ENDSEC       (End ENTITIES section)
  0
  EOF          (End of file)

"""

from .ac1009hdrvars import VARMAP

class AC1009Engine:
    HEADERVARS = dict(VARMAP)
    def __init__(self):
        self.drawing = None

    def new_header_var(self, key, value):
        factory = self.HEADERVARS[key]
        return factory(value)

    def table_entry_wrapper(self, tags, handle):
        return TableEntryWrapper(tags, handle)

    def table_wrapper(self, table):
        return TableWrapper(table)

class TableWrapper:
    """
    Encapsulate all DXF-Version specific details for all DXF tables.

    Tables are: LTYPE, LAYER, STYLE, ... in the TABLES section

    """
    def __init__(self, table):
        self. _table = table

    @property
    def name(self):
        return self._table.name

    def set_count(self, count):
        self._table._table_header.settag(70, count)

class TableEntryWrapper:
    """
    Encapsulate all DXF-Version specific details for all DXF table entries.

    Table entries starting with tag (0, TABLENAME): (0, LTYPE), (0, LAYER), ...
    in the TABLE tag-chunk.

    """
    def __init__(self, tags, handle):
        self.tags = tags
        self.handle = handle

    @property
    def name(self):
        return self.tags[self.tags.findfirst(2)].value
