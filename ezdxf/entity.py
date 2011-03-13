#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: entity module
# Created: 11.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

class Entity:
    """
    Proxy for entities stored in the entitydb of the drawing.

    '_handle' is the database-key
    '_tags' are the temporary stored entity data
    """
    def __init__(self, handle, drawing):
        self._handle = handle
        self._drawing = drawing
        self._tags = None

    @property
    def handle(self):
        return self._handle

    @property
    def tags(self):
        if self._tags is None:
            self._getdata()
        return self._tags

    @property
    def entitydb(self):
        return self._drawing.entitydb

    def _getdata(self):
        self._tags = self.entitydb[self._handle]

    def _putdata(self):
        if self._tags is not None:
            self.entitydb[self._handle] = self._tags
            self._tags = None

