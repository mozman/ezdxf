#!/usr/bin/env python
#coding:utf-8
# Purpose: ezdxf package
# Created: 10.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

version = (0, 1, 0)
VERSION = "%d.%d.%d"  % version
__version__ = VERSION

from .options import options
# example: ezdxf.options['templatedir'] = 'c:\templates'
from .tags import dxfinfo

def read(stream):
    from .drawing import Drawing
    return Drawing.read(stream)

def readfile(filename):
    def get_encoding():
        with open(filename) as fp:
            info = dxfinfo(fp)
        return info.encoding

    from .drawing import Drawing
    with open(filename, encoding=get_encoding()) as fp:
        dwg = Drawing.read(fp)
    dwg.filename = filename
    return dwg

def new(dxfversion='AC1009'):
    from .drawing import Drawing
    return Drawing.new(dxfversion)