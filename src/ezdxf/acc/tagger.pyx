# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
"""
Cython-optimized ASCII DXF tag loading and compilation.

"""

from typing import Iterator, TextIO
from libc.stdlib cimport atoi, strtod

# Import the DXF tag types from the pure Python module
from ezdxf.lldxf.types import (
    DXFTag,
    DXFVertex,
    DXFBinaryTag,
)
from ezdxf.lldxf.const import DXFStructureError


cdef inline bint is_point_code(int code) noexcept nogil:
    """Fast inline check for point codes without Python overhead."""
    return (
        code == 10 or code == 11 or code == 12 or code == 13 or
        code == 14 or code == 15 or code == 16 or code == 17 or
        code == 18 or code == 110 or code == 111 or code == 112 or
        code == 210 or code == 211 or code == 212 or code == 213 or
        code == 1010 or code == 1011 or code == 1012 or code == 1013
    )


cdef inline bint is_double_code(int code) noexcept nogil:
    """Fast inline check for double/float codes."""
    return (
        (10 <= code < 60) or (110 <= code < 150) or
        (210 <= code < 240) or (460 <= code < 470) or
        (1010 <= code < 1060)
    )


cdef inline bint is_int_code(int code) noexcept nogil:
    """Fast inline check for integer codes (INT16, INT32, INT64)."""
    return (
        # INT16: 60-79, 170-179, 270-289, 370-389, 400-409, 1060-1070
        (60 <= code < 80) or (170 <= code < 180) or
        (270 <= code < 290) or (370 <= code < 390) or
        (400 <= code < 410) or (1060 <= code <= 1070) or
        # INT32: 90-99, 420-429, 440-449, 450-459, 1071
        (90 <= code < 100) or (420 <= code < 430) or
        (440 <= code < 460) or (code == 1071) or
        # INT64: 160-169
        (160 <= code < 170)
    )


cdef inline bint is_binary_data_code(int code) noexcept nogil:
    """Fast inline check for binary data codes."""
    return (
        (310 <= code <= 319) or code == 1004
    )


def ascii_tags_loader(stream: TextIO, skip_comments: bool = True) -> Iterator[DXFTag]:
    """Cython-optimized version of ascii_tags_loader().

    Yields DXFTag objects from a text stream (untrusted external source)
    and does not optimize coordinates. Comment tags (group code == 999)
    will be skipped if skip_comments is True.

    Args:
        stream: text stream
        skip_comments: skip comment tags (group code == 999) if True

    Raises:
        DXFStructureError: Found invalid group code.
    """
    cdef int line = 1
    cdef bint eof = False
    cdef bint yield_comments = not skip_comments
    cdef int group_code
    cdef str code_str
    cdef str value
    cdef bytes code_bytes
    cdef char* code_ptr

    # Localize attributes for faster access
    readline = stream.readline
    _DXFTag = DXFTag

    while not eof:
        code_str = readline()
        if code_str:  # empty string indicates EOF
            # Fast C-level string to int conversion
            try:
                code_bytes = code_str.encode('ascii')
                code_ptr = code_bytes
                group_code = atoi(code_ptr)
            except (UnicodeEncodeError, ValueError):
                raise DXFStructureError(f'Invalid group code "{code_str}" at line {line}.')
        else:
            return

        value = readline()
        if value:  # empty string indicates EOF
            value = value.rstrip("\n")
            if group_code == 0 and value == "EOF":
                eof = True  # yield EOF tag but ignore any data beyond EOF
            if group_code != 999 or yield_comments:
                yield _DXFTag(group_code, value)
            line += 2
        else:
            return


