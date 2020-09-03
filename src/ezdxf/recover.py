#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
from typing import (
    TYPE_CHECKING, BinaryIO, Iterable, List, Callable, Tuple,
)
import itertools
from collections import defaultdict

from ezdxf.lldxf import const
from ezdxf.lldxf import repair
from ezdxf.lldxf.encoding import (
    has_dxf_backslash_encoding,
    decode_dxf_backslash_encoding,
)
from ezdxf.lldxf.types import (
    DXFTag, DXFVertex, DXFBinaryTag, POINT_CODES, BINARY_DATA, TYPE_TABLE,
    MAX_GROUP_CODE,
)
from ezdxf.lldxf.tags import group_tags, Tags
from ezdxf.lldxf.validator import entity_structure_validator
from ezdxf.tools.codepage import toencoding
from ezdxf.audit import Auditor, AuditError

if TYPE_CHECKING:
    from ezdxf.eztypes import Drawing, SectionDict

__all__ = ['read', 'readfile']

EXCLUDE_STRUCTURE_CHECK = {
    'SECTION', 'ENDSEC', 'EOF', 'TABLE', 'ENDTAB', 'ENDBLK', 'SEQEND'
}


def readfile(filename: str) -> Tuple['Drawing', 'Auditor']:
    """ Read a DXF document from file system similar to :func:`ezdxf.readfile`,
    but this function will repair as much flaws as possible, runs the required
    audit process automatically the DXF document and the :class:`Auditor`.

    Args:
        filename: file-system name of the DXF document to load

    """
    with open(filename, mode='rb') as fp:
        doc, auditor = read(fp)
    doc.filename = filename
    return doc, auditor


def read(stream: BinaryIO) -> Tuple['Drawing', 'Auditor']:
    """ Read a DXF document from a binary-stream similar to :func:`ezdxf.read`,
    but this function will detect the text encoding automatically and repair
    as much flaws as possible, runs the required audit process afterwards
    and returns the DXF document and the :class:`Auditor`.

    Args:
        stream: data stream to load in binary read mode

    """
    from ezdxf.document import Drawing
    recover_tool = Recover.run(stream)
    doc = Drawing()
    doc._load_section_dict(recover_tool.section_dict)

    auditor = Auditor(doc)
    for code, msg in recover_tool.errors:
        auditor.add_error(code, msg)
    for code, msg in recover_tool.fixes:
        auditor.fixed_error(code, msg)
    auditor.run()
    return doc, auditor


