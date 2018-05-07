# Created: 30.04.2014
# Copyright (c) 2014-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from array import array
from itertools import chain
from ..tools.c23 import ustr, reprlib, byte_to_hexstr, encode_hex_code_string_to_bytes

TAG_STRING_FORMAT = '%3d\n%s\n'
POINT_CODES = {10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 110, 111, 112, 210, 1010, 1011, 1012, 1013, 1014, 1015, 1016,
               1017, 1018, 1019, }

GENERAL_MARKER = 0
SUBCLASS_MARKER = 100
APP_DATA_MARKER = 102
EXT_DATA_MARKER = 1001
GROUP_MARKERS = {GENERAL_MARKER, SUBCLASS_MARKER, APP_DATA_MARKER, EXT_DATA_MARKER}
BINARY_FLAGS = {70, 90}
HANDLE_CODES = {5, 105}
POINTER_CODES = set(chain(range(320, 370), range(390, 400), (480, 481, 1005)))
HEX_HANDLE_CODES = set(chain(HANDLE_CODES, POINTER_CODES))
BINARAY_DATA = {310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 1004}


class DXFTag(object):
    __slots__ = ('code', '_value')

    def __init__(self, code, value):
        self.code = code
        self._value = value

    def __str__(self):
        return str((self.code, self.value))

    def __repr__(self):
        return "DXFTag{}".format(str(self))

    @property
    def value(self):
        return self._value

    def __getitem__(self, item):
        return (self.code, self.value)[item]

    def __iter__(self):
        yield self.code
        yield self.value

    def __eq__(self, other):
        return (self.code, self.value) == other

    # for Python 2.7 required
    def __ne__(self, other):
        return (self.code, self.value) != other

    def dxfstr(self):
        return TAG_STRING_FORMAT % (self.code, self._value)

    def clone(self):
        return self.__class__(self.code, self._value)


NONE_TAG = DXFTag(None, None)


class DXFVertex(DXFTag):
    __slots__ = ('code', '_value')

    def __init__(self, code, value):
        super(DXFVertex, self).__init__(code, array('d', value))

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return "DXFVertex({}, {})".format(self.code, str(self))

    @property
    def value(self):
        return tuple(self._value)

    def dxftags(self):
        c = self.code
        return ((code, value) for code, value in zip((c, c+10, c+20), self.value))

    def dxfstr(self):
        return ''.join(TAG_STRING_FORMAT % tag for tag in self.dxftags())


class DXFBinaryTag(DXFTag):
    __slots__ = ('code', '_value')

    def __str__(self):
        return "({}, {})".format(self.code, self.tostring())

    def __repr__(self):
        return "DXFBinaryTag({}, {})".format(self.code, reprlib.repr(self.tostring()))

    def tostring(self):  # value to string
        return ''.join(byte_to_hexstr(b) for b in self.value)

    def dxfstr(self):
        return TAG_STRING_FORMAT % (self.code, self.tostring())

    @classmethod
    def from_string(cls, code, value):
        return cls(code, encode_hex_code_string_to_bytes(value))


# TODO: test tuples_to_tags()
def tuples_to_tags(iterable):
    for code, value in iterable:
        if code in POINT_CODES:
            yield DXFVertex(code, value)
        elif code in BINARAY_DATA:
            yield DXFBinaryTag.from_string(code, value)
        else:
            yield DXFTag(code, value)


def _build_type_table(types):
    table = {}
    for caster, codes in types:
        for code in codes:
            table[code] = caster
    return table


TYPE_TABLE = _build_type_table([
    # all group code < 0 are spacial tags for internal use, but not accessible by get_dxf_attrib()
    (float, range(10, 60)),
    (int, range(60, 100)),
    (float, range(110, 150)),
    (int, range(160, 170)),
    (int, range(170, 180)),
    (float, range(210, 240)),
    (int, range(270, 290)),
    (int, range(290, 300)),  # bool 1=True 0=False
    (int, range(370, 390)),
    (int, range(400, 410)),
    (int, range(420, 430)),
    (int, range(440, 460)),
    (float, range(460, 470)),
    (float, range(1010, 1060)),
    (int, range(1060, 1072)),
])


def is_binary_data(code):
    return code in BINARAY_DATA


def is_pointer_code(code):
    return code in POINTER_CODES


def is_point_code(code):
    return code in POINT_CODES


def is_point_tag(tag):
    return tag[0] in POINT_CODES


def cast_tag_value(code, value, types=TYPE_TABLE):
    return types.get(code, ustr)(value)


def tag_type(code):
    return TYPE_TABLE.get(code, ustr)


def strtag(tag):
    return TAG_STRING_FORMAT % tuple(tag)

