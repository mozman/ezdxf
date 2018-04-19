# Created: 30.04.2014
# Copyright (c) 2014-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from collections import namedtuple
from itertools import chain
from ..tools.c23 import ustr
from .const import DXFValueError

DXFTag = namedtuple('DXFTag', 'code value')
NONE_TAG = DXFTag(None, None)
TAG_STRING_FORMAT = '%3d\n%s\n'


def point_tuple(value):
    return tuple(float(f) for f in value)


def _build_type_table(types):
    table = {}
    for caster, codes in types:
        for code in codes:
            table[code] = caster
    return table


def internal_type(value):
    return value


TYPE_TABLE = _build_type_table([
    (internal_type, (-10, )),  # spacial tags for internal use
    (point_tuple, range(10, 20)),  # 2d or 3d points
    (float, range(20, 60)),  # code 20-39 belongs to 2d/3d points and should not appear alone
    (int, range(60, 100)),
    (point_tuple, range(110, 113)),  # 110, 111, 112 - UCS definition
    (float, range(113, 150)),  # 113-139 belongs to UCS definition and should not appear alone
    (int, range(160, 170)),
    (int, range(170, 180)),
    (point_tuple, [210]),  # extrusion direction
    (float, range(211, 240)),  # code 220, 230 belongs to extrusion direction and should not appear alone
    (int, range(270, 290)),
    (int, range(290, 300)),  # bool 1=True 0=False
    (int, range(370, 390)),
    (int, range(400, 410)),
    (int, range(420, 430)),
    (int, range(440, 460)),
    (float, range(460, 470)),
    (point_tuple, range(1010, 1020)),
    (float, range(1020, 1060)),  # code 1020-1039 belongs to 2d/3d points and should not appear alone
    (int, range(1060, 1072)),
])

POINT_CODES = frozenset([
    10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
    110, 111, 112, 210,
    1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019,
])

GENERAL_MARKER = 0
SUBCLASS_MARKER = 100
APP_DATA_MARKER = 102
EXT_DATA_MARKER = 1001
GROUP_MARKERS = frozenset([GENERAL_MARKER, SUBCLASS_MARKER, APP_DATA_MARKER, EXT_DATA_MARKER])
BINARY_FLAGS = frozenset([70, 90])
HANDLE_CODES = frozenset([5, 105])
POINTER_CODES = frozenset(chain(range(320, 370), range(390, 400), (480, 481, 1005)))
HEX_HANDLE_CODES = frozenset(chain(HANDLE_CODES, POINTER_CODES))


def is_pointer_code(code):
    return code in POINTER_CODES


def is_point_code(code):
    return code in POINT_CODES


def is_point_tag(tag):
    return tag[0] in POINT_CODES


def cast_tag(tag, types=TYPE_TABLE):
    try:
        return DXFTag(tag[0], types.get(tag[0], ustr)(tag[1]))
    except ValueError:  # internal exception
        raise DXFValueError('Casting error for tag({0[0]}, {0[1]}).'.format(tag))


def cast_tag_value(code, value, types=TYPE_TABLE):
    return types.get(code, ustr)(value)


def tag_type(code):
    return TYPE_TABLE.get(code, ustr)


def strtag(tag):
    return TAG_STRING_FORMAT % tag


def strtag2(tag):
    code = tag.code
    if is_point_code(code):
        s = ""
        for coord in tag.value:
            s += strtag(DXFTag(code, coord))
            code += 10
        return s
    else:
        return strtag(tag)


def convert_tags_to_text_lines(line_tags):
    """ *line_tags* are tags with code 1 or 3, tag with code 3 is the tail of previous line with more than 255 chars.

    yield strings
    """
    line_tags = iter(line_tags)
    try:
        line = next(line_tags).value  # raises StopIteration
    except StopIteration:
        return
    while True:
        try:
            tag = next(line_tags)
        except StopIteration:
            if line:
                yield line
            return
        if tag.code == 3:
            line += tag.value
            continue
        yield line
        line = tag.value


def convert_text_lines_to_tags(text_lines):
    for line in text_lines:
        yield DXFTag(1, line[:255])
        if len(line) > 255:
            yield DXFTag(3, line[255:])  # tail (max. 255 chars), what if line > 510 chars???


