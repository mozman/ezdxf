# Purpose: header variables factory
# Created: 20.11.2010
# Copyright (c) 2010-2018, Manfred Moitzi
# License: MIT License

from .types import DXFVertex, DXFTag, cast_tag_value, TagValue


def SingleValue(value: TagValue, code: int = 1) -> DXFTag:
    return DXFTag(code, cast_tag_value(code, value))


def Point2D(value: TagValue) -> DXFVertex:
    return DXFVertex(10, (value[0], value[1]))


def Point3D(value: TagValue) -> DXFVertex:
    return DXFVertex(10, (value[0], value[1], value[2]))