# noinspection PyMethodMayBeStatic
class Recover:
    """ Loose coupled recovering tools. """

    def __init__(self, loader: Callable = None):
        # different tag loading strategies can be used:
        #  - bytes_loader(): expects a valid low level structure
        #  - synced_bytes_loader(): loads everything which looks like a tag
        #    and skip other content (dangerous!)
        self.tag_loader = loader or bytes_loader

        # The main goal of all efforts, a Drawing compatible dict of sections:
        self.section_dict: 'SectionDict' = dict()

        # Store error messages from low level processes
        self.errors = []
        self.fixes = []

    @classmethod
    def run(cls, stream: BinaryIO, loader: Callable = None) -> 'Recover':
        """ Execute the recover process. """
        recover_tool = Recover(loader)
        tags = recover_tool.load_tags(stream)
        sections = recover_tool.rebuild_sections(tags)
        recover_tool.load_section_dict(sections)
        tables = recover_tool.section_dict.get('TABLES')
        if tables:
            tables = recover_tool.rebuild_tables(tables)
            recover_tool.section_dict['TABLES'] = tables

        section_dict = recover_tool.section_dict
        for name, entities in section_dict.items():
            if name in {'TABLES', 'BLOCKS', 'OBJECTS', 'ENTITIES'}:
                section_dict[name] = list(recover_tool.check_entities(entities))

        return recover_tool

    def load_tags(self, stream: BinaryIO) -> Iterable[DXFTag]:
        return safe_tag_loader(stream, self.tag_loader, self.errors)

    def rebuild_sections(self, tags: Iterable[DXFTag]) -> List[List[DXFTag]]:
        """ Collect tags between SECTION and ENDSEC or next SECTION tags as
        sections as list of DXFTag objects, collects tags outside of sections
        as an extra section.

        Returns:
            List of sections as list of DXFTag() objects, the last section
            contains orphaned tags found outside of sections

        """

        def close_section():
            # ENDSEC tag is not collected
            nonlocal collector, inside_section
            if inside_section:
                sections.append(collector)
            else:  # missing SECTION
                # ignore this tag, it is even not an orphan
                self.fixes.append((
                    AuditError.MISSING_SECTION_TAG,
                    'DXF structure error: missing SECTION tag.'
                ))
            collector = []
            inside_section = False

        def open_section():
            nonlocal inside_section
            if inside_section:  # missing ENDSEC
                self.fixes.append((
                    AuditError.MISSING_ENDSEC_TAG,
                    'DXF structure error: missing ENDSEC tag.'
                ))
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
                    self.fixes.append((
                        AuditError.MISSING_ENDSEC_TAG,
                        'DXF structure error: missing ENDSEC tag.'
                    ))
                    close_section()
            else:
                collect()

        def collect():
            if inside_section:
                collector.append(tag)
            else:
                self.fixes.append((
                    AuditError.FOUND_TAG_OUTSIDE_SECTION,
                    f'DXF structure error: found tag outside section: '
                    f'({code}, {value})'
                ))
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

    def load_section_dict(self, sections: List[List[DXFTag]]) -> None:
        """ Merge sections of same type. """

        def add_section(name: str, tags) -> None:
            if name in section_dict:
                section_dict[name].extend(tags[2:])
            else:
                section_dict[name] = tags

        def _build_section_dict(d: dict) -> None:
            for name, section in d.items():
                if name in const.MANAGED_SECTIONS:
                    self.section_dict[name] = list(group_tags(section, 0))

        # Last section could be orphaned tags:
        orphans = sections.pop()
        if orphans and orphans[0] == (0, 'SECTION'):
            # The last section contains not the orphaned tags:
            sections.append(orphans)
            orphans = []

        section_dict = dict()
        for section in sections:
            code, name = section[1]
            if code == 2:
                add_section(name, section)
            else:  # invalid section name tag e.g. (2, "HEADER")
                self.fixes.append((
                    AuditError.MISSING_SECTION_NAME_TAG,
                    'DXF structure error: missing section name tag, ignore section.'
                ))

        header = section_dict.setdefault('HEADER', [
            DXFTag(0, 'SECTION'),
            DXFTag(2, 'HEADER'),
        ])
        self.rescue_orphaned_header_vars(header, orphans)
        _build_section_dict(section_dict)

    def rebuild_tables(self, tables: List[Tags]) -> List[Tags]:
        """ Rebuild TABLES section. """

        def append_table(name: str):
            if name not in content:
                return

            head = heads.get(name)
            if head:
                tables.append(head)
            else:
                # The new table head gets a valid handle from Auditor.
                tables.append(Tags([DXFTag(0, 'TABLE'), DXFTag(2, name)]))
            tables.extend(content[name])
            tables.append(Tags([DXFTag(0, 'ENDTAB')]))

        heads = dict()
        content = defaultdict(list)
        valid_tables = set(const.TABLE_NAMES_ACAD_ORDER)

        for entry in tables:
            name = entry[0].value.upper()
            if name == 'TABLE':
                try:
                    table_name = entry[1].value.upper()
                except (IndexError, AttributeError):
                    pass
                else:
                    heads[table_name] = entry
            elif name in valid_tables:
                content[name].append(entry)
        tables = [Tags([DXFTag(0, 'SECTION'), DXFTag(2, 'TABLES')])]
        for name in const.TABLE_NAMES_ACAD_ORDER:
            append_table(name)
        return tables

    def rescue_orphaned_header_vars(
            self,
            header: List[DXFTag],
            orphans: Iterable[DXFTag]) -> None:
        var_name = None
        for tag in orphans:
            code, value = tag
            if code == 9:
                var_name = tag
            elif var_name is not None:
                header.append(var_name)
                header.append(tag)
                var_name = None

    def check_entities(self, entities: List[Tags]) -> Iterable[Tags]:
        for entity in entities:
            _, dxftype = entity[0]
            if dxftype in EXCLUDE_STRUCTURE_CHECK:
                yield entity
            else:
                # raises DXFStructureError() for invalid entities
                yield Tags(entity_structure_validator(entity))


