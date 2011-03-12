#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: dxfengine factory
# Created: 11.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from .ac1009 import AC1009Engine
from .ac1015 import AC1015Engine
from .ac1018 import AC1018Engine
from .ac1021 import AC1021Engine
from .ac1024 import AC1024Engine

defaultengine = AC1009Engine()

engines = {
    'AC1009': defaultengine,
    'AC1015': AC1015Engine(),
    'AC1018': AC1018Engine(),
    'AC1021': AC1021Engine(),
    'AC1024': AC1024Engine(),
}

def dxfengine(dxfversion):
    return engines.get(dxfversion, defaultengine)
