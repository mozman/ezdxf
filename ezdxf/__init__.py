#!/usr/bin/env python
#coding:utf-8
# Purpose: ezdxf package
# Created: 10.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
version = (0, 2, 0)
VERSION = "%d.%d.%d" % version
__version__ = VERSION
__author__ = "mozman <mozman@gmx.at>"

import io
from contextlib import contextmanager

from .options import options  # example: ezdxf.options['templatedir'] = 'c:\templates'
from .tags import dxf_info

def read(stream):
    from .drawing import Drawing
    return Drawing.read(stream)

def readfile(filename, options=None):
    try: # is it ascii code-page encoded?
        return readfile_as_asc(filename, options)
    except UnicodeDecodeError: # try unicode and ignore errors
        return readfile_as_utf8(filename, options, errors='ignore')

#TODO: write integration test for reading 'utf-8' encoded files
def readfile_as_utf8(filename, options=None, errors='strict'):
    return _read_encoded_file(filename, options, encoding='utf-8', errors=errors)

#TODO: write integration test for reading 'ascii-code-page' encoded files
def readfile_as_asc(filename, options=None):
    def get_encoding():
        with open(filename) as fp:
            info = dxf_info(fp)
        return info.encoding

    return _read_encoded_file(filename, options, encoding=get_encoding())

def _read_encoded_file(filename, options=None, encoding='utf-8', errors='strict'):
    from .drawing import Drawing
    with io.open(filename, encoding=encoding, errors=errors) as fp:
        dwg = Drawing(fp, options)
    dwg.filename = filename
    return dwg

def new(dxfversion='AC1009'):
    from .drawing import Drawing
    return Drawing.new(dxfversion.upper())