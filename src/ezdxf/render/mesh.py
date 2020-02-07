# Purpose: simple mesh builders
# Copyright (c) 2018-2020 Manfred Moitzi
# License: MIT License
from typing import List, Sequence, Tuple, Iterable, TYPE_CHECKING
from ezdxf.lldxf.const import DXFValueError
from ezdxf.math import Matrix44, Vector
from ezdxf.math.construct3d import is_planar_face, subdivide_face
if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex, BaseLayout, UCS


class MeshBuilder:
    """
    A simple Mesh builder. Stores a list of vertices, a list of edges where an edge is a list of indices into the
    vertices list, and a faces list where each face is a list of indices into the vertices list.

    The render() method, renders the mesh into a DXF MESH entity. The MESH entity supports ngons in AutoCAD, ngons are
    polygons with more than 4 vertices.

    Can only create new meshes.

    """

    def __init__(self):
        self.vertices = []  # type: List[Vector]  # vertex storage, list of (x, y, z) tuples or Vector() objects
        self.faces = []  # type: List[Sequence[int]]  # face storage, each face is a tuple of vertex indices (v0, v1, v2, v3, ....), AutoCAD supports ngons
        self.edges = []  # type: List[Tuple[int, int]]  # edge storage, each edge is a 2-tuple of vertex indices (v0, v1)

    def copy(self):
        """ Returns a copy of mesh. """
        return self.from_builder(self)

    def faces_as_vertices(self) -> Iterable[List[Vector]]:
        """ Iterate over all mesh faces as list of vertices. """
        v = self.vertices
        for face in self.faces:
            yield [v[index] for index in face]

    def edges_as_vertices(self) -> Iterable[Tuple[Vector, Vector]]:
        """ Iterate over all mesh edges as tuple of two vertices. """
        v = self.vertices
        for edge in self.edges:
            yield v[edge[0]], v[edge[1]]

    def add_face(self, vertices: Iterable['Vertex']) -> None:
        """
        Add a face as vertices list to the mesh. A face requires at least 3 vertices, each vertex is a ``(x, y, z)``
        tuple or :class:`~ezdxf.math.Vector` object. The new vertex indices are stored as face in the :attr:`faces`
        list.

        Args:
            vertices: list of at least 3 vertices ``[(x1, y1, z1), (x2, y2, z2), (x3, y3, y3), ...]``

        """
        self.faces.append(self.add_vertices(vertices))

    def add_edge(self, vertices: Iterable['Vertex']) -> None:
        """
        An edge consist of two vertices ``[v1, v2]``, each vertex is a ``(x, y, z)`` tuple or a
        :class:`~ezdxf.math.Vector` object. The new vertex indices are stored as edge in the :attr:`edges` list.

        Args:
            vertices: list of 2 vertices : [(x1, y1, z1), (x2, y2, z2)]

        """
        vertices = list(vertices)
        if len(vertices) == 2:
            self.edges.append(self.add_vertices(vertices))
        else:
            raise DXFValueError('Invalid vertices count, expected two vertices.')

    def add_vertices(self, vertices: Iterable['Vertex']) -> Sequence[int]:
        """
        Add new vertices to the mesh, each vertex is a ``(x, y, z)`` tuple or a :class:`~ezdxf.math.Vector` object,
        returns the indices of the `vertices` added to the :attr:`vertices` list.

        e.g. adding 4 vertices to an empty mesh, returns the indices ``(0, 1, 2, 3)``, adding additional 4 vertices
        returns the indices ``(4, 5, 6, 7)``.

        Args:
            vertices: list of vertices, vertex as ``(x, y, z)`` tuple or :class:`~ezdxf.math.Vector` objects

        Returns:
            tuple: indices of the `vertices` added to the :attr:`vertices` list

        """
        start_index = len(self.vertices)
        self.vertices.extend(vertices)
        return tuple(range(start_index, len(self.vertices)))

    def add_mesh(self,
                 vertices: List[Vector] = None,
                 faces: List[Sequence[int]] = None,
                 edges: List[Tuple[int, int]] = None,
                 mesh=None) -> None:
        """
        Add another mesh to this mesh.

        A `mesh` can be a :class:`MeshBuilder`, :class:`MeshVertexMerger` or :class:`~ezdxf.entities.Mesh` object
        or requires the attributes :attr:`vertices`, :attr:`edges` and :attr:`faces`.

        Args:
            vertices: list of vertices, a vertex is a ``(x, y, z)`` tuple or :class:`~ezdxf.math.Vector` object
            faces: list of faces, a face is a list of vertex indices
            edges: list of edges, an edge is a list of vertex indices
            mesh: another mesh entity

        """
        if mesh is not None:
            vertices = mesh.vertices
            faces = mesh.faces
            edges = mesh.edges

        if vertices is None:
            raise ValueError("Requires vertices or another mesh.")
        faces = faces or []
        edges = edges or []
        indices = self.add_vertices(vertices)

        for v1, v2 in edges:
            self.edges.append((indices[v1], indices[v2]))

        for face_vertices in faces:
            self.faces.append(tuple(indices[vi] for vi in face_vertices))

    def has_none_planar_faces(self) -> bool:
        """ Returns ``True`` if any face is none planar. """
        return not all(is_planar_face(face) for face in self.faces_as_vertices())

    def render(self, layout: 'BaseLayout', dxfattribs: dict = None, matrix: 'Matrix44' = None):
        """
        Render mesh as :class:`~ezdxf.entities.Mesh` entity into `layout`.

        Args:
            layout: :class:`~ezdxf.layouts.BaseLayout` object
            dxfattribs: dict of DXF attributes e.g. ``{'layer': 'mesh', 'color': 7}``
            matrix: transformation matrix of type :class:`~ezdxf.math.Matrix44`

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
    def from_mesh(cls, other):
        """
        Create new mesh from other mesh as class method.

        Args:
            other: `mesh` of type :class:`MeshBuilder` and inherited or DXF :class:`~ezdxf.entities.Mesh` entity or
                   any object providing attributes :attr:`vertices`, :attr:`edges` and :attr:`faces`.

        """
        # just copy properties
        mesh = cls()
        mesh.add_mesh(mesh=other)
        return mesh

    @classmethod
    def from_builder(cls, other: 'MeshBuilder'):
        """
        Create new mesh from other mesh builder, faster than :meth:`from_mesh` but supports only
        :class:`MeshBuilder` and inherited classes.
        """
        # just copy properties
        mesh = cls()
        mesh.vertices = list(other.vertices)
        mesh.edges = list(other.edges)
        mesh.faces = list(other.faces)
        return mesh


class MeshTransformer(MeshBuilder):
    """ A mesh builder with inplace transformation support. """

    def subdivide(self, level: int = 1, quads=True, edges=False) -> 'MeshTransformer':
        """ Returns a new :class:`MeshTransformer` object with subdivided faces and edges.

        Args:
             level: subdivide levels from 1 to max of 5
             quads: create quad faces if ``True`` else create triangles
             edges: also subdivide edges if ``True``
        """
        mesh = self
        level = min(int(level), 5)
        while level > 0:
            mesh = _subdivide(mesh, quads, edges)
            level -= 1
        return MeshTransformer.from_builder(mesh)

    def transform(self, matrix: 'Matrix44'):
        """
        Transform mesh inplace by applying the transformation `matrix`.

        Args:
            matrix: 4x4 transformation matrix as :class:`~ezdxf.math.Matrix44` object

        """
        self.vertices = matrix.transform_vectors(self.vertices)
        return self

    def translate(self, x: float = 0, y: float = 0, z: float = 0):
        """
        Translate mesh inplace.

        Args:
            x: translation in x-axis
            y: translation in y-axis
            z: translation in z-axis

        """
        if isinstance(x, (float, int)):
            t = Vector(x, y, z)
        else:
            t = Vector(x)
        for index, vertex in enumerate(self.vertices):
            self.vertices[index] = t + vertex
        return self

    def scale(self, sx: float = 1, sy: float = 1, sz: float = 1):
        """
        Scale mesh inplace.

        Args:
            sx: scale factor for x-axis
            sy: scale factor for y-axis
            sz: scale factor for z-axis

        """
        self.vertices = [Vector(x * sx, y * sy, z * sz) for x, y, z in self.vertices]
        return self

    def scale_uniform(self, s: float):
        """
        Scale mesh uniform inplace.

        Args:
            s: scale factor for x-, y- and z-axis

        """
        self.vertices = [v * s for v in self.vertices]
        return self

    def rotate_x(self, angle: float):
        """
        Rotate mesh around x-axis about `angle` inplace.

        Args:
            angle: rotation angle in radians

        """
        self.vertices = Matrix44.x_rotate(angle).transform_vectors(self.vertices)
        return self

    def rotate_y(self, angle: float):
        """
        Rotate mesh around y-axis about `angle` inplace.

        Args:
            angle: rotation angle in radians

        """
        self.vertices = Matrix44.y_rotate(angle).transform_vectors(self.vertices)
        return self

    def rotate_z(self, angle: float):
        """
        Rotate mesh around z-axis about `angle` inplace.

        Args:
            angle: rotation angle in radians

        """
        self.vertices = Matrix44.z_rotate(angle).transform_vectors(self.vertices)
        return self

    def rotate_axis(self, axis: 'Vertex', angle: float):
        """
        Rotate mesh around an arbitrary axis located in the origin (0, 0, 0) about `angle`.

        Args:
            axis: rotation axis as Vector
            angle: rotation angle in radians

        """
        self.vertices = Matrix44.axis_rotate(axis, angle).transform_vectors(self.vertices)
        return self

    def transform_to_wcs(self, ucs: 'UCS'):
        """
        Transform local UCS vertices to WCS vertices.

        Args:
            ucs: user coordinate system

        """
        self.vertices = list(ucs.points_to_wcs(self.vertices))
        return self


def _subdivide(mesh, quads=True, edges=False) -> 'MeshVertexMerger':
    """ Returns a new :class:`MeshVertexMerger` object with subdivided faces and edges.

    Args:
         quads: create quad faces if ``True`` else create triangles
         edges: also subdivide edges if ``True``

    """
    new_mesh = MeshVertexMerger()
    for vertices in mesh.faces_as_vertices():
        if len(vertices) < 3:
            continue
        for face in subdivide_face(vertices, quads):
            new_mesh.add_face(face)

    if edges:
        for start, end in mesh.edges_as_vertices():
            mid = start.lerp(end)
            new_mesh.add_edge((start, mid))
            new_mesh.add_edge((mid, end))

    return new_mesh


class MeshVertexMerger(MeshBuilder):
    """
    Mesh with unique vertices. Resulting meshes have no doublets, but MeshVertexMerger() needs extra memory for
    bookkeeping.

    """

    # can not support vertex transformation
    def __init__(self, precision: int = 6):
        """
        Args:
            precision: floating point precision for vertex rounding

        """
        super().__init__()
        self.ledger = {}
        self.precision = precision

    def key(self, vertex: 'Vertex') -> 'Vertex':
        """ Returns rounded vertex. (internal API) """
        p = self.precision
        return round(vertex[0], p), round(vertex[1], p), round(vertex[2], p)

    def add_vertices(self, vertices: Iterable['Vertex']) -> Sequence[int]:
        """
        Add new `vertices` only, if no vertex with identical ``(x, y, z)`` coordinates already exist, else the index of
        the existing vertex is returned as index of the added vertices.

        Args:
            vertices: list of vertices, vertex as ``(x, y, z)`` tuple or :class:`~ezdxf.math.Vector` objects

        Returns:
            tuple: indices of the `vertices` added to the :attr:`~MeshBuilder.vertices` list

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
        Get index of `vertex`, raise :class:`KeyError` if not found.

        Args:
            vertex: ``(x, y, z)`` tuple or :class:`~ezdxf.math.Vector` object

        (internal API)
        """
        try:
            return self.ledger[self.key(vertex)]
        except KeyError:
            raise IndexError("vertex {} not found.".format(vertex))

    @classmethod
    def from_builder(cls, other: 'MeshBuilder'):
        """ Create new mesh from other mesh builder. """
        # rebuild from scratch to crate a valid ledger
        return cls.from_mesh(other)
