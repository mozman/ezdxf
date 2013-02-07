#!/usr/bin/env python
#coding:utf-8
# Purpose: ezdxf package
# Created: 10.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
version = (0, 2, 0)
VERSION = "%d.%d.%d"  % version
__version__ = VERSION
__author__ = "mozman <mozman@gmx.at>"

# Python2/3 support should be done here
import sys
if sys.version_info[0] > 2:
    # for Python 3
    tostr = str
else:
    # for Python 2
    tostr = unicode
# end of Python2/3 support

import io
from contextlib import contextmanager

from .options import options
# example: ezdxf.options['templatedir'] = 'c:\templates'
from .tags import dxfinfo

@contextmanager # TODO: test it!!!
def open_encoded_text_file(filename, mode='r', encoding='cp1252'):
    buffer = io.FileIO(filename, mode)
    fp = io.TextIOWrapper(buffer, encoding=encoding)
    try:
        yield fp
    finally:
        fp.close()
        buffer.close()

def read(stream):
    from .drawing import Drawing
    return Drawing.read(stream)


def readfile(filename):
    def get_encoding():
        with open(filename) as fp:
            info = dxfinfo(fp)
        return info.encoding

    from .drawing import Drawing
    with open_encoded_text_file(filename, encoding=get_encoding()) as fp:
        dwg = Drawing.read(fp)
    dwg.filename = filename
    return dwg

def new(dxfversion='AC1009'):
    from .drawing import Drawing
    return Drawing.new(dxfversion)