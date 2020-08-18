#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
from typing import TYPE_CHECKING, BinaryIO, Iterable, List
import itertools

from ezdxf.lldxf import const
from ezdxf.lldxf import repair
from ezdxf.lldxf.types import (
    DXFTag, DXFVertex, DXFBinaryTag, POINT_CODES, BINARY_DATA, TYPE_TABLE,
)
from ezdxf.lldxf.loader import SectionDict
from ezdxf.tools.codepage import toencoding

if TYPE_CHECKING:
    from ezdxf.eztypes import Drawing

__all__ = ['read', 'readfile']


# TODO: recover
#  Mimic the CAD "RECOVER" command, try to read messy DXF files,
#  needs only as much work until the regular ezdxf loader can handle
#  and audit the DXF file.

def readfile(filename: str) -> 'Drawing':
    """ Read a DXF document from file system similar to :func:`ezdxf.readfile`,
    but this function will repair as much flaws as possible to take the document
    to a state, where the :class:`~ezdxf.audit.Auditor` could start his journey
    to repair further issues.

    Args:
        filename: file-system name of the DXF document to load

    """
    with open(filename, mode='rb') as fp:
        return read(fp)


def read(stream: BinaryIO) -> 'Drawing':
    """ Read a DXF document from a binary-stream similar to :func:`ezdxf.read`,
    But this function will detect the text encoding automatically and repair
    as much flaws as possible to take the document to a state, where the
    :class:`~ezdxf.audit.Auditor` could start his journey to repair further issues.

    Args:
        stream: data stream to load in binary read mode

    """
    from ezdxf.document import Drawing
    tags = safe_tag_loader(stream)
    sections = _rebuild_sections(tags)
    _merge_sections(sections)
    sections_dict = _build_section_dict(sections)
    tables = sections_dict['TABLES']
    _rebuild_tables(tables)
    _merge_tables(tables)
    doc = Drawing()
    doc._load_section_dict(sections_dict)
    return doc


def _rebuild_sections(tags: Iterable[DXFTag]) -> List:
    """ Rebuild sections:

    - move header variable tags (9, "$...") "outside" of sections into the
      HEADER section
    - remove other tags "outside" of sections
    - recover missing ENDSEC and EOF tags

    """
    return []


def _merge_sections(sections: List):
    """ Merge sections of same type. """
    pass


def _build_section_dict(sections: List) -> SectionDict:
    pass


def _rebuild_tables(tables: List):
    """ Rebuild TABLES section:

    - remove tags "outside" of tables

    """
    pass


def _merge_tables(tables: List):
    """ Merge TABLES of same type. """
    pass


DEFAULT_ENCODING = 'cp1252'


def safe_tag_loader(stream: BinaryIO) -> Iterable[DXFTag]:
    tags, detector_stream = itertools.tee(bytes_loader(stream), 2)
    encoding = detect_encoding(detector_stream)

    # Apply repair filter:
    tags = repair.filter_invalid_yz_point_codes(tags)
    tags = repair.tag_reorder_layer(tags)
    return byte_tag_compiler(tags, encoding)


def bytes_loader(stream: BinaryIO) -> Iterable[DXFTag]:
    """
    Yields :class:``DXFTag`` objects from a bytes `stream` (untrusted external
    source), skips all comment tags (group code == 999).

    ``DXFTag.code`` is always an ``int`` and ``DXFTag.value`` is always a
    raw bytes value without line endings. Works with file system streams and
    :class:`BytesIO` streams.

    Args:
        stream: byte stream

    Raises:
        DXFStructureError: Found invalid group code.

    """
    line = 1
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
                code = int(code)
            except ValueError:
                code = code.decode(DEFAULT_ENCODING)
                raise const.DXFStructureError(
                    f'Invalid group code "{code}" at line {line}.')
            else:
                if code != 999:
                    yield DXFTag(code, value.rstrip(b'\r\n'))
                line += 2
        else:
            return


DWGCODEPAGE = b'$DWGCODEPAGE'
ACADVER = b'$ACADVER'


def detect_encoding(tags: Iterable[DXFTag]) -> str:
    """ Detect text encoding from header variables $DWGCODEPAGE and $ACADVER
    out of a stream of DXFTag objects.

    Assuming a malformed DXF file:

    The header variables could reside outside of the HEADER section,
    an ENDSEC tag is not a reliable fact that no $DWGCODEPAGE or
    $ACADVER header variable will show up in the remaining tag stream.

    Worst case: DXF file without a $ACADVER var, and a $DWGCODEPAGE
    unequal to "ANSI_1252" at the end of the file.

    """
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
            return 'utf8' if dxfversion >= const.DXF2007 else encoding

    return DEFAULT_ENCODING


def byte_tag_compiler(tags: Iterable[DXFTag],
                      encoding=DEFAULT_ENCODING) -> Iterable[DXFTag]:
    """ Compiles DXF tag values imported by bytes_loader() into Python types.

    Raises DXFStructureError() for invalid float values and invalid coordinate
    values.

    Expects DXF coordinates written in x, y[, z] order, this is not required
    by the DXF standard, but nearly all CAD applications write DXF coordinates
    that (sane) way, there are older CAD applications (namely an older
    QCAD version) that write LINE coordinates in x1, x2, y1, y2 order, which
    does not work with tag_compiler(). For this cases use tag_reorder_layer()
    from the repair module to reorder the LINE coordinates.

        tag_compiler(tag_reorder_layer(bytes_loader(stream)))

    Args:
        tags: DXF tag generator of type bytes_loader()
        encoding: text encoding

    Raises:
        DXFStructureError: Found invalid DXF tag or unexpected coordinate order.

    """

    def error_msg(tag):
        code = tag.code
        value = tag.value.decode(encoding)
        return f'Invalid tag (code={code}, value="{value}") near line: {line}.'

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
                    raise const.DXFStructureError(
                        f"Missing required y coordinate near line: {line}.")
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
                    raise const.DXFStructureError(
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
                        raise const.DXFStructureError(
                            f'Invalid binary data near line: {line}.')
                yield tag
            else:  # just a single tag
                type_ = TYPE_TABLE.get(code, str)
                value: bytes = x.value
                if type_ is str:
                    if code == 0:
                        # remove white space from structure tags
                        value = x.value.strip()
                    yield DXFTag(code, value.decode(encoding))
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
                                raise const.DXFStructureError(error_msg(x))
                        else:
                            raise const.DXFStructureError(error_msg(x))
        except StopIteration:
            return
