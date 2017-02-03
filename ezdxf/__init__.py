# Purpose: ezdxf package
# Created: 10.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

version = (0, 7, 10)  # also update VERSION in setup.py
VERSION = "%d.%d.%d" % version
__version__ = VERSION
__author__ = "mozman <mozman@gmx.at>"

import sys
if sys.version_info[:2] < (2, 7):
    raise ImportError("Package 'ezdxf' requires Python 2.7 or later!")

import io

import codecs
from .lldxf.encoding import dxfbackslashreplace
codecs.register_error('dxfreplace', dxfbackslashreplace)  # setup DXF unicode encoder -> '\U+nnnn'

from .options import options  # example: ezdxf.options.template_dir = 'c:\templates'
from .lldxf.tags import dxf_info
from .lldxf.tagger import stream_tagger, skip_comments
from .tools.importer import Importer
from .tools.codepage import is_supported_encoding
from .lldxf.const import DXFStructureError, DXFVersionError
from .tools.zipmanager import ctxZipReader
from .tools import transparency2float, float2transparency  #  convert transparency integer values to floats 0..1
from .tools.rgb import int2rgb, rgb2int
from .tools.pattern import PATTERN
from .lldxf import const  #  restore module structure ezdxf.const


def new(dxfversion='AC1009'):
    """Create a new DXF drawing.

    :param dxfversion: DXF version specifier, default is 'AC1009'

    new() can create drawings for following DXF versions:
    - 'AC1009': AutoCAD R12 (DXF12)
    - 'AC1015': AutoCAD 2000
    - 'AC1018': AutoCAD 2004
    - 'AC1021': AutoCAD 2007
    - 'AC1024': AutoCAD 2010
    - 'AC1027': AutoCAD 2013

    """
    from .drawing import Drawing
    return Drawing.new(dxfversion)


def read(stream):
    """Read DXF drawing from a text *stream*, which only needs a readline() method.

    read() can open drawings of following DXF versions:
    - pre 'AC1009' DXF versions will be upgraded to 'AC1009', requires encoding set by header var $DWGCODEPAGE
    - 'AC1009': AutoCAD R12 (DXF12), requires encoding set by header var $DWGCODEPAGE
    - 'AC1012': AutoCAD R12 upgraded to AC1015, requires encoding set by header var $DWGCODEPAGE
    - 'AC1014': AutoCAD R14 upgraded to AC1015, requires encoding set by header var $DWGCODEPAGE
    - 'AC1015': AutoCAD 2000, requires encoding set by header var $DWGCODEPAGE
    - 'AC1018': AutoCAD 2004, requires encoding set by header var $DWGCODEPAGE
    - 'AC1021': AutoCAD 2007, requires encoding='utf-8'
    - 'AC1024': AutoCAD 2010, requires encoding='utf-8'
    - 'AC1027': AutoCAD 2013, requires encoding='utf-8'

    """
    from .drawing import Drawing
    return Drawing.read(stream)


def readfile(filename, encoding='auto'):
    """Read DXF drawing from file *filename*.
    """
    if not is_dxf_file(filename):
        raise IOError("File '{}' is not a DXF file.".format(filename))

    with io.open(filename, mode='rt', encoding='utf-8', errors='ignore') as fp:
        info = dxf_info(fp)

    if encoding != 'auto':  # override encoding detection and $DWGCODEPAGE
        enc = encoding
    elif info.version >= 'AC1021':  # R2007 files and later are always encoded as UTF-8
        enc = 'utf-8'
    else:
        enc = info.encoding

    with io.open(filename, mode='rt', encoding=enc, errors='ignore') as fp:
        dwg = read(fp)

    dwg.filename = filename
    if encoding != 'auto' and is_supported_encoding(encoding):
        dwg.encoding = encoding
    return dwg


def readzip(zipfile, filename=None):
    """ Reads the DXF file *filename* from *zipfile* or the first DXF file in *zipfile* if *filename* is *None*.
    """
    with ctxZipReader(zipfile, filename) as zipstream:
        dwg = read(zipstream)
        dwg.filename = zipstream.dxf_file_name
    return dwg


def is_dxf_file(filename):
    with io.open(filename, errors='ignore') as fp:
        reader = skip_comments(stream_tagger(fp))
        return next(reader) == (0, 'SECTION')
