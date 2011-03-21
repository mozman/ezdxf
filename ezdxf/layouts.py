#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: layout manager
# Created: 21.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

# The ModelSpace is a special Layout called 'Model'

class Layouts:
    def __init__(self, drawing):
        self._layouts = {}
        self._drawing = drawing

    def __contains__(self, name):
        return name in self._layouts

    def create(self, name):
        pass

    def get(self, name):
        return self._layouts[name]

    def rename(self, oldname, newname):
        if self.__contains__(newname):
            raise ValueError('Layout with name %s already exists' % newname)
        layout = self.get(oldname)
        del self._layouts[oldname]
        self._layouts[newname] = layout
        layout.name = newname

    def remove(self, name):
        layout = self.get(name)
        del self._layouts[name]
        layout.destroy()

class Layout:
    def __init__(self, name, entityspace):
        self.name = name
        self._workspace = entityspace

    def destroy(self):
        pass
