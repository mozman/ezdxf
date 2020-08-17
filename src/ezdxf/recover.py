#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
from typing import TYPE_CHECKING, BinaryIO, Iterable
from ezdxf.lldxf import const
from ezdxf.lldxf.types import DXFTag
from ezdxf.tools.codepage import toencoding

if TYPE_CHECKING:
    from ezdxf.eztypes import Drawing, Tags

__all__ = ['read', 'readfile']


# TODO: recover
#  Mimic the CAD "RECOVER" command, try to read messy DXF files,
#  needs only as much work until the regular ezdxf loader can handle
#  and audit the DXF file:
#
# - recover missing ENDSEC and EOF tags
# - merge multiple sections with same name
# - reorder sections
# - merge multiple tables with same name
# - apply repair layers to replace legacy_mode from read/readfile:
#       - repair.fix_coordinate_order()
#       - repair.tag_reorder_layer
#       - repair.filter_invalid_yz_point_codes
# - recover tags "outside" of sections
# - move header variable tags (9, "$...") into HEADER section


def read(stream: BinaryIO) -> 'Drawing':
    """ Read a DXF document from a binary-stream similar to :func:`ezdxf.read`,
    But this function will detect the text encoding automatically and repair
    as much flaws as possible to take the document to a state, where the
    :class:`~ezdxf.audit.Auditor` could start his journey to repair further issues.

    Args:
        stream: data stream to load in binary read mode

    """
    pass


def readfile(filename: str) -> 'Drawing':
    """ Read a DXF document from file system similar to :func:`ezdxf.readfile`,
    but this function will repair as much flaws as possible to take the document
    to a state, where the :class:`~ezdxf.audit.Auditor` could start his journey
    to repair further issues.

    Args:
        filename: file-system name of the DXF document to load

    """
    pass


DWGCODEPAGE = '$DWGCODEPAGE'
ACADVER = '$ACADVER'


class BytesLoader:
    def __init__(self, stream: BinaryIO):
        self._stream = stream
        self._encoding = 'cp1252'
        self._line = 1

    @property
    def encoding(self) -> str:
        return self._encoding

    @encoding.setter
    def encoding(self, encoding: str):
        self._encoding = encoding

    def __iter__(self):
        return self

    def __next__(self):
        try:
            code = self._stream.readline()
            value = self._stream.readline()
        except EOFError:
            raise StopIteration
        if code == b'' and value == b'':
            raise StopIteration
        try:
            code = int(code)
        except ValueError:
            raise const.DXFStructureError(
                f'Invalid group code "{code}" at line {self._line}.')
        value = value.rstrip(b'\r\n')  # remove all kind of line endings
        value = value.decode(self._encoding)
        self._line += 2
        return DXFTag(code, value)


def encoding_detector(tags: BytesLoader) -> Iterable['DXFTag']:
    next_tag = None
    encoding = None
    version = None
    done = False
    for tag in iter(tags):
        if done:
            yield tag
            continue
        code, value = tag
        if code == 9:
            if value == DWGCODEPAGE:
                next_tag = DWGCODEPAGE  # e.g. (3, "ANSI_1252")
            elif value == ACADVER:
                next_tag = ACADVER  # e.g. (1, "AC1012")
        elif code == 3 and next_tag == DWGCODEPAGE:
            encoding = toencoding(value)
            next_tag = None
        elif code == 1 and next_tag == ACADVER:
            version = value
            if version >= const.DXF2007:
                encoding = 'utf8'
            next_tag = None

        if encoding and version:
            tags.encoding = encoding
            done = True

        yield tag
