# Purpose: trusted tag reader
# Created: 10.04.2016
# Copyright (C) 2016, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .types import DXFTag, is_point_code, cast_tag
from .const import DXFStructureError

DUMMY_TAG = DXFTag(999, '')


def StringTagger(s):
    """ Generates DXFTag() from trusted source - relies on
    well formed and error free DXF format. Does not skip comment
    tags 999.
    """

    lines = s.split('\n')
    if s.endswith('\n'):  # split() creates an extra item, if s ends with '\n'
        lines.pop()
    pos = 0

    def next_tag():
        return DXFTag(int(lines[pos]), lines[pos+1])

    count = len(lines)
    while pos < count:
        x = next_tag()
        pos += 2
        if is_point_code(x.code):
            y = next_tag()  # y coordinate is mandatory
            pos += 2
            if pos < count:
                z = next_tag()  # z coordinate just for 3d points
            else:  # if string s ends with a 2d point
                z = DUMMY_TAG
            if z.code == x.code + 20:
                pos += 2
                point = (x.code, (x.value, y.value, z.value))
            else:
                point = (x.code, (x.value, y.value))
            yield cast_tag(point)
        else:
            yield cast_tag(x)


def skip_comments(tagger, comments=None):
    if comments is None:
        comments = []
    for tag in tagger:
        if tag.code != 999:
            yield tag
        else:
            comments.append(tag.value)


def StreamTagger(stream):
    """ Generates DXFTag() from a stream. Does not skip comment 
    tags 999.
    """
    undo_tag = None

    def next_tag():
        code = stream.readline()
        value = stream.readline()
        if code and value:  # StringIO(): empty strings indicates EOF
            return DXFTag(int(code[:-1]), value[:-1])
        else:  # StringIO(): missing '\n' indicates EOF
            raise EOFError()

    while True:
        try:
            if undo_tag is not None:
                x = undo_tag
                undo_tag = None
            else:
                x = next_tag()
            if is_point_code(x.code):
                y = next_tag() # y coordinate is mandatory
                if y.code != x.code + 10:
                    raise DXFStructureError()
                z = next_tag()  # z coordinate just for 3d points
                if z.code == x.code + 20:
                    point = (x.code, (x.value, y.value, z.value))
                else:
                    point = (x.code, (x.value, y.value))
                    undo_tag = z
                yield cast_tag(point)
            else:  # just a single tag
                yield cast_tag(x)
        except EOFError:
            return
