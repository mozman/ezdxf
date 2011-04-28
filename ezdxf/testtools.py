#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test tools
# Created: 27.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from .handle import HandleGenerator
from .dxffactory import dxffactory
from .tags import StringIterator
from .tags import Tags, ExtendedTags, TagGroups, DXFStructureError
from .dxfattr import DXFAttr, DXFAttributes, DefSubclass

from .drawing import Drawing
from .database import SimpleDB

class DrawingProxy:
    """ a lightweight drawing proxy for testing

    TestDrawingProxy in test_tools.py checks if all none private! attributes
    exists in the Drawing() class, private means starts with '__'.
    """
    def __init__(self, version):
        self.dxfversion = version
        self.entitydb = SimpleDB()
        self.dxffactory = dxffactory(self.dxfversion, self)

    def _bootstraphook(self, header):
        pass

    def __does_not_exist_in_Drawing(self):
        """ ATTENTION: private attributes will not be checked in TestDrawingProxy! """

def normlines(text):
    lines = text.split('\n')
    return [line.strip() for line in lines]
