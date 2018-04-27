# Purpose: header variables factory
# Created: 20.11.2010
# Copyright (c) 2010-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

from .types import DXFVertex, DXFTag, cast_tag_value


def SingleValue(value, code=1):
    return DXFTag(code, cast_tag_value(code, value))


def Point2D(value):
    return DXFVertex(10, (value[0], value[1]))


def Point3D(value):
    return DXFVertex(10, (value[0], value[1], value[2]))
