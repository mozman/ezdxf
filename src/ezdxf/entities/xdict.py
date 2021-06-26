# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Union, Optional
from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.const import DXFStructureError
from ezdxf.lldxf.const import (
    ACAD_XDICTIONARY, XDICT_HANDLE_CODE, APP_DATA_MARKER,
)

if TYPE_CHECKING:
    from ezdxf.lldxf.tagwriter import TagWriter
    from ezdxf.eztypes import Dictionary, Drawing, DXFEntity, DXFObject

__all__ = ['ExtensionDict']


# Example for table head and -entries with extension dicts:
# AutodeskSamples\lineweights.dxf

class ExtensionDict:
    """ Stores extended data of entities in app data 'ACAD_XDICTIONARY', app
    data contains just one entry to a hard-owned DICTIONARY objects, which is
    not shared with other entities, each entity copy has its own extension
    dictionary and the extension dictionary is destroyed when the owner entity
    is deleted from database.

    """
    __slots__ = ('_xdict',)

    def __init__(self, xdict: Union[str, 'Dictionary']):
        # 1st loading stage: xdict as string -> handle to dict
        # 2nd loading stage: xdict as DXF Dictionary
        self._xdict = xdict

    @property
    def dictionary(self) -> 'Dictionary':
        """ Get associated extension dictionary as :class:`Dictionary` object.
        """
        assert self._xdict is not None
        return self._xdict

    @property
    def handle(self) -> str:
        return self._xdict.dxf.handle

    def __getitem__(self, key: str):
        return self.dictionary[key]

    def __setitem__(self, key: str, value):
        self.dictionary[key] = value

    def __contains__(self, key: str):
        return key in self.dictionary

    def get(self, key: str, default=None) -> Optional['DXFEntity']:
        return self._xdict.get(key, default)

    @classmethod
    def new(cls, owner_handle: str, doc: 'Drawing'):
        xdict = doc.objects.add_dictionary(
            owner=owner_handle,
            # All data in the extension dictionary belongs only to the owner
            hard_owned=True,
        )
        return cls(xdict)

    @property
    def is_alive(self):
        # Can not check if _xdict (as handle or Dictionary) really exist:
        return self._xdict is not None

    def update_owner(self, handle: str) -> None:
        """ Update owner tag of contained DXF Dictionary. """
        self.dictionary.dxf.owner = handle

    @classmethod
    def from_tags(cls, tags: Tags):
        assert tags is not None
        # Expected DXF structure:
        # [(102, '{ACAD_XDICTIONARY', (360, handle), (102, '}')]
        if len(tags) != 3 or tags[1].code != XDICT_HANDLE_CODE:
            raise DXFStructureError("ACAD_XDICTIONARY error.")
        return cls(tags[1].value)

    def load_resources(self, doc: 'Drawing') -> None:
        handle = self._xdict
        assert isinstance(handle, str)
        self._xdict = doc.entitydb.get(handle)

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        assert self._xdict is not None
        xdict = self._xdict
        handle = xdict if isinstance(xdict, str) else xdict.dxf.handle
        tagwriter.write_tag2(APP_DATA_MARKER, ACAD_XDICTIONARY)
        tagwriter.write_tag2(XDICT_HANDLE_CODE, handle)
        tagwriter.write_tag2(APP_DATA_MARKER, '}')

    def destroy(self) -> None:
        if self._xdict is not None:
            self._xdict.destroy()
            self._xdict = None

    def add_dictionary(self, name: str, doc: 'Drawing',
        hard_owned: bool = False) -> 'DXFEntity':
        dictionary = self._xdict
        new_dict = doc.objects.add_dictionary(
            owner=dictionary.dxf.hande,
            hard_owned=hard_owned,
        )
        dictionary[name] = new_dict
        return new_dict

    def add_placeholder(self, name: str,
        doc: 'Drawing') -> 'DXFEntity':
        dictionary = self._xdict
        placeholder = doc.objects.add_placeholder(dictionary.dxf.handle)
        dictionary[name] = placeholder
        return placeholder

    def link_dxf_object(self, name: str, obj: 'DXFObject') -> None:
        self._xdict.link_dxf_object(name, obj)
