#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: ezdxf package
# Created: 10.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

version = (0, 1, 0)
VERSION = "%d.%d.%d"  % version

from .options import options
# example: ezdxf.options['templatedir'] = 'c:\templates'
from .tags import dxfinfo

def read(stream):
    from .drawing import Drawing
    return Drawing.read(stream)

def readfile(filename):
    from .drawing import Drawing
    enc = _get_encoding(filename)
    with open(filename, encoding=enc) as fp:
        return Drawing.read(fp)

def _get_encoding(filename):
    with open(filename) as fp:
        info = dxfinfo(fp)
    return info.encoding
