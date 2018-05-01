# Purpose: untrusted stream tag reader, tag compiler for trusted and untrusted sources
# Created: 10.04.2016
# Copyright (c) 2016-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

from .types import DXFTag, DXFVertex, DXFBinaryTag
from .const import DXFStructureError
from .types import POINT_CODES, TYPE_TABLE, ustr, BINARAY_DATA
from ..tools.c23 import isstring


def internal_tag_compiler(s):
    """
    Generates DXFTag() from trusted (internal) source - relies on
    well formed and error free DXF format. Does not skip comment
    tags 999.

    Args:
        s: DXF unicode string, lines separated by universal line endings '\n'

    Yields: DXFTag() or inherited

    """
    assert isstring(s)
    lines = s.split('\n')
    # split() creates an extra item, if s ends with '\n',
    # but lines[-1] can be an empty string!!!
    if s.endswith('\n'):
        lines.pop()
    pos = 0
    count = len(lines)
    while pos < count:
        code = int(lines[pos])
        value = lines[pos+1]
        pos += 2
        if code in POINT_CODES:
            # next tag; y coordinate is mandatory - internal_tag_compiler relies on well formed DXF strings
            y = lines[pos+1]
            pos += 2
            if pos < count:
                # next tag; z coordinate just for 3d points
                z_code = int(lines[pos])
                z = lines[pos+1]
            else:  # if string s ends with a 2d point
                z_code, z = None, 0.
            if z_code == code+20:  # 3d point
                pos += 2
                point = (float(value), float(y), float(z))
            else:  # 2d point
                point = (float(value), float(y))
            yield DXFVertex(code, point)  # 2d/3d point
        elif code in BINARAY_DATA:
            yield DXFBinaryTag.from_string(code, value)
        else:  # single value tag: int, float or string
            yield DXFTag(code, TYPE_TABLE.get(code, ustr)(value))


def low_level_tagger(stream):
    """
    Generates DXFTag(code, value) tuples from a stream (untrusted external source) and does not optimize coordinates.
    Skip comment tags 999. code is always an int and value is always an unicode string without a trailing '\n'.
    Works with file system streams and StringIO() streams, only required feature is the readline() method.

    Args:
        stream: text stream

    Yields: DXFTag()

    Raises: DXFStructureError() for invalid group codes.
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
                if code != 999:  # skip comments
                    yield DXFTag(code, value.rstrip('\n'))
                line += 2
        else:
            return


def tag_compiler(tagger):
    """
    Compiles DXF tag values imported by low_level_tagger() into Python types.

    Raises DXFStructureError() for invalid float values and invalid coordinate values.

    Expects DXF coordinates written in x, y[, z] order, this is not required by the DXF standard, but nearly all CAD
    applications write DXF coordinates that (sane) way, there are older CAD applications (namely an older QCAD version)
    that write LINE coordinates in x1, x2, y1, y2 order, which does not work with tag_compiler(). For this cases use
    tag_reorder_layer() from the repair module to reorder the LINE coordinates::

        tag_compiler(tag_reorder_layer(low_level_tagger(stream)))

    Args:
        tagger: DXF tag generator/iterator like low_level_tagger() or skip_comments()

    Yields: DXFTag() or inherited

    Raises: DXFStructureError() for invalid dxf values and unexpected coordinate order.

    """
    def error_msg(tag):
        return 'Invalid tag (code={code}, value="{value}") near line: {line}.'.format(line=line, code=tag.code, value=tag.value)

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
                    raise DXFStructureError("Missing required y coordinate near line: {}.".format(line))
                z = next(tagger)  # z coordinate just for 3d points
                line += 2
                try:
                    if z.code == code + 20:  # it is a z-coordinate like (30, 0.0) for base x-code 10
                        point = (float(x.value), float(y.value), float(z.value))
                    else:
                        point = (float(x.value), float(y.value))
                        undo_tag = z
                except ValueError:  # internal exception
                    raise DXFStructureError('Invalid floating point values near line: {}.'.format(line))
                yield DXFVertex(code, point)
            elif code in BINARAY_DATA:
                try:
                    yield DXFBinaryTag.from_string(code, x.value)
                except ValueError:
                    raise DXFStructureError(error_msg(x))
            else:  # just a single tag; internal type casting, not types.cast_tag()
                try:
                    # fast path!
                    yield DXFTag(code, TYPE_TABLE.get(code, ustr)(x.value))
                except ValueError:  # internal exception
                    # slow path
                    if TYPE_TABLE.get(code, ustr) is int:  # ProE stores int values as floats :((
                        try:
                            yield DXFTag(code, int(float(x.value)))
                        except ValueError:
                            raise DXFStructureError(error_msg(x))
                    else:
                        raise DXFStructureError(error_msg(x))
        except StopIteration:
            return
