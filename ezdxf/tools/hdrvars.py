# Purpose: header variables factory
# Created: 20.11.2010
# Copyright (C) 2010, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from ..tags import DXFTag, cast_tag


def SingleValue(value, code=1):
    return cast_tag((code, value))


def Point2D(value):
    return DXFTag(10, (value[0], value[1]))


def Point3D(value):
    return DXFTag(10, (value[0], value[1], value[2]))
