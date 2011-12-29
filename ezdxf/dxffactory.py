#!/usr/bin/env python
#coding:utf-8
# Purpose: dxf-factory-factory
# Created: 11.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .ac1009 import AC1009Factory
from .ac1015 import AC1015Factory
from .ac1018 import AC1018Factory
from .ac1021 import AC1021Factory
from .ac1024 import AC1024Factory

default_factory = AC1009Factory

factories = {
    'AC1009': default_factory,
    'AC1015': AC1015Factory,
    'AC1018': AC1018Factory,
    'AC1021': AC1021Factory,
    'AC1024': AC1024Factory,
}

def dxffactory(dxfversion, drawing=None):
    factory_class = factories.get(dxfversion, default_factory)
    factory = factory_class()
    factory.drawing = drawing
    return factory


