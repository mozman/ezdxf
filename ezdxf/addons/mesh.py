# Author:  mozman <me@mozman.at>
# Purpose: simple mesh representaion
# module belongs to package ezdxf.addons
# Created: 10.12.2016
# License: MIT License


class MeshBuilder(object):
    def __init__(self):
        self._vertices = []
        self._faces = []
        self._edges = []

    def add_face(self, vertices):
        self._faces.append(self.add_vertices(vertices))

    def add_edge(self, vertices):
        self._edges.append(self.add_vertices(vertices))

    def add_vertices(self, vertices):
        start_index = len(self._vertices)
        self._vertices.extend(vertices)
        return tuple(range(start_index, len(self._vertices)))

    def add_mesh(self, vertices, faces=None, edges=None):
        if faces is None:
            faces = []
        if edges is None:
            edges = []
        indices = self.add_vertices(vertices)

        for v1, v2 in edges:
            self._edges.append((indices[v1], indices[v2]))

        for face_vertices in faces:
            self._faces.append(tuple(indices[vi] for vi in face_vertices))

    def get_vertices(self):
        return self._vertices

    def get_faces(self):
        return self._faces

    def get_edges(self):
        return self._edges

    def render(self, layout, dxfattribs=None):
        mesh = layout.add_mesh(dxfattribs)
        with mesh.edit_data() as data:
            data.vertices = self.get_vertices()
            data.faces = self.get_faces()


class MeshVertexMerger(MeshBuilder):
    def __init__(self, precision=6):
        super(MeshVertexMerger, self).__init__()
        self.vertices = {}
        self.precision = precision

    def add_vertices(self, vertices):
        ndigits = self.precision
        indices = []
        _vertices = self.vertices

        for vertex in ((round(x, ndigits), round(y, ndigits), round(z, ndigits)) for x, y, z in vertices):
            try:
                indices.append(_vertices[vertex])
            except KeyError:
                index = len(_vertices)
                _vertices[vertex] = index
                indices.append(index)
        return tuple(indices)

    def get_vertices(self):
        return [key for value, key in sorted((v, k) for k, v in self.vertices.items())]




