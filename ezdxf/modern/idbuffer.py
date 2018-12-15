# Created: 12.04.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT-License
from typing import TYPE_CHECKING, Iterable, Union, Any, cast
import array

from ezdxf.lldxf.types import DXFTag
from ezdxf.lldxf.packedtags import PackedTags, replace_tags
from ezdxf.lldxf import loader

from .dxfobjects import DXFObject, DefSubclass, DXFAttributes, none_subclass, ExtendedTags

if TYPE_CHECKING:
    from ezdxf.eztypes import Tags


def convert(values: Iterable[Union[str, int]]) -> Iterable[int]:
    for value in values:
        yield int(value, 16) if isinstance(value, str) else value


def new_array(values: Iterable[Union[str, int]] = None) -> array.array:
    a = array.array('Q')
    if values is not None:
        a.extend(convert(values))
    return a


class PackedHandles(PackedTags):
    code = -330  # compatible with DXFTag.code
    __slots__ = ('value',)

    def __init__(self, handles: Iterable[str] = None):
        # compatible with DXFTag.value
        self.value = new_array(handles)  # type: array.array

    def __len__(self) -> int:
        return len(self.value)

    def __getitem__(self, item: Union[slice, int]) -> Union[str, Iterable[str]]:
        if isinstance(item, slice):
            return ['%X' % v for v in self.value[item]]
        else:
            return '%X' % self.value[item]

    def __setitem__(self, item: int, value: Any) -> None:
        if isinstance(value, (tuple, list)):
            value = new_array(value)
        else:
            value = int(value, 16)
        self.value[item] = value

    def __delitem__(self, item: int) -> None:
        del self.value[item]

    def __iadd__(self, value: str) -> 'PackedHandles':
        self.append(value)
        return self

    def __eq__(self, other: 'PackedHandles') -> bool:
        return self.value == new_array(other)

    def append(self, handle: str) -> None:
        self.value.append(int(handle, 16))

    def extend(self, handles: Iterable[str]) -> None:
        self.value.extend(convert(handles))

    def dxftags(self) -> Iterable[DXFTag]:
        for handle in self.value:
            yield DXFTag(330, "%X" % handle)

    def clone(self) -> 'PackedHandles':
        return self.__class__(handles=self.value)

    def clear(self) -> None:
        del self.value[:]


@loader.register('IDBUFFER', legacy=False)
def tag_processor(tags: ExtendedTags):
    subclass = tags.get_subclass('AcDbIdBuffer')
    id_buffer = PackedHandles(handles=(tag.value for tag in subclass[1:]))
    replace_tags(subclass, codes=(330,), packed_data=id_buffer)
    return tags


_IDBUFFER_TPL = """0
IDBUFFER
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
AcDbIdBuffer
"""


class IDBuffer(DXFObject):
    __slots__ = ('_cached_handles',)
    TEMPLATE = tag_processor(ExtendedTags.from_text(_IDBUFFER_TPL))
    DXFATTRIBS = DXFAttributes(none_subclass, DefSubclass('AcDbIdBuffer', {}))

    @property
    def buffer_subclass(self) -> 'Tags':
        return self.tags.subclasses[1]  # 2nd subclass

    @property
    def handles(self) -> PackedHandles:
        try:
            return self._cached_handles
        except AttributeError:
            self._cached_handles = cast(PackedHandles, self.buffer_subclass.get_first_tag(PackedHandles.code))
            return self._cached_handles

    @handles.setter
    def handles(self, items: Iterable[str]) -> None:
        self.handles[:] = list(items)
