# Purpose: DXF file testing and opening
# Created: 05.01.2018
# Copyright (C) 2018-2019, Manfred Moitzi
# License: MIT License
# Local imports to avoid cyclic import
from typing import TextIO, TYPE_CHECKING, Union, Sequence
from ezdxf.tools.standards import setup_drawing
from ezdxf.lldxf.const import DXF12, DXF2013
from ezdxf.drawing import Drawing

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFInfo


def new(dxfversion: str = DXF2013, setup: Union[str, bool, Sequence[str]] = None) -> 'Drawing':
    """
    Create a new :class:`~ezdxf.drawing.Drawing` from scratch, `dxfversion` can be either ``'AC1009'`` the official DXF
    version name or ``'R12'`` the AutoCAD release name.

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

    .. versionadded:: 0.7.4

         release name as DXF version

    Args:
        dxfversion: DXF version specifier as string, default is ``'AC1027'`` (R2013)
        setup: setup drawing standard styles

                   - ``None`` or ``False`` for no setup
                   - ``'all'`` or ``True`` to setup everything
                   - a list of topics as strings, e.g. ``['linetypes', 'styles']`` to setup only linetypes and text styles:

               ====================== ======================================================
               ``linetypes``          setup line types
               ``styles``             setup text styles
               ``dimstyles``          setup all dimension styles
               ``dimstyles:metric``   setup metric dimension styles
               ``dimstyles:imperial`` setup imperial dimension styles (not implemented yet)
               ``visualstyles``       setup 25 standard visual styles
               ====================== ======================================================

    """
    doc = Drawing.new(dxfversion)
    if setup:
        setup_drawing(doc, topics=setup)
    return doc


def read(stream: TextIO, legacy_mode: bool = False, filter_stack=None) -> 'Drawing':
    """
    Read DXF drawing from a text-stream. Open stream in text mode (``mode='rt'``) and the correct encoding has to be
    set at the open function, the stream requires at least a :meth:`readline` method. Since DXF version R2007 (AC1021)
    file encoding is always ``'utf-8'``. Use the helper function :func:`dxf_stream_info` to detect required encoding.

    If argument `legacy_mode` is ``True``, `ezdxf` tries to reorder the coordinates of the LINE entity in files from
    CAD applications which wrote the coordinates in the order: x1, x2, y1, y2. Additional fixes may be added later. The
    legacy mode has a speed penalty of around 5%.

    Args:
        stream: input text stream opened with correct encoding, requires only a :meth:`readline` method.
        legacy_mode: adds an extra trouble shooting import layer if ``True``
        filter_stack: interface to put filters between reading layers

    Raises:
        DXFStructureError: for invalid DXF structure

    """
    from ezdxf.drawing import Drawing

    return Drawing.read(stream, legacy_mode=legacy_mode, filter_stack=filter_stack)


def readfile(filename: str, encoding: str = None, legacy_mode: bool = False, filter_stack=None) -> 'Drawing':
    """
    Read DXF drawing specified by `filename` from file-system.

    This is the preferred method to open existing DXF files. Read the DXF drawing from the file-system with
    auto-detection of encoding. Decoding errors will be ignored. Override encoding detection by setting argument
    `encoding` to the estimated encoding. (use Python encoding names like in the :func:`open` function).

    If argument `legacy_mode` is ``True``, `ezdxf` tries to reorder the coordinates of the LINE entity in files from
    CAD applications which wrote the coordinates in the order: x1, x2, y1, y2. Additional fixes may be added later. The
    legacy mode has a speed penalty of around 5%.

    .. hint::

        Try argument :code:`legacy_mode=True` if error ``'Missing required y coordinate near line: ...'`` occurs.

    Args:
        filename: DXF filename
        encoding: use ``None`` for auto detect (default), or set a specific encoding like ``'utf-8'``
        legacy_mode: adds an extra trouble shooting import layer if ``True``
        filter_stack: interface to put filters between reading layers

    Raises:
        IOError: File `filename` is not a DXF file or does not exist.
        DXFStructureError: for invalid DXF structure

    """
    # for argument filter_stack see :class:`~ezdxf.drawing.Drawing.read` for more information
    from ezdxf.lldxf.validator import is_dxf_file
    from ezdxf.tools.codepage import is_supported_encoding

    if not is_dxf_file(filename):
        raise IOError("File '{}' is not a DXF file.".format(filename))

    info = dxf_file_info(filename)
    if encoding is not None:
        # override default encodings if absolute necessary
        info.encoding = encoding
    with open(filename, mode='rt', encoding=info.encoding, errors='ignore') as fp:
        doc = read(fp, legacy_mode=legacy_mode, filter_stack=filter_stack)

    doc.filename = filename
    if encoding is not None and is_supported_encoding(encoding):
        # store overridden encoding if supported by AutoCAD, else default encoding 'cp1252' is used
        # as document encoding.
        doc.encoding = encoding
    return doc


def dxf_file_info(filename: str) -> 'DXFInfo':
    """
    Reads basic file information from DXF files: DXF version, encoding and handle seed.

    Returns:
        DXF info object with attributes: version, release, handseed, encoding

    """
    with open(filename, mode='rt', encoding='utf-8', errors='ignore') as fp:
        return dxf_stream_info(fp)


def dxf_stream_info(stream: TextIO) -> 'DXFInfo':
    """
    Reads basic DXF information from a text stream: DXF version, encoding and handle seed.

    Returns:
        DXF info object with attributes: version, release, handseed, encoding

    """
    from ezdxf.lldxf.validator import dxf_info

    info = dxf_info(stream)
    if info.version >= 'AC1021':  # R2007 files and later are always encoded as UTF-8
        info.encoding = 'utf-8'
    return info


def readzip(zipfile: str, filename: str = None) -> 'Drawing':
    """
    Read DXF drawing specified by `filename` from a zip archive, or if `filename` is ``None`` the first DXF file in the
    zip archive.

    Args:
        zipfile: name of the zip archive
        filename: filename of DXF file, or ``None`` to read the first DXF file from the zip archive.

    """
    from ezdxf.tools.zipmanager import ctxZipReader

    with ctxZipReader(zipfile, filename) as zipstream:
        doc = read(zipstream)
        doc.filename = zipstream.dxf_file_name
    return doc
