#!/usr/bin/env python
#coding:utf-8
# Purpose: handle module
# Created: 11.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

class HandleGenerator:
    def __init__(self, startvalue='1'):
        self._handle = int(startvalue, 16)

    @property
    def seed(self):
        return _hexstr(self._handle)

    def next(self):
        next_handle =  self.seed
        self._handle += 1
        return next_handle

    def reset(self, startvalue):
        self._handle = int(startvalue, 16)

def _hexstr(number):
    return "%X" % number
