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

from ezdxf.drawing import Drawing
from ezdxf.database import SimpleDB

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
