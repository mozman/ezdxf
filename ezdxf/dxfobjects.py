#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: dxf objects wrapper, dxf-objects arn non-graphical entities
# all dxf objects resides in the OBJECTS SECTION
# Created: 22.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

class DXFDictinary:
    def __init__(self, tags):
        self.tags = tags