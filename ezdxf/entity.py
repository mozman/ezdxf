#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: entity module
# Created: 11.03.2011
# Copyright (C) , Manfred Moitzi
# License: GPLv3

class Entity:
    def __init__(self, handle, drawing):
        self._handle = handle
        self._drawing = drawing
        self._data = None

    @property
    def handle(self):
        return self._handle

    def _aquire_data(self):
        self._data = self._drawing.entitydb.aquire(self._handle)

    def _commit(self):
        self._drawing.entitydb.commit(self._handle, self._data)
        self._data = None

