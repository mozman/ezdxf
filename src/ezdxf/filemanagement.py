# Created: 05.01.2018
# Copyright (C) 2018-2020, Manfred Moitzi
# License: MIT License
# Local imports to avoid cyclic import errors
from typing import TextIO, TYPE_CHECKING, Union, Sequence
import base64
import io
import warnings
from ezdxf.tools.standards import setup_drawing
from ezdxf.lldxf.const import DXF2013
from ezdxf.document import Drawing

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFInfo


def new(dxfversion: str = DXF2013,
        setup: Union[str, bool, Sequence[str]] = False) -> 'Drawing':
    """ Create a new :class:`~ezdxf.drawing.Drawing` from scratch, `dxfversion`
    can be either "AC1009" the official DXF version name or "R12" the
    AutoCAD release name.

    :func:`new` can create drawings for following DXF versions:

    ======= ========================
    Version AutoCAD Release
    ======= ========================
    AC1009  AutoCAD R12
    AC1015  AutoCAD R2000
    AC1018  AutoCAD R2004
    AC1021  AutoCAD R2007
    AC1024  AutoCAD R2010
    AC1027  AutoCAD R2013
    AC1032  AutoCAD R2018
    ======= ========================

    Args:
        dxfversion: DXF version specifier as string, default is "AC1027"
            respectively "R2013"
        setup: setup default styles, ``False`` for no setup,
            ``True`` to setup everything or a list of topics as strings,
            e.g. ["linetypes", "styles"] to setup only some topics:

            ================== ========================================
            Topic              Description
            ================== ========================================
            linetypes          setup line types
            styles             setup text styles
            dimstyles          setup default `ezdxf` dimension styles
            visualstyles       setup 25 standard visual styles
            ================== ========================================

    """
    doc = Drawing.new(dxfversion)
    if setup:
        setup_drawing(doc, topics=setup)
    return doc


def read(stream: TextIO, legacy_mode: bool = False) -> 'Drawing':
    """ Read a DXF document from a text-stream. Open stream in text mode
    (``mode='rt'``) and set correct text encoding, the stream requires at least
    a :meth:`readline` method.

    Since DXF version R2007 (AC1021) file encoding is always "utf-8",
    use the helper function :func:`dxf_stream_info` to detect the required
    text encoding for prior DXF versions.

    If this function struggles to load the DXF document and raises a
    :class:`DXFStructureError` exception, try the :func:`ezdxf.recover.read`
    function to load this corrupt DXF document.

    Args:
        stream: input text stream opened with correct encoding
        legacy_mode: adds an extra trouble shooting import layer if ``True``
            (deprecated)

    Raises:
        DXFStructureError: for invalid DXF structure

    .. deprecated:: v0.14

        argument `legacy_mode`, use module :mod:`ezdxf.recover`
        to load DXF documents with structural flaws.

    """
    from ezdxf.document import Drawing
    if legacy_mode:
        warnings.warn(
            '"legacy_mode" is deprecated (removed in v0.16), replace call by '
            'ezdxf.recover.readfile().',
            DeprecationWarning
        )
    return Drawing.read(stream, legacy_mode=legacy_mode)


