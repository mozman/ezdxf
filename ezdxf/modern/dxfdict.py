# Created: 22.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT-License
from typing import TYPE_CHECKING, cast, KeysView, ItemsView, Any, Union
from ezdxf.lldxf.const import DXFKeyError
from ezdxf.lldxf.packedtags import TagDict
from ezdxf.lldxf import loader

from .dxfobjects import DXFObject, DefSubclass, DXFAttributes, DXFAttr, ExtendedTags
from .dxfobjects import none_subclass

if TYPE_CHECKING:
    from collections import OrderedDict
    from ezdxf.eztypes import Tags, DXFEntity, Auditor


@loader.register('ACDBDICTIONARYWDFLT', legacy=False)
@loader.register('DICTIONARY', legacy=False)
def tag_processor(tags: ExtendedTags) -> ExtendedTags:
    subclass = tags.get_subclass('AcDbDictionary')
    d = TagDict.from_tags(subclass)
    d.replace_tags(subclass)
    return tags


_DICT_TPL = """0
DICTIONARY
5
0
330
0
100
AcDbDictionary
281
1
"""

dictionary_subclass = DefSubclass('AcDbDictionary', {
    'hard_owned': DXFAttr(280, default=0),  # Hard-owner flag.
    # If set to 1, indicates that elements of the dictionary are to be treated as hard-owned
    'cloning': DXFAttr(281, default=1),  # Duplicate record cloning flag (determines how to merge duplicate entries):
    # 0 = not applicable
    # 1 = keep existing
    # 2 = use clone
    # 3 = <xref>$0$<name>
    # 4 = $0$<name>
    # 5 = Unmangle name

    # 3: entry name
    # 350: entry handle, some DICTIONARY objects have 360 as handle group code, this is accepted by AutoCAD but not
    # documented by the DXF reference!!! ezdxf replaces 360 codes by 350.
})


class DXFDictionary(DXFObject):
    __slots__ = ('_cached_dict',)
    """
    AutoCAD maintains items such as mline styles and group definitions as objects in dictionaries.
    Other applications are free to create and use their own dictionaries as they see fit. The prefix "ACAD_" is reserved
    for use by AutoCAD applications.

    DXFDictionary entries are (key, handle) values, so it can only store handles and nothing else, to store other
    values, you have to create a DXFDictionaryVar object, and store its handle.

    """
    TEMPLATE = tag_processor(ExtendedTags.from_text(_DICT_TPL))
    DXFATTRIBS = DXFAttributes(
        none_subclass,
        dictionary_subclass,
    )

    @property
    def AcDbDictinary(self) -> 'Tags':
        return self.tags.subclasses[1]

    @property
    def is_hard_owner(self) -> bool:
        return bool(self.get_dxf_attrib('hard_owned', False))

    @property
    def data(self) -> 'OrderedDict':
        try:
            return self._cached_dict
        except AttributeError:
            self._cached_dict = cast('OrderedDict', self.AcDbDictinary.get_first_value(TagDict.code))
            return self._cached_dict

    def keys(self) -> KeysView:
        """
        Generator for the dictionary's keys.

        """
        return self.data.keys()

    def items(self) -> ItemsView:
        """
        Generator for the dictionary's items as (key, value) pairs.

        """
        return self.data.items()

    def __getitem__(self, key: str) -> str:
        """
        Return the value for `key` if key is in the dictionary, else raises a `KeyError`.

        """
        return self.get(key)

    def __setitem__(self, key: str, value: str) -> None:
        """
        Add item `(key, value)` to dictionary.

        """
        return self.add(key, value)

    def __delitem__(self, key: str) -> None:
        """
        Remove element `key` from the dictionary. Raises `KeyError` if key is not contained in the dictionary.

        """
        return self.remove(key)

    def __contains__(self, key: str) -> bool:
        """
        Return True if the dictionary has `key`, else False.

        """
        return key in self.data

    def __len__(self) -> int:
        """
        Return the number of items in the dictionary.

        """
        return len(self.data)

    count = __len__

    def get(self, key: str, default: Any = DXFKeyError) -> str:
        """
        Return the value (handle) for `key` if `key` is in the dictionary, else `default` or raises a `DXFKeyError`
        for `default`=`DXFKeyError`.

        """
        try:
            return self.data[key]
        except KeyError:
            if default is DXFKeyError:
                raise DXFKeyError("KeyError: '{}'".format(key))
            else:
                return default

    get_handle = get  # synonym

    def get_entity(self, key: str) -> Union['DXFEntity', str]:
        """
        Get object referenced by handle associated by `key` as wrapped entity, raises a `KeyError` if *key* not exists.

        """
        handle = self.get(key)
        if self.drawing is not None:
            return self.dxffactory.wrap_handle(handle)
        else:
            return handle

    def add(self, key: str, value: str) -> None:
        """
        Add item `(key, value)` to dictionary.

        """
        self.data[key] = value

    def remove(self, key: str) -> None:
        """
        Remove element `key` from the dictionary. Raises `DXFKeyError` if `key` not exists. Deletes hard owned DXF
        objects from OBJECTS section.

        """
        data = self.data
        if key not in data:
            raise DXFKeyError(key)

        if self.is_hard_owner:
            entity = self.get_entity(key)
            # Presumption: hard owned DXF objects always reside in the OBJECTS section
            self.drawing.objects.delete_entity(entity)
        del data[key]

    def discard(self, key: str) -> None:
        """
        Remove `key` from dictionary, if exists. Does NOT delete hard owned entities!

        """
        try:
            del self.data[key]
        except KeyError:
            pass

    def clear(self) -> None:
        """
        Removes all entries from DXFDictionary, and also deletes all hard owned DXF objects from OBJECTS section.

        """
        if self.is_hard_owner:
            self.delete_hard_owned_entries()
        self.data.clear()

    def delete_hard_owned_entries(self) -> None:
        # Presumption: hard owned DXF objects always reside in the OBJECTS section
        objects = self.drawing.objects
        wrap = self.dxffactory.wrap_handle
        for key, handle in self.items():
            objects.delete_entity(wrap(handle))

    def add_new_dict(self, key: str) -> 'DXFDictionary':
        """
        Create a new sub dictionary.

        Args:
            key: name of the sub dictionary

        """
        dxf_dict = self.drawing.objects.add_dictionary(owner=self.dxf.handle)
        self.add(key, dxf_dict.dxf.handle)
        return dxf_dict

    def get_required_dict(self, key: str) -> 'DXFDictionary':
        """
        Get DXFDictionary `key`, if exists or create a new DXFDictionary.

        """
        try:
            dxf_dict = self.get_entity(key)
        except DXFKeyError:
            dxf_dict = self.add_new_dict(key)
        return dxf_dict

    def audit(self, auditor: 'Auditor') -> None:
        auditor.check_handles_exists(self, handles=self.data.values())

    def destroy(self) -> None:
        if self.get_dxf_attrib('hard_owned', False):
            self.delete_hard_owned_entries()


