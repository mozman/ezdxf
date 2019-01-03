# Purpose: simple mesh builders
# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from typing import List, Sequence, Tuple, Iterable, TYPE_CHECKING
from ezdxf.algebra.vector import Vector
from ezdxf.lldxf.const import DXFValueError

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex, Matrix44, GenericLayoutType


class MeshBuilder:
    """
    A simple Mesh builder. Stores a list of vertices, a list of edges where an edge is a list of indices into the
    vertices list, and a faces list where each face is a list of indices into the vertices list.

    The render() method, renders the mesh into a DXF MESH entity. The MESH entity supports ngons in AutoCAD, ngons are
    polygons with more than 4 vertices.

    Can only create new meshes.

    """

    def __init__(self):
        self.vertices = []  # type: list[Vector]  # vertex storage, list of (x, y, z) tuples or Vector() objects
        self.faces = []  # type: List[Sequence[int]]  # face storage, each face is a list/tuple of vertex indices (v0, v1, v2, v3, ....), AutoCAD supports ngons
        self.edges = []  # type: list[Tuple[int, int]]  # edge storage, each edge is a 2-tuple of vertex indices (v0, v1)

    def add_face(self, vertices: Iterable['Vertex']) -> None:
        """
        Add a face as vertices list to the mesh. A face requires at least 3 vertices, each vertex is a (x, y, z) tuple.
        A face is stored as index list, which means, a face does not contain the vertex itself, but the indices of the
        vertices in the vertex list.

        list [index v1, index v2, index v3, ...].

        Args:
            vertices: list of at least 3 vertices [(x1, y1, z1), (x2, y2, z2), (x3, y3, y3), ...]

        """
        self.faces.append(self.add_vertices(vertices))

    def add_edge(self, vertices: Iterable['Vertex']) -> None:
        """
        An edge consist of two vertices [v1, v2]. Each vertex is a (x, y, z) tuple and will be added to the mesh
        and the resulting vertex indices will be added to the mesh edges list. The stored edge is [index v1, index v2]

        Args:
            vertices: list of 2 vertices : [(x1, y1, z1), (x2, y2, z2)]

        """
        vertices = list(vertices)
        if len(vertices) == 2:
            self.edges.append(self.add_vertices(vertices))
        else:
            raise DXFValueError('Invalid vertices count, expected two vertices.')

    def add_vertices(self, vertices: Iterable['Vertex']) -> Tuple:
        """
        Add new vertices to the mesh.

        e.g. adding 4 vertices to an empty mesh, returns the indices (0, 1, 2, 3), adding additional 4 vertices
        return s the indices (4, 5, 6, 7)

        Args:
            vertices: list of vertices, vertex as (x, y, z) tuple

        Returns: a tuple of vertex indices.

        """
        start_index = len(self.vertices)
        self.vertices.extend(vertices)
        return tuple(range(start_index, len(self.vertices)))

    def add_mesh(self,
                 vertices: List[Vector] = None,
                 faces: List[Sequence[int]] = None,
                 edges: List[Tuple[int, int]] = None,
                 mesh: 'MeshBuilder' = None) -> None:
        """
        Add another mesh to this mesh.

        Args:
            vertices: list of vertices, a vertex is a (x, y, z)
            faces: list of faces, a face is a list of vertex indices
            edges: list of edges, an edge is a list of vertex indices
            mesh: another mesh entity, mesh overrides vertices, faces and edges

        """
        if mesh is not None:
            vertices = mesh.vertices
            faces = mesh.faces
            edges = mesh.edges

        if vertices is None:
            raise ValueError("Requires vertices or another mesh.")
        if faces is None:
            faces = []
        if edges is None:
            edges = []
        indices = self.add_vertices(vertices)

        for v1, v2 in edges:
            self.edges.append((indices[v1], indices[v2]))

        for face_vertices in faces:
            self.faces.append(tuple(indices[vi] for vi in face_vertices))

    def transform(self, matrix: 'Matrix44') -> 'MeshBuilder':
        """
        Transform actual mesh into a new mesh by applying the transformation matrix to vertices.

        Args:
            matrix: 4x4 transformation matrix as Matrix44() object

        Returns: new Mesh() object

        """
        mesh = self.__class__()
        mesh.add_mesh(
            vertices=matrix.transform_vectors(self.vertices),
            faces=self.faces,
            edges=self.edges,
        )
        return mesh

    def translate(self, x: float = 0, y: float = 0, z: float = 0) -> None:
        """
        Translate mesh inplace.

        """
        if isinstance(x, (float, int)):
            t = Vector(x, y, z)
        else:
            t = Vector(x)
        for index, vertex in enumerate(self.vertices):
            self.vertices[index] = t + vertex

    def scale(self, sx: float = 1, sy: float = 1, sz: float = 1) -> None:
        """
        Scale mesh inplace.

        """
        self.vertices = [Vector(v[0] * sx, v[1] * sy, v[2] * sz) for v in self.vertices]
        for index, vertex in enumerate(self.vertices):
            self.vertices[index] = Vector(vertex[0] * sx, vertex[1] * sy, vertex[2] * sz)

    def render(self, layout: 'GenericLayoutType', dxfattribs: dict = None, matrix: 'Matrix44' = None):
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
                data.vertices = matrix.transform_vectors(self.vertices)
            else:
                data.vertices = self.vertices
            data.edges = self.edges
            data.faces = self.faces

    @classmethod
    def from_mesh(cls, other: 'MeshBuilder') -> 'MeshBuilder':
        mesh = cls()
        mesh.add_mesh(mesh=other)
        return mesh


class MeshVertexMerger(MeshBuilder):
    """
    Mesh with unique vertices. Resulting meshes have no doublets, but MeshVertexMerger() needs extra memory for
    bookkeeping.

    Can only create new meshes.

    """

    def __init__(self, precision: int = 6):
        super().__init__()
        self.ledger = {}
        self.precision = precision

    def key(self, vertex: 'Vertex') -> 'Vertex':
        p = self.precision
        return round(vertex[0], p), round(vertex[1], p), round(vertex[2], p)

    def add_vertices(self, vertices: Iterable['Vertex']) -> Sequence[int]:
        """
        Add new vertices only, if no vertex with identical x, y, z coordinates already exists, else the index of the
        existing vertex is returned as index of the new (not added) vertex.

        Args:
            vertices: list of vertices, vertex as (x, y, z) tuple

        Returns:
            A tuples of the vertex indices.

        """
        indices = []
        for vertex in vertices:
            key = self.key(vertex)
            try:
                indices.append(self.ledger[key])
            except KeyError:
                index = len(self.vertices)
                self.vertices.append(vertex)
                self.ledger[key] = index
                indices.append(index)
        return tuple(indices)

    def index(self, vertex: 'Vertex') -> int:
        """
        Get index of vertex, raise KeyError if not found.

        Args:
            vertex: (x, y, z) vertex

        Returns: index of vertex as int

        """
        try:
            return self.ledger[self.key(vertex)]
        except KeyError:
            raise IndexError("vertex {} not found.".format(vertex))
