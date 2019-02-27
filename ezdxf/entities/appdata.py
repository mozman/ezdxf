# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-13
#
# DXFEntity - Root Entity
# DXFObject - non graphical entities stored in OBJECTS section
# DXFGraphical - graphical DXF entities stored in ENTITIES and BLOCKS sections
#
from typing import TYPE_CHECKING, List, cast, Union, Iterable, Set, Sequence, Optional
from collections import OrderedDict
from ezdxf.lldxf.types import dxftag, uniform_appid
from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.const import DXFKeyError, DXFStructureError, DXFInternalEzdxfError
from ezdxf.lldxf.const import ACAD_XDICTIONARY, ACAD_REACTORS, XDICT_HANDLE_CODE, REACTOR_HANDLE_CODE, APP_DATA_MARKER

if TYPE_CHECKING:
    from ezdxf.lldxf.tagwriter import TagWriter
    from ezdxf.eztypes2 import Dictionary, Drawing, DXFEntity

__all__ = ['AppData', 'Reactors', 'ExtensionDict']

ERR_INVALID_DXF_ATTRIB = 'Invalid DXF attribute for entity {}'
ERR_DXF_ATTRIB_NOT_EXITS = 'DXF attribute {} does not exist'


class AppData:
    def __init__(self):
        # no back links, no self.clone() required, use deepcopy
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

    Reactors are other objects related to the object that contains this Reactor() instance.

    """

    def __init__(self, handles: Iterable[str] = None):
        # no back links, no self.clone() required
        self.reactors = None  # type: Set[str]  # stores handle strings
        self.set(handles)

    def __len__(self) -> int:
        return len(self.reactors)

    def __contains__(self, handle):
        return handle in self.reactors

    def __iter__(self):
        return iter(self.get())

    @classmethod
    def from_tags(cls, tags: Tags = None) -> 'Reactors':
        """
        Create Reactors() instance from tags.

        Expected DXF structure: [(102, '{ACAD_REACTORS'), (330, handle), ...,(102, '}')]

        Args:
            tags: list of DXFTags()

        """
        if tags is None:
            return cls(None)

        if len(tags) < 3:
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


class ExtensionDict:
    # todo: test, but requires objects section
    def __init__(self, owner: 'DXFEntity', xdict: Union[str, 'Dictionary']):
        # back link owner, so __clone__() necessary
        self.owner = owner
        # _xdict is None -> empty dict
        # _xdict as string -> handle to dict
        # _xdict as Dictionary
        self._xdict = xdict

    def copy(self, owner: 'DXFEntity') -> Optional['ExtensionDict']:
        """ Create a clone of the extension dictionary with new `owner`. """
        assert self._xdict is not None
        xdict = self.get()
        copy = xdict.copy()
        # The copy of an extension dictionary can not have the same owner as the source dictionary.
        return self.__class__(owner, copy)

    def update_owner(self, owner: 'DXFEntity') -> None:
        assert self._xdict is not None
        self.owner = owner.dxf.handle
        xdict = self.get()
        xdict.dxf.owner = self.owner

    def __deepcopy__(self, memodict: dict = None):
        """ Extension dict is owned by just one entity, multiple references are not (should not?) possible """
        return self.copy(self.owner)

    @classmethod
    def from_tags(cls, entity: 'DXFEntity', tags: Tags = None):
        if tags is None:
            return cls(entity, None)

        # expected DXF structure: [(102, '{ACAD_XDICTIONARY', (360, handle), (102, '}')]
        if len(tags) != 3 or tags[1].code != XDICT_HANDLE_CODE:
            raise DXFStructureError("ACAD_XDICTIONARY error in entity: " + str(entity))
        return cls(entity, tags[1].value)

    @property
    def doc(self) -> 'Drawing':
        return self.owner.doc

    def get(self) -> 'Dictionary':
        """
        Get associated extension dictionary as Dictionary() object.

        """
        if self._xdict is None:
            self._xdict = self._new()
        elif isinstance(self._xdict, str):
            # replace handle string by DXFDictionary object
            self._xdict = cast('Dictionary', self.owner.entitydb.get(self._xdict))
        return self._xdict

    def _new(self) -> 'Dictionary':
        xdict = self.doc.objects.add_dictionary(
            owner=self.owner.dxf.handle,
            hard_owned=True,  # I guess all data in the extension dictionary belongs only to the owner
        )
        return cast('Dictionary', xdict)

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        xdict = self._xdict
        if xdict is None:
            return
        handle = xdict if isinstance(xdict, str) else xdict.dxf.handle
        tagwriter.write_tag2(APP_DATA_MARKER, ACAD_XDICTIONARY)
        tagwriter.write_tag2(XDICT_HANDLE_CODE, handle)
        tagwriter.write_tag2(APP_DATA_MARKER, '}')

    def destroy(self, doc: 'Drawing'):
        if self._xdict is not None:
            doc.objects.delete_entity(self.get())
        self._xdict = None