_DICT_WITH_DEFAULT_CLS = """0
CLASS
1
ACDBDICTIONARYWDFLT
2
AcDbDictionaryWithDefault
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

_DICT_WITH_DEFAULT_TPL = """0
ACDBDICTIONARYWDFLT
5
0
330
0
100
AcDbDictionary
281
1
100
AcDbDictionaryWithDefault
340
0
"""


class DXFDictionaryWithDefault(DXFDictionary):
    TEMPLATE = tag_processor(ExtendedTags.from_text(_DICT_WITH_DEFAULT_TPL))
    CLASS = (ExtendedTags.from_text(_DICT_WITH_DEFAULT_CLS))
    DXFATTRIBS = DXFAttributes(
        none_subclass,
        dictionary_subclass,
        DefSubclass('AcDbDictionaryWithDefault', {
            'default': DXFAttr(340),
        }),
    )

    def get(self, key: str, default: Any = DXFKeyError) -> str:
        """
        Return the value for `key` if exists else returns the predefined dictionary wide `default` value. Parameter
        `default` is always ignored!

        """
        return super(DXFDictionaryWithDefault, self).get(key, default=self.dxf.default)


_DICTIONARYVAR_CLS = """0
CLASS
1
DICTIONARYVAR
2
AcDbDictionaryVar
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

_DICTIONARYVAR_TPL = """0
DICTIONARYVAR
5
0
330
0
102
DictionaryVariables
280
0
1

"""


class DXFDictionaryVar(DXFObject):
    """
    DICTIONARYVAR objects are used by AutoCAD as a means to store named values in the database for setvar / getvar
    purposes without the need to add entries to the DXF HEADER section. System variables that are stored as
    DICTIONARYVAR objects are the following:

        - DEFAULTVIEWCATEGORY
        - DIMADEC
        - DIMASSOC
        - DIMDSEP
        - DRAWORDERCTL
        - FIELDEVAL
        - HALOGAP
        - HIDETEXT
        - INDEXCTL
        - INDEXCTL
        - INTERSECTIONCOLOR
        - INTERSECTIONDISPLAY
        - MSOLESCALE
        - OBSCOLOR
        - OBSLTYPE
        - OLEFRAME
        - PROJECTNAME
        - SORTENTS
        - UPDATETHUMBNAIL
        - XCLIPFRAME
        - XCLIPFRAME

    """
    TEMPLATE = ExtendedTags.from_text(_DICTIONARYVAR_TPL)
    CLASS = ExtendedTags.from_text(_DICTIONARYVAR_CLS)
    DXFATTRIBS = DXFAttributes(
        none_subclass,
        DefSubclass('DictionaryVariables', {
            'schema': DXFAttr(280, default=0),  # Object schema number (currently set to 0)
            'value': DXFAttr(1),
        }),
    )
