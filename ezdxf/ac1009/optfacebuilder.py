#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: optimizing face builder
# Created: 04.04.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from ..const import VERTEXNAMES

class OptimizingFaceBuilder:
    precision = 6

    def __init__(self, faces):
        self.faces = []
        self.vertices = []
        self.indexmap = {}
        self.build(faces)

    @property
    def nvertices(self):
        return len(self.vertices)

    @property
    def nfaces(self):
        return len(self.faces)

    def get_vertices(self):
        vertices = self.vertices[:]
        vertices.extend(self.faces)
        return vertices

    def build(self, faces):
        for face in faces:
            facevertex = face.pop()
            for vertex, name in zip(face, VERTEXNAMES):
                index = self.add(vertex)
                facevertex.setdxfattr(name, index+1)
            self.faces.append(facevertex)

    def add(self, vertex):
        def key(point):
            return tuple( (round(coord, self.precision) for coord in point) )

        key = key(vertex.location)
        try:
            return self.indexmap[key]
        except KeyError:
            index = len(self.vertices)
            self.indexmap[key] = index
            self.vertices.append(vertex)
            return index
