# Created: 12.04.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals
from ..lldxf.types import DXFTag
from .dxfobjects import DXFObject, DefSubclass, DXFAttributes, DXFAttr, none_subclass, ExtendedTags


_SORT_ENTITIES_TABLE_CLS = """  0
CLASS
  1
SORTENTSTABLE
  2
AcDbSortentsTable
  3
ObjectDBX Classes
 90
        0
 91
        4
280
     0
281
     0
"""

_SORT_ENTITIES_TABLE_TPL = """0
SORTENTSTABLE
5
0
102
{ACAD_REACTORS
330
0
102
}
330
0
100
AcDbSortentsTable
330
0
"""


def take2(iterable):
    store = None
    for item in iterable:
        if store is None:
            store = item
        else:
            yield store, item
            store = None


class SortEntitiesTable(DXFObject):
    # If the SORTENTS Regen flag (bit-code value 16) is set, AutoCAD regenerates entities in ascending handle order.
    # When the DRAWORDER command is used, a SORTENTSTABLE object is attached to the *Model_Space or *Paper_Space block's
    # extension dictionary under the name ACAD_SORTENTS. The SORTENTSTABLE object related to this dictionary associates
    # a different handle with each entity, which redefines the order in which the entities are regenerated.
    TEMPLATE = ExtendedTags.from_text(_SORT_ENTITIES_TABLE_TPL)
    CLASS = ExtendedTags.from_text(_SORT_ENTITIES_TABLE_CLS)
    DXFATTRIBS = DXFAttributes(none_subclass, DefSubclass('AcDbSortentsTable', {
        'block_record': DXFAttr(330),  # Soft-pointer ID/handle to owner (currently only the *MODEL_SPACE or *PAPER_SPACE blocks)
        # in ezdxf the block_record handle for a layout is also called layout_key
        # 331: Soft-pointer ID/handle to an entity (zero or more entries may exist)
        #   5: Sort handle (zero or more entries may exist)
    }))
    TABLE_START_INDEX = 2

    @property
    def sortentstable_subclass(self):
        return self.tags.subclasses[1]  # 2nd subclass

    def __len__(self):
        return (len(self.sortentstable_subclass)-self.TABLE_START_INDEX) // 2

    def __iter__(self):
        for handle, sort_handle in take2(self.sortentstable_subclass[self.TABLE_START_INDEX:]):
            yield handle.value, sort_handle.value

    def append(self, handle, sort_handle):
        subclass = self.sortentstable_subclass
        subclass.append(DXFTag(331, handle))
        subclass.append(DXFTag(5, sort_handle))

    def clear(self):
        del self.sortentstable_subclass[self.TABLE_START_INDEX:]

    def set_handles(self, handles):
        self.clear()
        for handle, sort_handle in handles:
            self.append(handle, sort_handle)

    def __getitem__(self, item):
        return list(self)[item]

    def __setitem__(self, item, value):
        handles = list(self)
        handles[item] = value
        self.set_handles(handles)

    def __delitem__(self, key):
        handles = list(self)
        del handles[key]
        self.set_handles(handles)
