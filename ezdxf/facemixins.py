#!/usr/bin/env python
#coding:utf-8
# Purpose: graphic mixins
# Created: 2011-04-30
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
        mcount = self.dxf.mcount
        ncount = self.dxf.ncount
        m, n = pos
        if 0 <= m < mcount and 0 <= n < ncount:
            pos = m * ncount + n
            return self._get_vertex_at_trusted_position(pos)
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
            vertex = self._builder._build_entity('VERTEX', dxfattribs)
            vertex.dxf.flags = const.VTX_3D_POLYFACE_MESH_VERTEX
            return vertex

        existing_faces = list(self.faces())
        for face in faces:
            vertices = self._points_to_vertices(face, {})
            vertices.append(facevertex())
            existing_faces.append(vertices)
        self._generate(existing_faces)

    def _generate(self, faces):
        def remove_all_vertices():
            startindex, endindex = self._get_index_range()
            if startindex <= endindex:
                self._builder._remove_entities(startindex, (endindex - startindex) + 1)

        def insert_new_vertices(vertices):
            index = self._builder._get_index(self) + 1
            self._builder._insert_entities(index, vertices)

        facebuilder = FaceBuilder(faces)
        remove_all_vertices()
        insert_new_vertices(facebuilder.get_vertices())
        self.update_count(facebuilder.nvertices, facebuilder.nfaces)

    def update_count(self, nvertices, nfaces):
        self.dxf.mcount = nvertices
        self.dxf.ncount = nfaces

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

        vertices = list(iter(self))
        for vertex in vertices:
            if is_face(vertex):
                yield get_face(vertex)
