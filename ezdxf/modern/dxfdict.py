# Created: 22.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals
from ..lldxf.const import DXFValueError, DXFKeyError
from ..lldxf.types import DXFTag
from .dxfobjects import DXFObject, DefSubclass, DXFAttributes, DXFAttr, ExtendedTags
from .dxfobjects import none_subclass

ENTRY_NAME_CODE = 3

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
})


class DXFDictionary(DXFObject):
    """
    AutoCAD maintains items such as mline styles and group definitions as objects in dictionaries.
    Other applications are free to create and use their own dictionaries as they see fit. The prefix "ACAD_" is reserved
    for use by AutoCAD applications.

    DXFDictionary entries are (key, handle) values, so it can only store handles and nothing else, to store other
    values, you have to create a DXFDictionaryVar object, and store its handle.

    """
    TEMPLATE = ExtendedTags.from_text(_DICT_TPL)
    DXFATTRIBS = DXFAttributes(
        none_subclass,
        dictionary_subclass,
    )

    @property
    def AcDbDictinary(self):
        return self.tags.subclasses[1]

    @property
    def is_hard_owner(self):
        return bool(self.get_dxf_attrib('hard_owned', False))

    def keys(self):
        """
        Generator for the dictionary's keys.

        """
        return (item[0] for item in self.items())

    def items(self):
        """
        Generator for the dictionary's items (``(key, value)`` pairs).

        """
        key = ""
        for code, value in self.AcDbDictinary:
            if code == ENTRY_NAME_CODE:  # Entry name
                key = value
            elif code == 350:  # handle to entry object
                yield key, value

    def __getitem__(self, key):
        """
        Return the value for *key* if *key* is in the dictionary, else raises a :class:`KeyError()`.

        """
        return self.get(key)

    def __setitem__(self, key, value):
        """
        Add item *(key, value)* to dictionary.

        """
        return self.add(key, value)

    def __delitem__(self, key):
        """
        Remove element *key* from the dictionary. *KeyError* if *key* is not contained in the dictionary.

        """
        return self.remove(key)

    def __contains__(self, key):
        """
        Return *True* if the dictionary has a key *key*, else *False*.

        """
        return False if self._get_item_index(key) is None else True

    def __len__(self):
        """
        Return the number of items in the dictionary.

        """
        return self.count()

    def count(self):
        """
        Return the number of items in the dictionary.

        """
        return sum(1 for tag in self.AcDbDictinary if tag.code == ENTRY_NAME_CODE)

    def get(self, key, default=DXFKeyError):
        """
        Return the value (handle) for *key* if *key* is in the dictionary, else *default*, raises a *DXFKeyError*
        for *default*=DXFKeyError.

        """
        index = self._get_item_index(key)
        if index is None:
            if default is DXFKeyError:
                raise DXFKeyError("KeyError: '{}'".format(key))
            else:
                return default
        else:
            return self.AcDbDictinary[index + 1].value

    get_handle = get  # synonym

    def get_entity(self, key):
        """
        Get object referenced by handle associated by *key* as wrapped entity, raises a *KeyError* if *key* not exists.

        """
        handle = self.get(key)
        if self.drawing is not None:
            return self.dxffactory.wrap_handle(handle)
        else:
            return handle

    def add(self, key, value, code=350):
        """
        Add item ``(key, value)`` to dictionary. The key parameter *code* specifies the group code of the *value*
        data and defaults to ``350`` (soft-owner handle).

        """
        index = self._get_item_index(key)
        value_tag = DXFTag(code, value)
        content_tags = self.AcDbDictinary
        if index is None:  # create new entry
            content_tags.append(DXFTag(ENTRY_NAME_CODE, key))
            content_tags.append(value_tag)
        else:  # always replace existing values, until I understand the 281-tag (name mangling)
            content_tags[index + 1] = value_tag

    def remove(self, key):
        """
        Remove element *key* from the dictionary. Raises *DXFKeyError* if *key* is not contained in the
        dictionary. Deletes hard owned DXF objects from OBJECTS section.

        """
        if self.is_hard_owner:
            entity = self.get_entity(key)
            # Presumption: hard owned DXF objects always reside in the OBJECTS section
            self.drawing.objects.delete_entity(entity)

        index = self._get_item_index(key)
        if index is None:
            raise DXFKeyError("KeyError: '{}'".format(key))
        else:
            self._discard(index)

    def discard(self, key):
        """
        Remove *key* from the dictionary, if it is present. Does NOT delete hard owned entities!

        """
        self._discard(self._get_item_index(key))

    def _discard(self, index):
        if index:
            del self.AcDbDictinary[index:index + 2]  # remove key and value

    def _get_item_index(self, key):
        for index, tag in enumerate(self.AcDbDictinary):
            if tag.code == ENTRY_NAME_CODE and tag.value == key:
                return index
        return None

    def clear(self):
        """
        Removes all entries from DXFDictionary, and also deletes all hard owned DXF objects from OBJECTS section.

        """
        if self.is_hard_owner:
            self.delete_hard_owned_entries()
        try:
            start_index = self.AcDbDictinary.tag_index(code=ENTRY_NAME_CODE)
        except DXFValueError:  # no entries found
            return
        del self.AcDbDictinary[start_index:]

    def delete_hard_owned_entries(self):
        # Presumption: hard owned DXF objects always reside in the OBJECTS section
        objects = self.drawing.objects
        wrap = self.dxffactory.wrap_handle
        for key, handle in self.items():
            objects.delete_entity(wrap(handle))

    def add_new_dict(self, key):
        """
        Create a new sub dictionary.

        Args:
            key: name of the sub dictionary

        """
        dxf_dict = self.drawing.objects.add_dictionary(owner=self.dxf.handle)
        self.add(key, dxf_dict.dxf.handle)
        return dxf_dict

    def get_required_dict(self, key):
        try:
            dxf_dict = self.get_entity(key)
        except DXFKeyError:
            dxf_dict = self.add_new_dict(key)
        return dxf_dict

    def audit(self, auditor):
        if auditor.drawing.rootdict.tags is self.tags:  # if root dict, ignore owner tag because it is always #0
            codes = (330,)
        else:
            codes = None
        auditor.check_pointer_target_exists(self, ignore_codes=codes)

    def destroy(self):
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
    TEMPLATE = ExtendedTags.from_text(_DICT_WITH_DEFAULT_TPL)
    CLASS = ExtendedTags.from_text(_DICT_WITH_DEFAULT_CLS)
    DXFATTRIBS = DXFAttributes(
        none_subclass,
        dictionary_subclass,
        DefSubclass('AcDbDictionaryWithDefault', {
            'default': DXFAttr(340),
        }),
    )

    def get(self, key, default=DXFKeyError):
        """
        Return the value for *key* if *key* is in the dictionary, else the predefined dictionary wide *default*
        value. Parameter *default* is always ignored!

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
