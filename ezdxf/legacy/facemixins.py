# Purpose: graphic mixins
# Created: 2011-04-30
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <me@mozman.at>"

from itertools import chain

from ..lldxf import const
from .polyfacebuilder import PolyfaceBuilder


class PolymeshMixin(object):
    def set_mesh_vertex(self, pos, point, dxfattribs=None):
        """ Set location and DXF attributes of a single mesh vertex.

        :param pos: 0-based (row, col)-tuple, position of mesh vertex
        :param point point: (x, y, z)-tuple, new 3D coordinates of the mesh vertex
        :param dxfattribs: dict of DXF attributes
        """
        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['location'] = point
        vertex = self.get_mesh_vertex(pos)
        vertex.update_dxf_attribs(dxfattribs)

    def get_mesh_vertex(self, pos):
        """ Get location of a single mesh vertex.

        :param pos: 0-based (row, col)-tuple, position of mesh vertex
        """
        m_count = self.dxf.m_count
        n_count = self.dxf.n_count
        m, n = pos
        if 0 <= m < m_count and 0 <= n < n_count:
            pos = m * n_count + n
            return self.__getitem__(pos)
        else:
            raise const.DXFIndexError(repr(pos))

    def get_mesh_vertex_cache(self):
        """ Get a MeshVertexCache() object for this Polymesh. The caching object provides fast access to the location
        attributes of the mesh vertices.
        """
        return MeshVertexCache(self)


class MeshVertexCache(object):
    """ Cache mesh vertices in a dict, keys are 0-based (row, col)-tuples.

    .. attribute:: vertices (read only)

       Dict of mesh vertices, keys are 0-based (row, col)-tuples. Writing to this dict doesn't change the DXF entity.

    - set vertex location: cache[row, col] = (x, y, z)
    - get vertex location: x, y, z = cache[row, col]
    """
    def __init__(self, mesh):
        self.vertices = self._setup(mesh, mesh.dxf.m_count, mesh.dxf.n_count)

    def _setup(self, mesh, m_count, n_count):
        cache = {}
        vertices = iter(mesh.vertices())
        for m in range(m_count):
            for n in range(n_count):
                cache[(m, n)] = next(vertices)
        return cache

    def __getitem__(self, pos):
        """ Get mesh vertex location as (x, y, z)-tuple.
        """
        try:
            return self.vertices[pos].dxf.location
        except KeyError:
            raise const.DXFIndexError(repr(pos))

    def __setitem__(self, pos, location):
        """ Get mesh vertex location as (x, y, z)-tuple.
        """
        try:
            self.vertices[pos].dxf.location = location
        except KeyError:
            raise const.DXFIndexError(repr(pos))


class PolyfaceMixin(object):
    """ Order of mesh_vertices and face_records *IS* important (ACAD2010)

    1. mesh_vertices: the polyface mesh vertex locations
    2. face_records: indices of the face forming vertices
    """
    def append_face(self, face, dxfattribs=None):
        """ Appends a single *face*. Appending single faces is very inefficient, try collecting single faces and use
        *Polyface.append_faces()*

        :param face: list of (x, y, z)-tuples
        :param dxfattribs: dict of DXF attributes
        """
        self.append_faces([face], dxfattribs)

    def append_faces(self, faces, dxfattribs=None):
        """ Append multiple *faces*. *faces* is a list of single faces and a single face is a list of (x, y, z)-tuples.

        :param faces: list of (list of (x, y, z)-tuples)
        :param dxfattribs: dict of DXF attributes
        """
        def new_face_record():
            dxfattribs['flags'] = const.VTX_3D_POLYFACE_MESH_VERTEX
            return self._new_entity('VERTEX', dxfattribs)

        if dxfattribs is None:
            dxfattribs = {}

        existing_vertices, existing_faces = self.indexed_faces()
        # existing_faces is a generator, can't append new data
        new_faces = []
        for face in faces:
            # convert face point coordinates to DXF Vertex() objects.
            face_mesh_vertices = self._points_to_dxf_vertices(face, {})
            # index of first new vertex
            index = len(existing_vertices)
            existing_vertices.extend(face_mesh_vertices)
            # create a new face_record with all indices set to 0
            face_record = Face(new_face_record(), existing_vertices)
            # set correct indices
            face_record.indices = tuple(range(index, index+len(face_mesh_vertices)))
            new_faces.append(face_record)
        self._rebuild(chain(existing_faces, new_faces))

    def _rebuild(self, faces, precision=6):
        """ Build a valid Polyface() structure out of *faces*.

        :param faces: list of Face() objects.
        """
        polyface_builder = PolyfaceBuilder(faces, precision=precision)
        self._unlink_all_vertices()  # but don't remove it from database
        self._append_vertices(polyface_builder.get_vertices())
        self.update_count(polyface_builder.nvertices, polyface_builder.nfaces)

    def update_count(self, nvertices, nfaces):
        self.dxf.m_count = nvertices
        self.dxf.n_count = nfaces

    def optimize(self, precision=6):
        """ Rebuilds polyface with vertex optimization. Merges vertices with nearly same vertex locations.
        Polyfaces created by *ezdxf* are optimized automatically.

        :param int precision: decimal precision for determining identical vertex locations
        """
        vertices, faces = self.indexed_faces()
        self._rebuild(faces, precision)

    def faces(self):
        """ Iterate over all faces, a face is a tuple of vertices.
        result is a list: vertex, vertex, vertex, [vertex,] face_record
        """
        faces = self.indexed_faces()[1]  # just need the faces generator
        for face in faces:
            face_vertices = list(face)
            face_vertices.append(face.face_record)
            yield face_vertices

    def indexed_faces(self):
        """ Returns a list of all vertices and a generator of Face() objects.
        """
        vertices = []
        face_records = []
        for vertex in self.vertices():
            (vertices if vertex.is_poly_face_mesh_vertex else face_records).append(vertex)

        faces = (Face(face_record, vertices) for face_record in face_records)
        return vertices, faces


class Face(object):
    """ Represents a single face of a polyface structure.

    .. attribute:: Face.vertices

        List of all polyface vertices.

    .. attribute:: Face.face_record

        The face forming vertex of type ``AcDbFaceRecord``, contains the indices to the face building vertices. Indices
        of the DXF structure are 1-based and a negative index indicates the beginning of an invisible edge.
        Face.face_record.dxf.color determines the color of the face.

    .. attribute:: Face.indices

        Indices to the face building vertices as tuple. This indices are 0-base and are used to get vertices from the
        list *Face.vertices*.
    """
    def __init__(self, face_record, vertices):
        self.vertices = vertices
        self.face_record = face_record
        self.indices = self._indices()

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, pos):
        return self.vertices[self.indices[pos]]

    def __iter__(self):
        return (self.vertices[index] for index in self.indices)

    def points(self):
        return (vertex.dxf.location for vertex in self)

    def _raw_indices(self):
        return (self.face_record.get_dxf_attrib(name, 0) for name in const.VERTEXNAMES)

    def _indices(self):
        return tuple(abs(index)-1 for index in self._raw_indices() if index != 0)

    def is_edge_visible(self, pos):
        name = const.VERTEXNAMES[pos]
        return self.face_record.get_dxf_attrib(name) > 0
