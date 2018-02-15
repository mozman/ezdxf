# Author:  mozman <me@mozman.at>
# Purpose: simple mesh builders
# module belongs to package ezdxf.addons
# Created: 10.12.2016
# License: MIT License


class MeshBuilder(object):
    """
    A simple Mesh builder. Stores a list of vertices, a list of edges where an edge is a list of indices into the
    vertices list, and a faces list where each face is a list of indices into the vertices list.

    Can only create new meshes.

    """
    def __init__(self):
        self._vertices = []
        self._faces = []
        self._edges = []

    def add_face(self, vertices):
        """
        Add a face to the mesh. a face consist of at least 3 vertices. Each vertex is a (x, y, z) tuple and will be
        added to the mesh and the resulting vertex indices will be added to the mesh faces list. The stored face is a
        list [index v1, index v2, index v3, ...].

        Args:
            vertices: list of at least 3 vertices [(x1, y1, z1), (x2, y2, z2), (x3, y3, y3), ...]

        Returns:

        """
        self._faces.append(self.add_vertices(vertices))

    def add_edge(self, vertices):
        """
        An edge consist of two vertices [v1, v2]. Each vertex is a (x, y, z) tuple and will be added to the mesh
        and the resulting vertex indices will be added to the mesh edges list. The stored edge is [index v1, index v2]

        Args:
            vertices: list of 2 vertices : [(x1, y1, z1), (x2, y2, z2)]

        """
        self._edges.append(self.add_vertices(vertices))

    def add_vertices(self, vertices):
        """
        Add new vertices to the mesh.

        e.g: adding 4 vertices to an empty mesh, returns the indices (0, 1, 2, 3), adding additional 4 vertices
        return s the indices (4, 5, 6, 7)

        Args:
            vertices: list of vertices, vertex as (x, y, z) tuple

        Returns:
            A tuples of the vertex indices.

        """
        start_index = len(self._vertices)
        self._vertices.extend(vertices)
        return tuple(range(start_index, len(self._vertices)))

    def add_mesh(self, vertices, faces=None, edges=None):
        """
        Add another mesh to this mesh.

        Args:
            vertices: list of vertices, a vertex is a (x, y, z)
            faces: list of faces, a face is a list of vertex indices
            edges: list of edges, an edge is a list of vertex indices

        """
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

    def render(self, layout, dxfattribs=None, matrix=None):
        """
        Render mesh as MESH entity into layout.

        Args:
            layout: ezdxf Layout() object
            dxfattribs: dict of DXF attributes e.g. {'layer': 'mesh', 'color': 7}
            matrix: transformation matrix, requires a .transform_vectors() method
        """
        mesh = layout.add_mesh(dxfattribs=dxfattribs)
        with mesh.edit_data() as data:
            if matrix is not None:
                data.vertices = matrix.transform_vectors(self.get_vertices())
            else:
                data.vertices = self.get_vertices()
            data.edges = self.get_edges()
            data.faces = self.get_faces()


class MeshVertexMerger(MeshBuilder):
    """
    Mesh with unique vertices.

    Can only create new meshes.

    """
    def __init__(self, precision=6):
        super(MeshVertexMerger, self).__init__()
        self.vertices = {}
        self.precision = precision

    def add_vertices(self, vertices):
        """
        Add new vertices only, if no vertex with identical x, y, z coordinates already exists, else the index of the
        existing vertex is returned as index of the new (not added) vertex.

        Args:
            vertices: list of vertices, vertex as (x, y, z) tuple

        Returns:
            A tuples of the vertex indices.

        """
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
