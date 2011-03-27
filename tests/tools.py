#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test tools
# Created: 27.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from ezdxf.handle import HandleGenerator
from ezdxf.dxffactory import dxffactory
from ezdxf.tags import StringIterator
from ezdxf.tags import Tags, ExtendedTags, TagGroups, DXFStructureError, DXFAttr

class DrawingProxy:
    def __init__(self, version):
        self.dxfversion = version
        self.handles = HandleGenerator()
        self.entitydb = {}
        self.dxffactory = dxffactory(self.dxfversion, self)

    def read_header_vars(self, header):
        pass

def normlines(text):
    lines = text.split('\n')
    return [line.strip() for line in lines]
