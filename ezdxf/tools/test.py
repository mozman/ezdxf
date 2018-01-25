# Purpose: test tools
# Created: 27.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from ezdxf.tools.handle import HandleGenerator
from ezdxf.dxffactory import dxffactory
from ezdxf.lldxf.tags import Tags, DXFStructureError, DXFTag
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass

from ezdxf.drawing import Drawing
from ezdxf.database import EntityDB
from ezdxf.lldxf.tagger import internal_tag_compiler


class ModelSpace:
    layout_key = 'FFFF'


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

    def bootstrap_hook(self, header):
        pass

    def __does_not_exist_in_Drawing(self):
        """ ATTENTION: private attributes will not be checked in TestDrawingProxy! """


def compile_tags_without_handles(text):
    return (tag for tag in internal_tag_compiler(text) if tag.code not in (5, 105))


def normlines(text):
    lines = text.split('\n')
    return [line.strip() for line in lines]


def load_section(text, name):
    from ezdxf.lldxf.loader import load_dxf_structure
    dxf = load_dxf_structure(internal_tag_compiler(text), ignore_missing_eof=True)
    return dxf[name]
