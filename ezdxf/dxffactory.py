# Purpose: dxf-factory-factory
# Created: 11.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <me@mozman.at>"

from .legacy import LegacyDXFFactory
from .modern import ModernDXFFactory


def dxffactory(drawing):
    dxfversion = drawing.dxfversion
    factory_class = LegacyDXFFactory if dxfversion <= 'AC1009' else ModernDXFFactory
    return factory_class(drawing)


