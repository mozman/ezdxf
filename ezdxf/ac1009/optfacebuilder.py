#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: optimizing face builder
# Created: 04.04.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

class OptimizingFaceBuilder:
    def __init__(self, faces, builder):
        self.builder = builder
        self.faces = faces
        self.nvertices = 0
        self.nfaces = 0
        self.build()

    def get_vertices(self):
        pass

    def build(self):
        pass

