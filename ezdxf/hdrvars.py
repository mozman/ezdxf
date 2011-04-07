#!/usr/bin/env python
#coding:utf-8
# Author:  mozman
# Purpose: header variables factory
# Created: 20.11.2010
# Copyright (C) 2010, Manfred Moitzi
# License: GPLv3

from .tags import DXFTag, tagcast

def SingleValue(value, code=1):
    return tagcast( (code, value) )

def Point2D(value):
    return (DXFTag(10, value[0]), DXFTag(20, value[1]))

def Point3D(value):
    return (DXFTag(10, value[0]), DXFTag(20, value[1]), DXFTag(30, value[2]))
