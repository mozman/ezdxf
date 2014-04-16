# Purpose: graphic mixins
# Created: 2011-04-30
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from . import const
from .facebuilder import FaceBuilder


class PolymeshMixin(object):
    def set_mesh_vertex(self, pos, point, dxfattribs=None):
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['location'] = point
        vertex = self.get_mesh_vertex(pos)
        vertex.update_dxf_attribs(dxfattribs)

    def get_mesh_vertex(self, pos):
        m_count = self.dxf.m_count
        n_count = self.dxf.n_count
        m, n = pos
        if 0 <= m < m_count and 0 <= n < n_count:
            pos = m * n_count + n
            return self.__getitem__(pos)
        else:
            raise IndexError(repr(pos))


class PolyfaceMixin(object):
    """ Order of vertices and faces IS important (ACAD2010)
    1. vertices (describes the coordinates)
    2. faces (describes the face forming vertices)

    """
    def append_face(self, face, dxfattribs=None):
        self.append_faces([face], dxfattribs)

    def append_faces(self, faces, dxfattribs=None):
        def facevertex():
            vertex = self._new_entity('VERTEX', dxfattribs)
            vertex.dxf.flags = const.VTX_3D_POLYFACE_MESH_VERTEX
            return vertex

        existing_faces = list(self.faces())
        for face in faces:
            vertices = self._points_to_vertices(face, {})
            vertices.append(facevertex())
            existing_faces.append(vertices)
        self._generate(existing_faces)

    def _generate(self, faces):
        facebuilder = FaceBuilder(faces)
        self._unlink_all_vertices()  # but don't remove it from database
        self._append_vertices(facebuilder.get_vertices())


        self.update_count(facebuilder.nvertices, facebuilder.nfaces)

    def update_count(self, nvertices, nfaces):
        self.dxf.m_count = nvertices
        self.dxf.n_count = nfaces

    def faces(self):
        """ Iterate over all faces, a face is a tuple of vertices.
        result: [vertex, vertex, ..., face-vertex]
        """
        def is_face(vertex):
            flags = vertex.dxf.flags
            if flags & const.VTX_3D_POLYFACE_MESH_VERTEX > 0 and \
               flags & const.VTX_3D_POLYGON_MESH_VERTEX == 0:
                return True
            else:
                return False

        def get_face(vertex):
            face = []
            for vtx in const.VERTEXNAMES:
                index = vertex.get_dxf_attrib(vtx, 0)
                if index != 0:
                    index = abs(index) - 1
                    face.append(vertices[index])
                else:
                    break
            face.append(vertex)
            return face

        vertices = list(self.vertices())
        for vertex in vertices:
            if is_face(vertex):
                yield get_face(vertex)
