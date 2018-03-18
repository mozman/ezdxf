# Created: 22.03.2011
# Copyright (c) 2011, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals
from ..lldxf.tags import DXFTag
from ..lldxf.extendedtags import ExtendedTags
from ..lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ..dxfentity import DXFEntity
from ..lldxf.const import DXFKeyError, DXFValueError

ENTRY_NAME_CODE = 3

none_subclass = DefSubclass(None, {
    'handle': DXFAttr(5),
    'owner': DXFAttr(330),
})


class DXFClass(DXFEntity):
    DXFATTRIBS = DXFAttributes(
        DefSubclass(None, {
            'name': DXFAttr(1),
            'cpp_class_name': DXFAttr(2),
            'app_name': DXFAttr(3),
            'flags': DXFAttr(90),
            'instance_count': DXFAttr(91, dxfversion='AC1018'),
            'was_a_proxy': DXFAttr(280),
            'is_an_entity': DXFAttr(281),
        }),
    )


class DXFObject(DXFEntity):
    def audit(self, auditor):
        auditor.check_pointer_target_exists(self, zero_pointer_valid=False)


_DICT_TPL = """  0
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


class DXFDictionary(DXFObject):
    TEMPLATE = ExtendedTags.from_text(_DICT_TPL)
    DXFATTRIBS = DXFAttributes(
        none_subclass,
        DefSubclass('AcDbDictionary', {
            'hard_owned': DXFAttr(280),
            'cloning': DXFAttr(281),
        }),
    )

    @property
    def AcDbDictinary(self):
        return self.tags.subclasses[1]

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
        Remove element *key* from the dictionary. *KeyError* if *key* is not contained in the
        dictionary.
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
        dictionary.
        """
        index = self._get_item_index(key)
        if index is None:
            raise DXFKeyError("KeyError: '{}'".format(key))
        else:
            self._discard(index)

    def discard(self, key):
        """
        Remove *key* from the dictionary if it is present.
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
        try:
            start_index = self.AcDbDictinary.tag_index(code=ENTRY_NAME_CODE)
        except DXFValueError:  # no entries found
            return
        del self.AcDbDictinary[start_index:]

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


_DICT_WITH_DEFAULT_CLS = """  0
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

_DICT_WITH_DEFAULT_TPL = """  0
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
        DefSubclass('AcDbDictionary', {
            'hard_owned': DXFAttr(280),
            'cloning': DXFAttr(281),
        }),
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


class XRecord(DXFObject):
    DXFATTRIBS = DXFAttributes(
        none_subclass,
        DefSubclass('AcDbXrecord', {
            'cloning': DXFAttr(280),
        }),
    )

    @property
    def content_tags(self):
        return self.tags.get_subclass('AcDbXrecord')

    @staticmethod
    def _adjust_index(index):
        return index if index < 0 else index + 2

    def __len__(self):
        # ignore first tags = (100, 'AcDbXrecord'), (280, ...)
        return len(self.content_tags) - 2

    def __getitem__(self, index):
        """
        Returns DXF tag at position *index*.
        """
        # skip first tags = (100, 'AcDbXrecord'), (280, ...)
        return self.content_tags[XRecord._adjust_index(index)]

    def __setitem__(self, index, dxftag):
        """
        Replace DXF tag at position *index* with *dxftag*.
        """
        # skip first tags = (100, 'AcDbXrecord'), (280, ...)
        self.content_tags[XRecord._adjust_index(index)] = dxftag

    def __iter__(self):
        """
        Iterate over data, yielding DXF tags as named tuple *(code, value)*.
        """
        tags = iter(self.content_tags)
        next(tags)  # skip (100, 'AcDbXrecord')
        next(tags)  # skip (280, ...)
        return tags

    def append(self, dxftag):
        """
        Append *dxftag* at the end of the tag list.
        """
        self.content_tags.append(dxftag)


class DXFDataTable(DXFObject):
    DXFATTRIBS = DXFAttributes(
        none_subclass,
        DefSubclass('AcDbDataTable', {
            'version': DXFAttr(70),
            'columns': DXFAttr(90),
            'rows': DXFAttr(91),
            'tabel_name': DXFAttr(1),
        }),
    )


_PLACEHOLDER_TPL = """  0
ACDBPLACEHOLDER
5
0
330
0
"""


class ACDBPlaceHolder(DXFEntity):
    TEMPLATE = ExtendedTags.from_text(_PLACEHOLDER_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, )
