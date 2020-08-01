# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
# Created 2019-02-27
from typing import TYPE_CHECKING, cast, Union, Optional
from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.const import DXFStructureError
from ezdxf.lldxf.const import (
    ACAD_XDICTIONARY, XDICT_HANDLE_CODE, APP_DATA_MARKER,
)

if TYPE_CHECKING:
    from ezdxf.lldxf.tagwriter import TagWriter
    from ezdxf.eztypes import Dictionary, Drawing, DXFEntity, ObjectsSection

__all__ = ['ExtensionDict']


class ExtensionDict:
    """ Stores extended data of entities in app data 'ACAD_XDICTIONARY', app
    data contains just one entry to a hard-owned DICTIONARY objects, which is
    not shared with other entities, each entity copy has its own extension
    dictionary and the extension dictionary is destroyed when the owner entity
    is deleted from database.

    """

    def __init__(self, owner: 'DXFEntity', xdict: Union[str, 'Dictionary']):
        # back link owner, so __clone__() necessary
        self.owner = owner
        # _xdict as string -> handle to dict
        # _xdict as DXF Dictionary
        self._xdict = xdict

    @property
    def dictionary(self) -> 'Dictionary':
        """ Get associated extension dictionary as Dictionary() object. """
        assert self._xdict is not None
        if isinstance(self._xdict, str):
            # replace handle string by DXFDictionary object
            self._xdict = cast('Dictionary',
                               self.owner.entitydb.get(self._xdict))
        return self._xdict

    def __getitem__(self, key: str):

        return self.dictionary[key]

    def __setitem__(self, key: str, value):
        self.dictionary[key] = value

    def __contains__(self, key: str):
        return key in self.dictionary

    @property
    def dxf(self):
        return self.dictionary.dxf

    @classmethod
    def new(cls, owner: 'DXFEntity'):
        xdict = owner.doc.objects.add_dictionary(
            owner=owner.dxf.handle,
            hard_owned=True,
            # All data in the extension dictionary belongs only to the owner
        )
        return cls(owner, xdict)

    def copy(self, owner: 'DXFEntity') -> Optional['ExtensionDict']:
        """ Create a copy of the extension dictionary with new `owner`. """
        assert self._xdict is not None
        copy = self.dictionary.copy()
        # the copy is not added to objects section nor to the entity database!
        # The copy of an extension dictionary can not have the same owner as the source dictionary.
        return self.__class__(owner, copy)

    @property
    def is_alive(self):
        return self._xdict is not None

    def update_owner(self, owner: 'DXFEntity') -> None:
        """ Update owner attribute, but also owner tag of contained DXF Dictionary.
        """
        assert self._xdict is not None
        self.owner = owner
        self.dictionary.dxf.owner = self.owner.dxf.handle

    def __deepcopy__(self, memodict: dict = None):
        """ Extension dict is owned by just one entity, multiple references are
        not (should not?) possible.
        """
        return self.copy(self.owner)  # use current owner as temporary solution

    @classmethod
    def from_tags(cls, entity: 'DXFEntity', tags: Tags):
        assert tags is not None
        # Expected DXF structure:
        # [(102, '{ACAD_XDICTIONARY', (360, handle), (102, '}')]
        if len(tags) != 3 or tags[1].code != XDICT_HANDLE_CODE:
            raise DXFStructureError(
                "ACAD_XDICTIONARY error in entity: " + str(entity))
        return cls(entity, tags[1].value)

    @property
    def doc(self) -> 'Drawing':
        return self.owner.doc

    @property
    def objects(self) -> 'ObjectsSection':
        return self.owner.doc.objects

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        assert self._xdict is not None
        xdict = self._xdict
        handle = xdict if isinstance(xdict, str) else xdict.dxf.handle
        tagwriter.write_tag2(APP_DATA_MARKER, ACAD_XDICTIONARY)
        tagwriter.write_tag2(XDICT_HANDLE_CODE, handle)
        tagwriter.write_tag2(APP_DATA_MARKER, '}')

    def destroy(self, doc: 'Drawing') -> None:
        assert self._xdict is not None
        doc.objects.delete_entity(self.dictionary)
        self._xdict = None

    def add_dictionary(self, name: str,
                       hard_owned: bool = False) -> 'DXFEntity':
        new_dict = self.dictionary.add_new_dict(name, hard_owned=hard_owned)
        return new_dict

    def add_placeholder(self, name: str) -> 'DXFEntity':
        dictionary = self.dictionary
        placeholder = self.objects.add_placeholder(dictionary.dxf.handle)
        dictionary[name] = placeholder
        return placeholder
