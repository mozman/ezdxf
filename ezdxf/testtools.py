# Purpose: test tools
# Created: 27.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .handle import HandleGenerator
from .dxffactory import dxffactory
from .tags import StringIterator
from .tags import Tags, TagGroups, DXFStructureError, DXFTag
from .classifiedtags import ClassifiedTags
from .dxfattr import DXFAttr, DXFAttributes, DefSubclass

from .drawing import Drawing
from .database import EntityDB


class DrawingProxy:
    """ a lightweight drawing proxy for testing

    TestDrawingProxy in test_tools.py checks if all none private! attributes
    exists in the Drawing() class, private means starts with '__'.
    """
    def __init__(self, version):
        self.dxfversion = version
        self.entitydb = EntityDB()
        self.dxffactory = dxffactory(self)

    def _bootstraphook(self, header):
        pass

    def __does_not_exist_in_Drawing(self):
        """ ATTENTION: private attributes will not be checked in TestDrawingProxy! """


def normlines(text):
    lines = text.split('\n')
    return [line.strip() for line in lines]
