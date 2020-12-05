# cython: language_level=3
# cython: profile = False
# distutils: language = c++
# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import Iterable, TextIO, Iterator, List
from ezdxf.audit import AuditError
from ezdxf.lldxf.const import (
    DXFStructureError, DEFAULT_ENCODING, DXF2007
)
from ezdxf.lldxf.encoding import (
    has_dxf_unicode,
    decode_dxf_unicode,
)
from ezdxf.lldxf.types import (
    DXFTag, POINT_CODES, DXFVertex, DXFBinaryTag, BINARY_DATA, TYPE_TABLE,
)
from ezdxf.tools.codepage import toencoding

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

# The acceleration of ascii_tag_loader() and tag_compiler() was not successful.
# Next attempt is to use memory mapped files and process the binary data
# without the stream overhead, this requires detecting the encoding from the
# file and bytes decoding on the fly.
#
# This is similar to the "recover" loading procedure.
#
# If this approach is successful it is maybe better to rewrite the existing
# loading infrastructure. Loading binary DXF files should be preserved
# and loading from a (web) stream has a separated slower processing path.
#
# Optimizing for loading DXF files from the file system seems to be reasonable
# because this is the most common use case. A slower processing time for web
# apps is the price to pay.

# First test by adapting the loading procedure from the recover module:
def binary_loader(fname: str) -> Iterable[DXFTag]:
    cdef int line = 1
    cdef int group_code
    with open(fname, 'rb') as stream:
        while True:
            try:
                code = stream.readline()
                value = stream.readline()
            except EOFError:
                # EOFError indicates a DXFStructureError, but should be handled
                # in top layers.
                return

            # ByteIO(): empty strings indicates EOF
            if code and value:
                try:
                    group_code = int(code)
                except ValueError:
                    code = code.decode(DEFAULT_ENCODING)
                    raise DXFStructureError(
                        f'Invalid group code "{code}" at line {line}.')
                else:
                    if group_code != 999:
                        yield DXFTag(group_code, value.rstrip(b'\r\n'))
                    line += 2
            else:
                return

DWGCODEPAGE = b'$DWGCODEPAGE'
ACADVER = b'$ACADVER'

def detect_encoding(tags: Iterable[DXFTag]) -> str:
    encoding = None
    dxfversion = None
    next_tag = None

    for code, value in tags:
        if code == 9:
            if value == DWGCODEPAGE:
                next_tag = DWGCODEPAGE  # e.g. (3, "ANSI_1252")
            elif value == ACADVER:
                next_tag = ACADVER  # e.g. (1, "AC1012")
        elif code == 3 and next_tag == DWGCODEPAGE:
            encoding = toencoding(value.decode(DEFAULT_ENCODING))
            next_tag = None
        elif code == 1 and next_tag == ACADVER:
            dxfversion = value.decode(DEFAULT_ENCODING)
            next_tag = None

        if encoding and dxfversion:
            return 'utf8' if dxfversion >= DXF2007 else encoding

    return DEFAULT_ENCODING

def byte_tag_compiler(tags: Iterable[DXFTag],
                      encoding=DEFAULT_ENCODING,
                      messages: List = None,
                      errors: str = 'surrogateescape',
                      ) -> Iterable[DXFTag]:

    def error_msg(tag):
        code = tag.code
        value = tag.value.decode(encoding)
        return f'Invalid tag ({code}, "{value}") near line: {line}.'

    if messages is None:
        messages = []
    tags = iter(tags)
    undo_tag = None
    line = 0
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
                y = next(tags)  # y coordinate is mandatory
                line += 2
                # e.g. y-code for x-code=10 is 20
                if y.code != code + 10:
                    raise DXFStructureError(
                        f"Missing required y-coordinate near line: {line}.")
                # optional z coordinate
                z = next(tags)
                line += 2
                try:
                    # is it a z-coordinate like (30, 0.0) for base x-code=10
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
                # maybe pre compiled in low level tagger (binary DXF)
                if isinstance(x, DXFBinaryTag):
                    tag = x
                else:
                    try:
                        tag = DXFBinaryTag.from_string(code, x.value)
                    except ValueError:
                        raise DXFStructureError(
                            f'Invalid binary data near line: {line}.')
                yield tag
            else:  # just a single tag
                type_ = TYPE_TABLE.get(code, str)
                value: bytes = x.value
                if type_ is str:
                    if code == 0:
                        # remove white space from structure tags
                        value = x.value.strip().upper()
                    try:  # 2 stages to document decoding errors
                        str_ = value.decode(encoding, errors='strict')
                    except UnicodeDecodeError:
                        str_ = value.decode(encoding, errors=errors)
                        messages.append((
                            AuditError.DECODING_ERROR,
                            f'Fixed unicode decoding error near line {line}'
                        ))

                    # Convert DXF unicode notation "\U+xxxx" to unicode,
                    # but exclude structure tags (code>0):
                    if code and has_dxf_unicode(str_):
                        str_ = decode_dxf_unicode(str_)

                    yield DXFTag(code, str_)
                else:
                    try:
                        # fast path for int and float
                        yield DXFTag(code, type_(value))
                    except ValueError:
                        # slow path - ProE stores int values as floats :((
                        if type_ is int:
                            try:
                                yield DXFTag(code, int(float(x.value)))
                            except ValueError:
                                raise DXFStructureError(error_msg(x))
                        else:
                            raise DXFStructureError(error_msg(x))
        except StopIteration:
            return
