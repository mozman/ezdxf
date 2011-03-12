#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: dxfvalue
# Created: 12.03.2011
# Copyright (C) , Manfred Moitzi
# License: GPLv3

from .tags import TAG_STRING_FORMAT

class DXFValue:
    def __init__(self, tag):
        self.tag = tag

    @property
    def code(self):
        return self.tag[0]

    @property
    def value(self):
        return self.tag[1]

    @property
    def ispoint(self):
        return isinstance(self.tag[0], tuple)

    def getpoint(self):
        if self.ispoint:
            return tuple( [tag[1] for tag in self.tag] )
        else:
            raise ValueError

    def __str__(self):
        if self.ispoint:
            return "".join([TAG_STRING_FORMAT % tag for tag in self.tag])
        else:
            return TAG_STRING_FORMAT % self.tag
