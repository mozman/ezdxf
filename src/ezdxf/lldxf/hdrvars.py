# Purpose: header variables factory
# Created: 20.11.2010
# Copyright (c) 2010-2018, Manfred Moitzi
# License: MIT License
from typing import Sequence, Union
from .types import DXFVertex, DXFTag, cast_tag_value


def SingleValue(value: Union[str, float], code: int = 1) -> DXFTag:
    return DXFTag(code, cast_tag_value(code, value))


def Point2D(value: Sequence[float]) -> DXFVertex:

    return DXFVertex(10, (value[0], value[1]))


def Point3D(value: Sequence[float]) -> DXFVertex:
    return DXFVertex(10, (value[0], value[1], value[2]))


class HeaderVarDef:
    def __init__(self, name, code, factory, mindxf, maxdxf, priority, default=None):
        self.name = name
        self.code = code
        self.factory = factory
        self.mindxf = mindxf
        self.maxdxf = maxdxf
        self.priority = priority
        self.default = default
