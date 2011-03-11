#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: dxfengine factory
# Created: 11.03.2011
# Copyright (C) , Manfred Moitzi
# License: GPLv3

from .ac1009 import R12Engine

engines = {
    'AC1009': R12Engine,
}

def dxfengine(dxfversion):
    return engines.get(dxfversion, defaultengine(dxfversion))

def defaultengine(dxfversion):
    return R12Engine