def readfile(filename: str, encoding: str = None,
             legacy_mode: bool = False) -> 'Drawing':
    """  Read the DXF document `filename` from the file-system.

    This is the preferred method to load existing ASCII or Binary DXF files,
    the required text encoding will be detected automatically and decoding
    errors will be ignored.

    Override encoding detection by setting argument `encoding` to the
    estimated encoding. (use Python encoding names like in the :func:`open`
    function).

    If this function struggles to load the DXF document and raises a
    :class:`DXFStructureError` exception, try the :func:`ezdxf.recover.readfile`
    function to load this corrupt DXF document.

    Args:
        filename: filename of the ASCII- or Binary DXF document
        encoding: use ``None`` for auto detect (default), or set a specific
            encoding like "utf-8", argument is ignored for Binary DXF files
        legacy_mode: adds an extra trouble shooting import layer if ``True``
            (deprecated)

    Raises:
        IOError: File `filename` is not a DXF file or does not exist.
        DXFStructureError: for invalid DXF structure

    .. deprecated:: v0.14

        argument `legacy_mode`, use module :mod:`ezdxf.recover`
        to load DXF documents with structural flaws.

    """
    from ezdxf.lldxf.validator import is_dxf_file, is_binary_dxf_file
    from ezdxf.tools.codepage import is_supported_encoding
    from ezdxf.lldxf.tagger import binary_tags_loader
    if legacy_mode:
        warnings.warn(
            '"legacy_mode" is deprecated (removed in v0.16), replace call by '
            'ezdxf.recover.read().', DeprecationWarning
        )

    filename = str(filename)
    if is_binary_dxf_file(filename):
        with open(filename, 'rb') as fp:
            data = fp.read()
            loader = binary_tags_loader(data)
            return Drawing.load(loader, legacy_mode)

    if not is_dxf_file(filename):
        raise IOError("File '{}' is not a DXF file.".format(filename))

    info = dxf_file_info(filename)
    if encoding is not None:
        # override default encodings if absolute necessary
        info.encoding = encoding
    with open(filename, mode='rt', encoding=info.encoding,
              errors='ignore') as fp:
        doc = read(fp, legacy_mode=legacy_mode)

    doc.filename = filename
    if encoding is not None and is_supported_encoding(encoding):
        # store overridden encoding if supported by AutoCAD, else default
        # encoding stored in $DWGENCODING is used as document encoding or
        # 'cp1252' if $DWGENCODING is unset.
        doc.encoding = encoding
    return doc


def dxf_file_info(filename: str) -> 'DXFInfo':
    """ Reads basic file information from a DXF document: DXF version, encoding
    and handle seed.

    """
    with open(filename, mode='rt', encoding='utf-8', errors='ignore') as fp:
        return dxf_stream_info(fp)


def dxf_stream_info(stream: TextIO) -> 'DXFInfo':
    """ Reads basic DXF information from a text stream: DXF version, encoding
    and handle seed.

    """
    from ezdxf.lldxf.validator import dxf_info

    info = dxf_info(stream)
    # R2007 files and later are always encoded as UTF-8
    if info.version >= 'AC1021':
        info.encoding = 'utf-8'
    return info


def readzip(zipfile: str, filename: str = None) -> 'Drawing':
    """ Load a DXF document specified by `filename` from a zip archive, or if
    `filename` is ``None`` the first DXF document in the zip archive.

    Args:
        zipfile: name of the zip archive
        filename: filename of DXF file, or ``None`` to load the first DXF
            document from the zip archive.

    """
    from ezdxf.tools.zipmanager import ctxZipReader

    with ctxZipReader(zipfile, filename) as zipstream:
        doc = read(zipstream)
        doc.filename = zipstream.dxf_file_name
    return doc


def decode_base64(data: bytes) -> 'Drawing':
    """ Load a DXF document from base64 encoded binary data, like uploaded data
    to web applications.

    Args:
        data: DXF document base64 encoded binary data

    """
    # Copyright (c) 2020, Joseph Flack
    # License: MIT License
    # Decode base64 encoded data into binary data
    binary_data = base64.b64decode(data)

    # Replace windows line ending '\r\n' by universal line ending '\n'
    binary_data = binary_data.replace(b'\r\n', b'\n')

    # Read DXF file info from data, basic DXF information in the HEADER
    # section is ASCII encoded so encoding setting here is not important
    # for this task:
    text = binary_data.decode('utf-8', errors='ignore')
    stream = io.StringIO(text)
    info = dxf_stream_info(stream)
    stream.close()

    # Use encoding info to create correct decoded text input stream for ezdxf
    text = binary_data.decode(info.encoding, errors='ignore')
    stream = io.StringIO(text)

    # Load DXF document from data stream
    doc = read(stream)
    stream.close()
    return doc
