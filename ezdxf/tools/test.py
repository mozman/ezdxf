# Purpose: test tools
# Created: 27.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from ezdxf.tools.handle import HandleGenerator
from ezdxf.dxffactory import dxffactory
from ezdxf.tags import StringIterator
from ezdxf.tags import Tags, TagGroups, DXFStructureError, DXFTag
from ezdxf.classifiedtags import ClassifiedTags
from ezdxf.dxfattr import DXFAttr, DXFAttributes, DefSubclass

from ezdxf.drawing import Drawing
from ezdxf.database import EntityDB


class ModelSpace:
    layout_key = None


class DrawingProxy:
    """ a lightweight drawing proxy for testing

    TestDrawingProxy in test_tools.py checks if all none private! attributes
    exists in the Drawing() class, private means starts with '__'.
    """
    def __init__(self, version):
        self.dxfversion = version
        self.entitydb = EntityDB()
        self.dxffactory = dxffactory(self)

    def modelspace(self):
        return ModelSpace()

    def _bootstraphook(self, header):
        pass

    def __does_not_exist_in_Drawing(self):
        """ ATTENTION: private attributes will not be checked in TestDrawingProxy! """


def normlines(text):
    lines = text.split('\n')
    return [line.strip() for line in lines]