def safe_tag_loader(stream: BinaryIO,
                    loader: Callable = None,
                    errors: List = None) -> Iterable[DXFTag]:
    """ Yields :class:``DXFTag`` objects from a bytes `stream`
    (untrusted external  source), skips all comment tags (group code == 999).

    - Fixes unordered and invalid vertex tags.
    - Pass :func:`synced_bytes_loader` as argument `loader` to brute force
      load invalid tag structure.

    Args:
        stream: input data stream as bytes
        loader: low level tag loader, default loader is :func:`bytes_loader`
        errors: list to store error messages

    """
    if loader is None:
        loader = bytes_loader
    tags, detector_stream = itertools.tee(loader(stream), 2)
    encoding = detect_encoding(detector_stream)

    # Apply repair filter:
    tags = repair.tag_reorder_layer(tags)
    tags = repair.filter_invalid_yz_point_codes(tags)
    return byte_tag_compiler(tags, encoding, errors)


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
                code = code.decode(const.DEFAULT_ENCODING)
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
    code = 999
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
            encoding = toencoding(value.decode(const.DEFAULT_ENCODING))
            next_tag = None
        elif code == 1 and next_tag == ACADVER:
            dxfversion = value.decode(const.DEFAULT_ENCODING)
            next_tag = None

        if encoding and dxfversion:
            return 'utf8' if dxfversion >= const.DXF2007 else encoding

    return const.DEFAULT_ENCODING


def byte_tag_compiler(tags: Iterable[DXFTag],
                      encoding=const.DEFAULT_ENCODING,
                      errors: List = None) -> Iterable[DXFTag]:
    """ Compiles DXF tag values imported by bytes_loader() into Python types.

    Raises DXFStructureError() for invalid float values and invalid coordinate
    values.

    Expects DXF coordinates written in x, y[, z] order, see function
    :func:`safe_tag_loader` for usage with applied repair filters.

    Args:
        tags: DXF tag generator, yielding tag values as bytes like bytes_loader()
        encoding: text encoding
        errors: list to store error messages

    Raises:
        DXFStructureError: Found invalid DXF tag or unexpected coordinate order.

    """

    def error_msg(tag):
        code = tag.code
        value = tag.value.decode(encoding)
        return f'Invalid tag ({code}, "{value}") near line: {line}.'

    if errors is None:
        errors = []
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
                        value = x.value.strip().upper()
                    try:
                        str_ = value.decode(encoding)
                    except UnicodeDecodeError:
                        errors.append((
                            AuditError.DECODING_ERROR,
                            f'Ignore decoding error in line {line}.'
                        ))
                        str_ = value.decode(encoding, errors='ignore')

                    # Convert DXF unicode notation "\U+xxxx" to unicode,
                    # but exclude structure tags (code>0):
                    if code and has_dxf_backslash_encoding(str_):
                        str_ = decode_dxf_backslash_encoding(str_)

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
                                raise const.DXFStructureError(error_msg(x))
                        else:
                            raise const.DXFStructureError(error_msg(x))
        except StopIteration:
            return
