#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: database module
# Created: 11.03.2011
# Copyright (C) , Manfred Moitzi
# License: GPLv3

class EntityDB:
    """ A simple key/value database a.k.a. dict(), but can be replaced.
    """
    def __init__(self):
        self._database = {}

    def __delitem__(self, key):
        del self._database[key]

    def __getitem__(self, handle):
        return self.aquire(handle)

    def __setitem__(self, handle, entity):
        self.commit(handle, entity)

    def aquire(self, handle):
        assert isinstance(handle, int)
        return self._database[handle]

    def commit(self, handle, entity):
        assert isinstance(handle, int)
        self._database[handle] = entity

    def remove(self, key):
        del self._database[key]
