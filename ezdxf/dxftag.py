# Purpose: dxf tag type def
# Created: 30.04.2014
# Copyright (C) 2014, Manfred Moitzi
# License: MIT License

from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from collections import namedtuple
from .c23 import ustr

DXFTag = namedtuple('DXFTag', 'code value')
NONE_TAG = DXFTag(999999, 'NONE')
TAG_STRING_FORMAT = '%3d\n%s\n'


def point_tuple(value):
    return tuple(float(f) for f in value)


def _build_type_table(types):
    table = {}
    for caster, codes in types:
        for code in codes:
            table[code] = caster
    return table

TYPE_TABLE = _build_type_table([
    (ustr, range(0, 10)),
    (point_tuple, range(10, 20)),  # 2d or 3d points
    (float, range(20, 60)),  # code 20-39 belongs to 2d/3d points and should not appear alone
    (int, range(60, 100)),
    (ustr, range(100, 106)),
    (point_tuple, range(110, 113)),  # 110, 111, 112 - UCS definition
    (float, range(113, 150)),  # 113-139 belongs to UCS definition and should not appear alone
    (int, range(160, 170)),
    (int, range(170, 180)),
    (point_tuple, [210]),  # extrusion direction
    (float, range(211, 240)),  # code 220, 230 belongs to extrusion direction and should not appear alone
    (int, range(270, 290)),
    (int, range(290, 300)),  # bool 1=True 0=False
    (ustr, range(300, 370)),
    (int, range(370, 390)),
    (ustr, range(390, 400)),
    (int, range(400, 410)),
    (ustr, range(410, 420)),
    (int, range(420, 430)),
    (ustr, range(430, 440)),
    (int, range(440, 460)),
    (float, range(460, 470)),
    (ustr, range(470, 480)),
    (ustr, range(480, 482)),
    (ustr, range(999, 1010)),
    (point_tuple, range(1010, 1020)),
    (float, range(1020, 1060)),  # code 1020-1039 belongs to 2d/3d points and should not appear alone
    (int, range(1060, 1072)),
])


def is_point_code(code):
    return (10 <= code <= 19) or code == 210 or (110 <= code <= 112) or (1010 <= code <= 1019)


def is_point_tag(tag):
    return is_point_code(tag[0])


def cast_tag(tag, types=TYPE_TABLE):
    caster = types.get(tag[0], ustr)
    try:
        return DXFTag(tag[0], caster(tag[1]))
    except ValueError:
        if caster is int:  # convert float to int
            return DXFTag(tag[0], int(float(tag[1])))
        else:
            raise


def cast_tag_value(code, value, types=TYPE_TABLE):
    return types.get(code, ustr)(value)


def tag_type(code):
    try:
        return TYPE_TABLE[code]
    except KeyError:
        raise ValueError("Invalid tag code: {}".format(code))


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
