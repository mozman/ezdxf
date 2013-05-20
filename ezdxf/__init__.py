# Purpose: ezdxf package
# Created: 10.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
version = (0, 2, 0)
VERSION = "%d.%d.%d" % version
__version__ = VERSION
__author__ = "mozman <mozman@gmx.at>"

import sys
if sys.version_info[:2] < (2, 7):
    raise ImportError("Package 'ezdxf' requires Python 2.7 or later!")

import io

from .options import options  # example: ezdxf.options['templatedir'] = 'c:\templates'
from .tags import dxf_info
from .tags import TagIterator

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
    return Drawing.new(dxfversion.upper())

def read(stream):
    """Read DXF drawing from a *stream*, which only needs a readline() method.
    """
    from .drawing import Drawing
    return Drawing.read(stream)

def readfile(filename):
    """Read DXF drawing from file *filename*.
    """
    try: # is it ascii code-page encoded?
        return readfile_as_asc(filename)
    except UnicodeDecodeError: # try unicode and ignore errors
        return readfile_as_utf8(filename, errors='ignore')

#TODO: write integration test for reading 'utf-8' encoded files
def readfile_as_utf8(filename, errors='strict'):
    """Read DXF drawing from file *filename*, expects an 'utf-8' encoding.
    """
    return _read_encoded_file(filename, encoding='utf-8', errors=errors)

#TODO: write integration test for reading 'ascii-code-page' encoded files
def readfile_as_asc(filename):
    """Read DXF drawing from file *filename*, expects an ascii code-page encoding.
    """
    def get_encoding():
        with io.open(filename) as fp:
            info = dxf_info(fp)
        return info.encoding
    return _read_encoded_file(filename, encoding=get_encoding())

# noinspection PyArgumentList
def _read_encoded_file(filename, encoding='utf-8', errors='strict'):
    from .drawing import Drawing
    with io.open(filename, encoding=encoding, errors=errors) as fp:
        dwg = Drawing.read(fp)
    dwg.filename = filename
    return dwg
