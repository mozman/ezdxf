# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, List, Iterable, Set, Sequence
from collections import OrderedDict
from ezdxf.lldxf.types import dxftag, uniform_appid
from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.const import DXFKeyError, DXFStructureError
from ezdxf.lldxf.const import ACAD_REACTORS, REACTOR_HANDLE_CODE, APP_DATA_MARKER

if TYPE_CHECKING:
    from ezdxf.lldxf.tagwriter import TagWriter

__all__ = ['AppData', 'Reactors']

ERR_INVALID_DXF_ATTRIB = 'Invalid DXF attribute for entity {}'
ERR_DXF_ATTRIB_NOT_EXITS = 'DXF attribute {} does not exist'


class AppData:
    def __init__(self):
        self.data = OrderedDict()

    def __contains__(self, appid: str) -> bool:
        return uniform_appid(appid) in self.data

    def __len__(self) -> int:
        return len(self.data)

    def get(self, appid: str) -> Tags:
        try:
            return self.data[uniform_appid(appid)]
        except KeyError:
            raise DXFKeyError(appid)

    def set(self, tags: Tags) -> None:
        if len(tags):
            appid = tags[0].value
            self.data[appid] = tags

    def add(self, appid: str, data: Iterable[Sequence]) -> None:
        data = Tags(dxftag(code, value) for code, value in data)
        appid = uniform_appid(appid)
        if data[0] != (APP_DATA_MARKER, appid):
            data.insert(0, dxftag(APP_DATA_MARKER, appid))
        if data[-1] != (APP_DATA_MARKER, '}'):
            data.append(dxftag(APP_DATA_MARKER, '}'))
        self.set(data)

    def discard(self, appid: str):
        _appid = uniform_appid(appid)
        if _appid in self.data:
            del self.data[_appid]

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        for data in self.data.values():
            tagwriter.write_tags(data)


class Reactors:
    """ Handle storage for related reactors.

    Reactors are other objects related to the object that contains this
    Reactor() instance.

    """

    def __init__(self, handles: Iterable[str] = None):
        self.reactors: Set[str] = None  # stores handles as strings
        self.set(handles)

    def __len__(self) -> int:
        return len(self.reactors)

    def __contains__(self, handle):
        return handle in self.reactors

    def __iter__(self):
        return iter(self.get())

    @classmethod
    def from_tags(cls, tags: Tags = None) -> 'Reactors':
        """ Create Reactors() instance from tags.

        Expected DXF structure: [(102, '{ACAD_REACTORS'), (330, handle), ..., (102, '}')]

        Args:
            tags: list of DXFTags()

        """
        if tags is None:
            return cls(None)

        if len(tags) < 2:  # no reactors are valid
            raise DXFStructureError("ACAD_REACTORS error")
        return cls((handle.value for handle in tags[1:-1]))

    def get(self) -> List[str]:
        return sorted(self.reactors, key=lambda x: int(x, base=16))

    def set(self, handles: Iterable[str]) -> None:
        self.reactors = set(handles or [])

    def add(self, handle: str) -> None:
        self.reactors.add(handle)

    def discard(self, handle: str):
        self.reactors.discard(handle)

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        tagwriter.write_tag2(APP_DATA_MARKER, ACAD_REACTORS)
        for handle in self.get():
            tagwriter.write_tag2(REACTOR_HANDLE_CODE, handle)
        tagwriter.write_tag2(APP_DATA_MARKER, '}')
