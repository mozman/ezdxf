# Created: 15.04.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT-License
from typing import TYPE_CHECKING, Iterable, Tuple
from ezdxf.lldxf.types import DXFTag
from ezdxf.tools import take2

from .dxfobjects import DXFObject, DefSubclass, DXFAttributes, DXFAttr, none_subclass, ExtendedTags


if TYPE_CHECKING:
    from ezdxf.eztypes import Tags


_SORT_ENTITIES_TABLE_CLS = """0
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
0
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


class SortEntitiesTable(DXFObject):
    # should work with AC1015/R2000 but causes problems with TrueView/AutoCAD LT 2019: "expected was-a-zombie-flag"
    # No problems with AC1018/R2004 and later
    #
    # If the header variable $SORTENTS Regen flag (bit-code value 16) is set, AutoCAD regenerates entities in ascending
    # handle order.
    #
    # When the DRAWORDER command is used, a SORTENTSTABLE object is attached to the *Model_Space or *Paper_Space block's
    # extension dictionary under the name ACAD_SORTENTS. The SORTENTSTABLE object related to this dictionary associates
    # a different handle with each entity, which redefines the order in which the entities are regenerated.
    #
    # $SORTENTS (280): Controls the object sorting methods (bitcode):
    # 0 = Disables SORTENTS
    # 1 = Sorts for object selection
    # 2 = Sorts for object snap
    # 4 = Sorts for redraws; obsolete
    # 8 = Sorts for MSLIDE command slide creation; obsolete
    # 16 = Sorts for REGEN commands
    # 32 = Sorts for plotting
    # 64 = Sorts for PostScript output; obsolete
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_SORT_ENTITIES_TABLE_TPL)
    CLASS = ExtendedTags.from_text(_SORT_ENTITIES_TABLE_CLS)
    DXFATTRIBS = DXFAttributes(none_subclass, DefSubclass('AcDbSortentsTable', {
        'block_record': DXFAttr(330),  # Soft-pointer ID/handle to owner (currently only the *MODEL_SPACE or *PAPER_SPACE blocks)
        # in ezdxf the block_record handle for a layout is also called layout_key
        # 331: Soft-pointer ID/handle to an entity (zero or more entries may exist)
        #   5: Sort handle (zero or more entries may exist)
    }))
    # AutoCAD has no problem with not existing entities as group code 331, just ignores this entries,
    # so it is not necessary to update the SORTENTSTABLE when deleting entities
    TABLE_START_INDEX = 2

    @property
    def sortentstable_subclass(self) -> 'Tags':
        return self.tags.subclasses[1]  # 2nd subclass

    def __len__(self) -> int:
        return (len(self.sortentstable_subclass)-self.TABLE_START_INDEX) // 2

    def __iter__(self) -> Iterable[Tuple[str, str]]:
        """
        Yields all redraw associations as (object_handle, sort_handle) tuples.

        """
        for handle, sort_handle in take2(self.sortentstable_subclass[self.TABLE_START_INDEX:]):
            yield handle.value, sort_handle.value

    def append(self, handle: str, sort_handle: str) -> None:
        """
        Append redraw association (handle, sort_handle).

        Args:
            handle: DXF entity handle (uppercase hex value without leading '0x')
            sort_handle: sort handle (uppercase hex value without leading '0x')

        """
        subclass = self.sortentstable_subclass
        subclass.append(DXFTag(331, handle))
        subclass.append(DXFTag(5, sort_handle))

    def clear(self) -> None:
        """
        Remove all handles from redraw order table.

        """
        del self.sortentstable_subclass[self.TABLE_START_INDEX:]

    def set_handles(self, handles: Iterable[Tuple[str, str]]) -> None:
        """
        Set all redraw associations from iterable `handles`, after removing all existing associations.

        Args:
            handles: iterable yielding (object_handle, sort_handle) tuples

        """
        # The sort_handle doesn't have to be unique, same or all handles can share the same sort_handle and sort_handles
        # can use existing handles too.
        #
        # The '0' handle can be used, but this sort_handle will be drawn as latest (on top of all other entities) and
        # not as first as expected. Invalid entity handles will be ignored by AutoCAD.
        self.clear()
        for handle, sort_handle in handles:
            self.append(handle, sort_handle)

    def remove_invalid_handles(self) -> None:
        """
        Remove all handles which do not exists in the drawing database.

        """
        entitydb = self.drawing.entitydb
        valid_handles = [(handle, sort_handle) for handle, sort_handle in self if handle in entitydb]
        # list is required, set_handles() deletes all entries before iterating valid_handles
        self.set_handles(valid_handles)

    def remove_handle(self, handle: str) -> None:
        """
        Remove handle of DXF entity from redraw order table.

        Args:
            handle: DXF entity handle (uppercase hex value without leading '0x')

        """
        handles = dict(self)
        if handle in handles:
            del handles[handle]
            self.set_handles(handles.items())
