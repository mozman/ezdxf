# cython: language_level=3
# cython: profile = False
# distutils: language = c++
# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import Iterable, TextIO, Iterator
from ezdxf.lldxf.types import (
    DXFTag, POINT_CODES, DXFVertex, DXFBinaryTag, BINARY_DATA, TYPE_TABLE
)
from ezdxf.lldxf.const import DXFStructureError

def ascii_tags_loader(stream: TextIO,
                      skip_comments: bool = True) -> Iterable[DXFTag]:
    cdef int line = 1
    cdef bint yield_comments = not skip_comments
    cdef int group_code
    readline = stream.readline
    _DXFTag = DXFTag

    while True:
        try:
            code = readline()
            value = readline()
        except EOFError:
            return
        if code and value:  # StringIO(): empty strings indicates EOF
            try:
                group_code = int(code)
            except ValueError:
                raise DXFStructureError(
                    f'Invalid group code "{code}" at line {line}.')
            else:
                if group_code != 999 or yield_comments:
                    yield _DXFTag(group_code, value.rstrip('\n'))
                line += 2
        else:
            return

def tag_compiler(tags: Iterator[DXFTag]) -> Iterable[DXFTag]:
    def error_msg(tag):
        return f'Invalid tag (code={tag.code}, value="{tag.value}") ' \
               f'near line: {line}.'

    undo_tag = None
    cdef int line = 0
    cdef int code

    while True:
        try:
            if undo_tag is not None:
                x = undo_tag
                undo_tag = None
            else:
                x = next(tags)
                line += 2
            code = x.code
            if code in POINT_CODES:
                # y-axis is mandatory
                y = next(tags)
                line += 2
                if y.code != code + 10:  # like 20 for base x-code 10
                    raise DXFStructureError(
                        f"Missing required y coordinate near line: {line}.")
                # z-axis just for 3d points
                z = next(tags)
                line += 2
                try:
                    # z-axis like (30, 0.0) for base x-code 10
                    if z.code == code + 20:
                        point = (float(x.value), float(y.value), float(z.value))
                    else:
                        point = (float(x.value), float(y.value))
                        undo_tag = z
                except ValueError:
                    raise DXFStructureError(
                        f'Invalid floating point values near line: {line}.')
                yield DXFVertex(code, point)
            elif code in BINARY_DATA:
                # Maybe pre compiled in low level tagger (binary DXF):
                if isinstance(x, DXFBinaryTag):
                    tag = x
                else:
                    try:
                        tag = DXFBinaryTag.from_string(code, x.value)
                    except ValueError:
                        raise DXFStructureError(
                            f'Invalid binary data near line: {line}.')
                yield tag
            else:  # Just a single tag
                try:
                    # Fast path!
                    if code == 0:
                        value = x.value.strip()
                    else:
                        value = x.value
                    yield DXFTag(code, TYPE_TABLE.get(code, str)(value))
                except ValueError:
                    # ProE stores int values as floats :((
                    if TYPE_TABLE.get(code, str) is int:
                        try:
                            yield DXFTag(code, int(float(x.value)))
                        except ValueError:
                            raise DXFStructureError(error_msg(x))
                    else:
                        raise DXFStructureError(error_msg(x))
        except StopIteration:
            return
