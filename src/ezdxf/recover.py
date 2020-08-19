#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
from typing import (
    TYPE_CHECKING, BinaryIO, Iterable, List, Callable, Tuple, Dict
)
import itertools
import logging

from ezdxf.lldxf import const
from ezdxf.lldxf import repair
from ezdxf.lldxf.types import (
    DXFTag, DXFVertex, DXFBinaryTag, POINT_CODES, BINARY_DATA, TYPE_TABLE,
    MAX_GROUP_CODE,
)
from ezdxf.lldxf.tags import group_tags, Tags
from ezdxf.tools.codepage import toencoding

logger = logging.getLogger('ezdxf')

if TYPE_CHECKING:
    from ezdxf.eztypes import Drawing, Auditor

__all__ = ['read', 'auto_read', 'readfile', 'auto_readfile']


# TODO: recover
#  Mimic the CAD "RECOVER" command, try to read messy DXF files,
#  needs only as much work until the regular ezdxf loader can handle
#  and audit the DXF file.

def auto_readfile(filename: str) -> Tuple['Drawing', 'Auditor']:
    """ Read a DXF document from file system similar to :func:`ezdxf.readfile`,
    but this function will repair as much flaws as possible,  runs the required
    audit process automatically and returns the result.

    Args:
        filename: file-system name of the DXF document to load

    """

    with open(filename, mode='rb') as fp:
        return auto_read(fp)


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


def auto_read(stream: BinaryIO) -> Tuple['Drawing', 'Auditor']:
    """ Read a DXF document from a binary-stream similar to :func:`ezdxf.read`,
    But this function will detect the text encoding automatically and repair
    as much flaws as possible, runs the required audit process automatically
    and returns the result.

    Args:
        stream: data stream to load in binary read mode

    """
    doc = read(stream)
    return doc, doc.audit()


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
    sections_dict = _build_section_dict(sections)
    tables = sections_dict.get('TABLES')
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

    def close_section():
        # ENDSEC tag is not collected
        nonlocal collector, inside_section
        if inside_section:
            sections.append(collector)
        else:  # missing SECTION
            # ignore this tag, it is even not an orphan
            logger.warning(
                'DXF structure error: ENDSEC with preceding SECTION.')
        collector = []
        inside_section = False

    def open_section():
        nonlocal inside_section
        if inside_section:  # missing ENDSEC
            logger.warning('DXF structure error: missing ENDSEC.')
            close_section()
        collector.append(tag)
        inside_section = True

    def process_structure_tag():
        if value == 'SECTION':
            open_section()
        elif value == 'ENDSEC':
            close_section()
        elif value == 'EOF':
            if inside_section:
                logger.warning('DXF structure error: missing ENDSEC.')
                close_section()
        else:
            collect()

    def collect():
        if inside_section:
            collector.append(tag)
        else:
            logger.warning(
                f'DXF structure error: found tag outside section: '
                f'({code}, {value}')
            orphans.append(tag)

    orphans = []
    sections = []
    collector = []
    inside_section = False
    for tag in tags:
        code, value = tag
        if code == 0:
            process_structure_tag()
        else:
            collect()

    sections.append(orphans)
    return sections


MANAGED_SECTIONS = {
    'CLASSES', 'TABLES', 'BLOCKS', 'ENTITIES', 'OBJECTS', 'ACDSDATA'
}


def _build_section_dict(sections: List) -> Dict[str, List[Tags]]:
    """ Merge sections of same type. """

    def add_section(name: str, tags):
        if name in section_dict:
            section_dict[name].extend(tags[2:])
        else:
            section_dict[name] = tags

    orphans = sections.pop()
    section_dict = dict()
    for section in sections:
        code, name = section[1]
        if code == 2:
            add_section(name, section)
        else:  # invalid section name tag e.g. (2, "HEADER")
            logger.warning(
                'DXF structure error: missing section name tag, ignore whole '
                'section.')

    header = section_dict.setdefault('HEADER', [
        DXFTag(0, 'SECTION'),
        DXFTag(2, 'HEADER'),
    ])
    _rescue_orphaned_header_vars(header, orphans)
    for name, section in section_dict.items():
        if name in MANAGED_SECTIONS:
            section_dict[name] = list(group_tags(sections, 0))
    return section_dict


def _rescue_orphaned_header_vars(
        header: List[DXFTag],
        orphans: Iterable[DXFTag]):
    var_name = None
    for tag in orphans:
        code, value = tag
        if code == 9:
            var_name = tag
        elif var_name is not None:
            header.append(var_name)
            header.append(tag)
            var_name = None


def _rebuild_tables(tables: List):
    """ Rebuild TABLES section:

    - remove tags "outside" of tables

    """
    pass


def _merge_tables(tables: List):
    """ Merge TABLES of same type. """
    pass


DEFAULT_ENCODING = 'cp1252'


def safe_tag_loader(stream: BinaryIO,
                    loader: Callable = None) -> Iterable[DXFTag]:
    """ Yields :class:``DXFTag`` objects from a bytes `stream`
    (untrusted external  source), skips all comment tags (group code == 999).

    - Fixes unordered and invalid vertex tags.
    - Pass :func:`synced_bytes_loader` as argument `loader` to brute force
      load invalid tag structure.

    Args:
        stream: input data stream as bytes
        loader: low level tag loader, default loader is :func:`bytes_loader`

    """
    if loader is None:
        loader = bytes_loader
    tags, detector_stream = itertools.tee(loader(stream), 2)
    encoding = detect_encoding(detector_stream)

    # Apply repair filter:
    tags = repair.filter_invalid_yz_point_codes(tags)
    tags = repair.tag_reorder_layer(tags)
    return byte_tag_compiler(tags, encoding)


def bytes_loader(stream: BinaryIO) -> Iterable[DXFTag]:
    """ Yields :class:``DXFTag`` objects from a bytes `stream`
    (untrusted external  source), skips all comment tags (group code == 999).

    ``DXFTag.code`` is always an ``int`` and ``DXFTag.value`` is always a
    raw bytes value without line endings. Works with file system streams and
    :class:`BytesIO` streams.

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


def synced_bytes_loader(stream: BinaryIO) -> Iterable[DXFTag]:
    """ Yields :class:``DXFTag`` objects from a bytes `stream`
    (untrusted external source), skips all comment tags (group code == 999).

    ``DXFTag.code`` is always an ``int`` and ``DXFTag.value`` is always a
    raw bytes value without line endings. Works with file system streams and
    :class:`BytesIO` streams.

    Does not raise DXFStructureError on invalid group codes, instead skips
    lines until a valid group code or EOF is found.

    This can remove invalid lines before group codes, but can not
    detect invalid lines between group code and tag value.

    """
    upper_boundary = MAX_GROUP_CODE + 1
    while True:
        seeking_valid_group_code = True
        try:
            while seeking_valid_group_code:
                code = stream.readline()
                if code:
                    try:
                        code = int(code)
                    except ValueError:
                        pass
                    else:
                        if 0 <= code < upper_boundary:
                            seeking_valid_group_code = False
                else:
                    return  # total empty result is EOF
            value = stream.readline()
        except EOFError:
            return

        if code != 999:
            yield DXFTag(code, value.rstrip(b'\r\n'))


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

    Expects DXF coordinates written in x, y[, z] order, see function
    :func:`safe_tag_loader` for usage with applied repair filters.

    Args:
        tags: DXF tag generator, yielding tag values as bytes like bytes_loader()
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
