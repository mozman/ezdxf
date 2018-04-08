# Created: 04.04.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from ..lldxf.const import VERTEXNAMES


class PolyfaceBuilder(object):
    def __init__(self, faces, precision=6):
        self.precision = precision
        self.faces = []
        self.vertices = []
        self.index_mapping = {}
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
            face_record = face.face_record
            for vertex, name in zip(face, VERTEXNAMES):
                index = self.add(vertex)
                # preserve sign of old index value
                sign = -1 if face_record.get_dxf_attrib(name, 0) < 0 else +1
                face_record.set_dxf_attrib(name, (index + 1) * sign)
            self.faces.append(face_record)

    def add(self, vertex):
        def key(point):
            return tuple((round(coord, self.precision) for coord in point))

        location = key(vertex.dxf.location)
        try:
            return self.index_mapping[location]
        except KeyError:  # internal exception
            index = len(self.vertices)
            self.index_mapping[location] = index
            self.vertices.append(vertex)
            return index
