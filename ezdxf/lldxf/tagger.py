# Purpose: trusted string tag reader & stream tag reader
# Created: 10.04.2016
# Copyright (C) 2016, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .types import DXFTag, cast_tag
from .const import DXFStructureError

DUMMY_TAG = DXFTag(999, '')


def internal_tag_compiler(s):
    """
    Generates DXFTag() from trusted (internal) source - relies on
    well formed and error free DXF format. Does not skip comment
    tags 999.
    """
    from .types import POINT_CODES
    lines = s.split('\n')
    if s.endswith('\n'):  # split() creates an extra item, if s ends with '\n'
        lines.pop()
    pos = 0
    count = len(lines)
    while pos < count:
        x = DXFTag(int(lines[pos]), lines[pos+1])
        pos += 2
        code = x.code
        if code in POINT_CODES:
            # next tag; y coordinate is mandatory - internal_tag_compiler relies on well formed DXF strings
            y = DXFTag(int(lines[pos]), lines[pos+1])
            pos += 2
            if pos < count:
                # next tag; z coordinate just for 3d points
                z = DXFTag(int(lines[pos]), lines[pos+1])
            else:  # if string s ends with a 2d point
                z = DUMMY_TAG
            if z.code == code + 20:
                pos += 2
                point = (float(x.value), float(y.value), float(z.value))
            else:
                point = (float(x.value), float(y.value))
            yield DXFTag(code, point)
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


def low_level_tagger(stream):
    """
    Generates DXFTag(code, value) tuples from a stream (untrusted external source) and does not optimize coordinates.
    Does not skip comment tags 999. code is always an int and value is always an unicode string without a trailing '\n'.
    Works with file system streams and StringIO() streams. Raises DXFStructureError() for invalid group codes.
    """
    line = 1
    while True:
        try:
            code = stream.readline()
            value = stream.readline()  # if throws EOFError -> DXFStructureError, but should be handled in upper layers
        except EOFError:
            return
        if code and value:  # StringIO(): empty strings indicates EOF
            try:
                code = int(code)
            except ValueError:
                raise DXFStructureError('Invalid group code "{}" at line {}.'.format(code, line))
            else:
                yield DXFTag(code, value.rstrip('\n'))
                line += 2
        else:
            return


def tag_compiler(tagger):
    """
    Compiles DXF tag values imported by low_level_tagger() into Python types.

    Does not skip comment tags 999. Raises DXFStructureError() for invalid float values and invalid coordinate values.

    Expects DXF coordinates written in x, y[, z] order, this is not required by the DXF standard, but nearly all CAD
    applications write DXF coordinates that (sane) way, there are older CAD applications (namely an older QCAD version)
    that write LINE coordinates in x1, x2, y1, y2 order, which does not work with tag_compiler(). For this cases use
    tag_reorder_layer() from the repair module to reorder the LINE coordinates::

        tag_compiler(tag_reorder_layer(low_level_tagger(stream)))

    """
    from .types import POINT_CODES

    undo_tag = None
    line = 0
    while True:
        try:
            if undo_tag is not None:
                x = undo_tag
                undo_tag = None
            else:
                x = next(tagger)
                line += 2
            code = x.code
            if code in POINT_CODES:
                y = next(tagger)  # y coordinate is mandatory
                line += 2
                if y.code != code + 10:  # like 20 for base x-code 10
                    raise DXFStructureError("Missing required y coordinate near line: {}.".format(line.counter))
                z = next(tagger)  # z coordinate just for 3d points
                line += 2
                try:
                    if z.code == code + 20:  # it is a z-coordinate like (30, 0.0) for base x-code 10
                        point = (float(x.value), float(y.value), float(z.value))
                    else:
                        point = (float(x.value), float(y.value))
                        undo_tag = z
                except ValueError:  # internal exception
                    raise DXFStructureError('Invalid floating point values near line: {}.'.format(line.counter))
                yield DXFTag(code, point)
            else:  # just a single tag
                try:
                    yield cast_tag(x)
                except ValueError:  # internal exception
                    raise DXFStructureError('Invalid tag (code={code}, value="{value}") near line: {line}.'.format(
                        line=line,
                        code=x.code,
                        value=x.value,
                    ))
        except StopIteration:
            return
