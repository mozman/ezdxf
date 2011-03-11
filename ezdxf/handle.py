#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: handle module
# Created: 11.03.2011
# Copyright (C) , Manfred Moitzi
# License: GPLv3

class HandleGenerator:
    def __init__(self, startvalue=0):
        self._handle = startvalue

    @property
    def current_max_handle(self):
        return self._handle

    @property
    def next_handle(self):
        nexthandle = self._handle
        self._handle += 1
        return nexthandle

    def reset(self, startvalue):
        self._handle = startvalue