def tag_compiler(tags: Iterator[DXFTag]) -> Iterator[DXFTag]:
    """Cython-optimized version of tag_compiler().

    Compiles DXF tag values imported by ascii_tags_loader() into Python types.

    Raises DXFStructureError() for invalid float values and invalid coordinate values.

    Args:
        tags: DXF tag generator e.g. ascii_tags_loader()

    Raises:
        DXFStructureError: Found invalid DXF tag or unexpected coordinate order.
    """
    cdef int line = 0
    cdef int code
    cdef object x, y, z
    cdef object undo_tag = None
    cdef tuple point
    cdef double x_val, y_val, z_val
    cdef str value_str
    cdef bytes value_bytes
    cdef char* value_ptr
    cdef char* endptr
    cdef long int_value

    def error_msg(tag):
        return f'Invalid tag (code={tag.code}, value="{tag.value}") near line: {line}.'

    while True:
        try:
            if undo_tag is not None:
                x = undo_tag
                undo_tag = None
            else:
                x = next(tags)
                line += 2

            code = x.code

            # Handle point codes (coordinates)
            if is_point_code(code):
                # y-axis is mandatory
                y = next(tags)
                line += 2
                if y.code != code + 10:
                    raise DXFStructureError(
                        f"Missing required y coordinate near line: {line}."
                    )

                # z-axis just for 3d points
                z = next(tags)
                line += 2
                try:
                    # z-axis like (30, 0.0) for base x-code 10
                    if z.code == code + 20:
                        # 3D point - use C-level float conversion
                        value_str = x.value
                        value_bytes = value_str.encode('ascii')
                        value_ptr = value_bytes
                        x_val = strtod(value_ptr, &endptr)

                        value_str = y.value
                        value_bytes = value_str.encode('ascii')
                        value_ptr = value_bytes
                        y_val = strtod(value_ptr, &endptr)

                        value_str = z.value
                        value_bytes = value_str.encode('ascii')
                        value_ptr = value_bytes
                        z_val = strtod(value_ptr, &endptr)

                        point = (x_val, y_val, z_val)
                    else:
                        # 2D point
                        value_str = x.value
                        value_bytes = value_str.encode('ascii')
                        value_ptr = value_bytes
                        x_val = strtod(value_ptr, &endptr)

                        value_str = y.value
                        value_bytes = value_str.encode('ascii')
                        value_ptr = value_bytes
                        y_val = strtod(value_ptr, &endptr)

                        point = (x_val, y_val)
                        undo_tag = z
                except (ValueError, UnicodeEncodeError):
                    raise DXFStructureError(
                        f"Invalid floating point values near line: {line}."
                    )
                yield DXFVertex(code, point)

            # Handle binary data
            elif is_binary_data_code(code):
                if isinstance(x, DXFBinaryTag):
                    tag = x
                else:
                    try:
                        tag = DXFBinaryTag.from_string(code, x.value)
                    except ValueError:
                        raise DXFStructureError(
                            f"Invalid binary data near line: {line}."
                        )
                yield tag

            # Handle single tags with type conversion
            else:
                try:
                    value_str = x.value
                    # Fast path for structure markers (group code 0)
                    if code == 0:
                        value = value_str.strip()
                        yield DXFTag(code, value)
                    # Fast C-level conversion for floats
                    elif is_double_code(code):
                        value_bytes = value_str.encode('ascii')
                        value_ptr = value_bytes
                        yield DXFTag(code, strtod(value_ptr, &endptr))
                    # Fast C-level conversion for ints
                    elif is_int_code(code):
                        value_bytes = value_str.encode('ascii')
                        value_ptr = value_bytes
                        int_value = atoi(value_ptr)
                        yield DXFTag(code, int_value)
                    # String value (default)
                    else:
                        yield DXFTag(code, value_str)

                except (ValueError, UnicodeEncodeError):
                    # ProE stores int values as floats :((
                    if is_int_code(code):
                        try:
                            yield DXFTag(code, int(float(x.value)))
                        except ValueError:
                            raise DXFStructureError(error_msg(x))
                    else:
                        raise DXFStructureError(error_msg(x))

        except StopIteration:
            return


