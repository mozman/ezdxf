# Copyright (c) 2018-2021 Manfred Moitzi
# License: MIT License
from typing import (
    List,
    Sequence,
    Tuple,
    Iterable,
    TYPE_CHECKING,
    Union,
    Dict,
    TypeVar,
    Type,
)
from ezdxf.lldxf.const import DXFValueError
from ezdxf.math import (
    Matrix44,
    Vec3,
    NULLVEC,
    is_planar_face,
    subdivide_face,
    normal_vector_3p,
    subdivide_ngons,
)

if TYPE_CHECKING:
    from ezdxf.eztypes import (
        Vertex,
        UCS,
        Polyface,
        Polymesh,
        GenericLayoutType,
        Mesh,
    )

T = TypeVar("T")


class MeshBuilder:
    """A simple Mesh builder. Stores a list of vertices, a list of edges where
    an edge is a list of indices into the vertices list, and a faces list where
    each face is a list of indices into the vertices list.

    The render() method, renders the mesh into a DXF MESH entity. The MESH
    entity supports ngons in AutoCAD, ngons are polygons with more than 4
    vertices.

    Can only create new meshes.

    """

    def __init__(self):
        # vertex storage, list of (x, y, z) tuples or Vec3() objects
        self.vertices: List[Vec3] = []
        # face storage, each face is a tuple of vertex indices (v0, v1, v2, v3, ....),
        # AutoCAD supports ngons
        self.faces: List[Sequence[int]] = []
        # edge storage, each edge is a 2-tuple of vertex indices (v0, v1)
        self.edges: List[Tuple[int, int]] = []

    def copy(self):
        """Returns a copy of mesh."""
        return self.from_builder(self)

    def faces_as_vertices(self) -> Iterable[List[Vec3]]:
        """Iterate over all mesh faces as list of vertices."""
        v = self.vertices
        for face in self.faces:
            yield [v[index] for index in face]

    def edges_as_vertices(self) -> Iterable[Tuple[Vec3, Vec3]]:
        """Iterate over all mesh edges as tuple of two vertices."""
        v = self.vertices
        for edge in self.edges:
            yield v[edge[0]], v[edge[1]]

    def add_face(self, vertices: Iterable["Vertex"]) -> None:
        """Add a face as vertices list to the mesh. A face requires at least 3
        vertices, each vertex is a ``(x, y, z)`` tuple or
        :class:`~ezdxf.math.Vec3` object. The new vertex indices are stored as
        face in the :attr:`faces` list.

        Args:
            vertices: list of at least 3 vertices ``[(x1, y1, z1), (x2, y2, z2),
                (x3, y3, y3), ...]``

        """
        self.faces.append(self.add_vertices(vertices))

    def add_edge(self, vertices: Iterable["Vertex"]) -> None:
        """An edge consist of two vertices ``[v1, v2]``, each vertex is a
        ``(x, y, z)`` tuple or a :class:`~ezdxf.math.Vec3` object. The new
        vertex indices are stored as edge in the :attr:`edges` list.

        Args:
            vertices: list of 2 vertices : [(x1, y1, z1), (x2, y2, z2)]

        """
        vertices = list(vertices)
        if len(vertices) == 2:
            self.edges.append(self.add_vertices(vertices))  # type: ignore
        else:
            raise DXFValueError(
                "Invalid vertices count, expected two vertices."
            )

    def add_vertices(self, vertices: Iterable["Vertex"]) -> Sequence[int]:
        """Add new vertices to the mesh, each vertex is a ``(x, y, z)`` tuple
        or a :class:`~ezdxf.math.Vec3` object, returns the indices of the
        `vertices` added to the :attr:`vertices` list.

        e.g. adding 4 vertices to an empty mesh, returns the indices
        ``(0, 1, 2, 3)``, adding additional 4 vertices returns the indices
        ``(4, 5, 6, 7)``.

        Args:
            vertices: list of vertices, vertex as ``(x, y, z)`` tuple or
                :class:`~ezdxf.math.Vec3` objects

        Returns:
            tuple: indices of the `vertices` added to the :attr:`vertices` list

        """
        start_index = len(self.vertices)
        self.vertices.extend(Vec3.generate(vertices))
        return tuple(range(start_index, len(self.vertices)))

    def add_mesh(
        self,
        vertices: List[Vec3] = None,
        faces: List[Sequence[int]] = None,
        edges: List[Tuple[int, int]] = None,
        mesh=None,
    ) -> None:
        """Add another mesh to this mesh.

        A `mesh` can be a :class:`MeshBuilder`, :class:`MeshVertexMerger` or
        :class:`~ezdxf.entities.Mesh` object or requires the attributes
        :attr:`vertices`, :attr:`edges` and :attr:`faces`.

        Args:
            vertices: list of vertices, a vertex is a ``(x, y, z)`` tuple or
                :class:`~ezdxf.math.Vec3` object
            faces: list of faces, a face is a list of vertex indices
            edges: list of edges, an edge is a list of vertex indices
            mesh: another mesh entity

        """
        if mesh is not None:
            vertices = Vec3.list(mesh.vertices)
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
        """Returns ``True`` if any face is none planar."""
        return not all(
            is_planar_face(face) for face in self.faces_as_vertices()
        )

    def render_mesh(
        self,
        layout: "GenericLayoutType",
        dxfattribs: dict = None,
        matrix: "Matrix44" = None,
        ucs: "UCS" = None,
    ):
        """Render mesh as :class:`~ezdxf.entities.Mesh` entity into `layout`.

        Args:
            layout: :class:`~ezdxf.layouts.BaseLayout` object
            dxfattribs: dict of DXF attributes e.g. ``{'layer': 'mesh', 'color': 7}``
            matrix: transformation matrix of type :class:`~ezdxf.math.Matrix44`
            ucs: transform vertices by :class:`~ezdxf.math.UCS` to :ref:`WCS`

        """
        vertices = self.vertices
        if matrix is not None:
            vertices = list(matrix.transform_vertices(vertices))
        if ucs is not None:
            vertices = ucs.points_to_wcs(vertices)  # type: ignore
        mesh = layout.add_mesh(dxfattribs=dxfattribs)
        with mesh.edit_data() as data:
            # data will be copied at setting in edit_data()
            data.vertices = vertices
            data.edges = self.edges
            data.faces = self.faces  # type: ignore
        return mesh

    render = render_mesh  # TODO: 2021-02-10 - compatibility alias

    def render_normals(
        self,
        layout: "GenericLayoutType",
        length: float = 1,
        relative=True,
        dxfattribs: dict = None,
    ):
        """Render face normals as :class:`~ezdxf.entities.Line` entities into
        `layout`, useful to check orientation of mesh faces.

        Args:
            layout: :class:`~ezdxf.layouts.BaseLayout` object
            length: visual length of normal, use length < 0 to point normals in
                opposite direction
            relative: scale length relative to face size if ``True``
            dxfattribs: dict of DXF attributes e.g. ``{'layer': 'normals', 'color': 6}``

        """
        for face in self.faces_as_vertices():
            count = len(face)
            if count < 3:
                continue
            center = sum(face) / count
            i = 0
            n = NULLVEC
            while i <= count - 3:
                n = normal_vector_3p(face[i], face[i + 1], face[i + 2])
                if n != NULLVEC:  # not colinear vectors
                    break
                i += 1

            if relative:
                _length = (face[0] - center).magnitude * length
            else:
                _length = length
            layout.add_line(center, center + n * _length, dxfattribs=dxfattribs)

    @classmethod
    def from_mesh(cls: Type[T], other: Union["MeshBuilder", "Mesh"]) -> T:
        """Create new mesh from other mesh as class method.

        Args:
            other: `mesh` of type :class:`MeshBuilder` and inherited or DXF
                :class:`~ezdxf.entities.Mesh` entity or any object providing
                attributes :attr:`vertices`, :attr:`edges` and :attr:`faces`.

        """
        # just copy properties
        mesh = cls()
        assert isinstance(mesh, MeshBuilder)
        mesh.add_mesh(mesh=other)
        return mesh  # type: ignore

    @classmethod
    def from_polyface(cls: Type[T], other: Union["Polymesh", "Polyface"]) -> T:
        """Create new mesh from a  :class:`~ezdxf.entities.Polyface` or
        :class:`~ezdxf.entities.Polymesh` object.

        """
        if other.dxftype() != "POLYLINE":
            raise TypeError(f"Unsupported DXF type: {other.dxftype()}")

        mesh = cls()
        assert isinstance(mesh, MeshBuilder)
        if other.is_poly_face_mesh:
            _, faces = other.indexed_faces()  # type: ignore
            for face in faces:
                mesh.add_face(face.points())
        elif other.is_polygon_mesh:
            vertices = other.get_mesh_vertex_cache()  # type: ignore
            for m in range(other.dxf.m_count - 1):
                for n in range(other.dxf.n_count - 1):
                    mesh.add_face(
                        (
                            vertices[m, n],
                            vertices[m, n + 1],
                            vertices[m + 1, n + 1],
                            vertices[m + 1, n],
                        )
                    )
        else:
            raise TypeError("Not a polymesh or polyface.")
        return mesh  # type: ignore

    def render_polyface(
        self,
        layout: "GenericLayoutType",
        dxfattribs: dict = None,
        matrix: "Matrix44" = None,
        ucs: "UCS" = None,
    ):
        """Render mesh as :class:`~ezdxf.entities.Polyface` entity into
        `layout`.

        Args:
            layout: :class:`~ezdxf.layouts.BaseLayout` object
            dxfattribs: dict of DXF attributes e.g. ``{'layer': 'mesh', 'color': 7}``
            matrix: transformation matrix of type :class:`~ezdxf.math.Matrix44`
            ucs: transform vertices by :class:`~ezdxf.math.UCS` to :ref:`WCS`

        """
        polyface = layout.add_polyface(dxfattribs=dxfattribs)
        t = MeshTransformer.from_builder(self)
        if matrix is not None:
            t.transform(matrix)
        if ucs is not None:
            t.transform(ucs.matrix)
        polyface.append_faces(subdivide_ngons(t.faces_as_vertices()))
        return polyface

    def render_3dfaces(
        self,
        layout: "GenericLayoutType",
        dxfattribs: dict = None,
        matrix: "Matrix44" = None,
        ucs: "UCS" = None,
    ):
        """Render mesh as :class:`~ezdxf.entities.Face3d` entities into
        `layout`.

        Args:
            layout: :class:`~ezdxf.layouts.BaseLayout` object
            dxfattribs: dict of DXF attributes e.g. ``{'layer': 'mesh', 'color': 7}``
            matrix: transformation matrix of type :class:`~ezdxf.math.Matrix44`
            ucs: transform vertices by :class:`~ezdxf.math.UCS` to :ref:`WCS`

        """
        t = MeshTransformer.from_builder(self)
        if matrix is not None:
            t.transform(matrix)
        if ucs is not None:
            t.transform(ucs.matrix)
        for face in subdivide_ngons(t.faces_as_vertices()):
            layout.add_3dface(face, dxfattribs=dxfattribs)

    @classmethod
    def from_builder(cls: Type[T], other: "MeshBuilder") -> T:
        """Create new mesh from other mesh builder, faster than
        :meth:`from_mesh` but supports only :class:`MeshBuilder` and inherited
        classes.

        """
        # just copy properties
        mesh = cls()
        assert isinstance(mesh, MeshBuilder)
        mesh.vertices = list(other.vertices)
        mesh.edges = list(other.edges)
        mesh.faces = list(other.faces)
        return mesh  # type: ignore


class MeshTransformer(MeshBuilder):
    """A mesh builder with inplace transformation support."""

    def subdivide(
        self, level: int = 1, quads=True, edges=False
    ) -> "MeshTransformer":
        """Returns a new :class:`MeshTransformer` object with subdivided faces
        and edges.

        Args:
             level: subdivide levels from 1 to max of 5
             quads: create quad faces if ``True`` else create triangles
             edges: also subdivide edges if ``True``
        """
        mesh = self
        level = min(int(level), 5)
        while level > 0:
            mesh = _subdivide(mesh, quads, edges)  # type: ignore
            level -= 1
        return MeshTransformer.from_builder(mesh)

    def transform(self, matrix: "Matrix44"):
        """Transform mesh inplace by applying the transformation `matrix`.

        Args:
            matrix: 4x4 transformation matrix as :class:`~ezdxf.math.Matrix44`
                object

        """
        self.vertices = list(matrix.transform_vertices(self.vertices))
        return self

    def translate(self, dx: float = 0, dy: float = 0, dz: float = 0):
        """Translate mesh inplace.

        Args:
            dx: translation in x-axis
            dy: translation in y-axis
            dz: translation in z-axis

        """
        if isinstance(dx, (float, int)):
            t = Vec3(dx, dy, dz)
        else:
            t = Vec3(dx)
        self.vertices = [t + v for v in self.vertices]
        return self

    def scale(self, sx: float = 1, sy: float = 1, sz: float = 1):
        """Scale mesh inplace.

        Args:
            sx: scale factor for x-axis
            sy: scale factor for y-axis
            sz: scale factor for z-axis

        """
        self.vertices = [
            Vec3(x * sx, y * sy, z * sz) for x, y, z in self.vertices
        ]
        return self

    def scale_uniform(self, s: float):
        """Scale mesh uniform inplace.

        Args:
            s: scale factor for x-, y- and z-axis

        """
        self.vertices = [v * s for v in self.vertices]
        return self

    def rotate_x(self, angle: float):
        """Rotate mesh around x-axis about `angle` inplace.

        Args:
            angle: rotation angle in radians

        """
        self.vertices = list(
            Matrix44.x_rotate(angle).transform_vertices(self.vertices)
        )
        return self

    def rotate_y(self, angle: float):
        """Rotate mesh around y-axis about `angle` inplace.

        Args:
            angle: rotation angle in radians

        """
        self.vertices = list(
            Matrix44.y_rotate(angle).transform_vertices(self.vertices)
        )
        return self

    def rotate_z(self, angle: float):
        """Rotate mesh around z-axis about `angle` inplace.

        Args:
            angle: rotation angle in radians

        """
        self.vertices = list(
            Matrix44.z_rotate(angle).transform_vertices(self.vertices)
        )
        return self

    def rotate_axis(self, axis: "Vertex", angle: float):
        """Rotate mesh around an arbitrary axis located in the origin (0, 0, 0)
        about `angle`.

        Args:
            axis: rotation axis as Vec3
            angle: rotation angle in radians

        """
        self.vertices = list(
            Matrix44.axis_rotate(axis, angle).transform_vertices(self.vertices)
        )
        return self


def _subdivide(mesh, quads=True, edges=False) -> "MeshVertexMerger":
    """Returns a new :class:`MeshVertexMerger` object with subdivided faces
    and edges.

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
    """Subclass of :class:`MeshBuilder`

    Mesh with unique vertices and no doublets, but needs extra memory for
    bookkeeping.

    :class:`MeshVertexMerger` creates a key for every vertex by rounding its
    components by the Python :func:`round` function and a given `precision`
    value. Each vertex with the same key gets the same vertex index, which is
    the index of first vertex with this key, so all vertices with the same key
    will be located at the location of this first vertex. If you want an average
    location of and for all vertices with the same key look at the
    :class:`MeshAverageVertexMerger` class.

    Args:
        precision: floating point precision for vertex rounding

    """

    # can not support vertex transformation
    def __init__(self, precision: int = 6):
        """
        Args:
            precision: floating point precision for vertex rounding

        """
        super().__init__()
        self.ledger: Dict["Vertex", int] = {}
        self.precision: int = precision

    def key(self, vertex: "Vertex") -> "Vertex":
        """Returns rounded vertex. (internal API)"""
        p = self.precision
        return round(vertex[0], p), round(vertex[1], p), round(vertex[2], p)

    def add_vertices(self, vertices: Iterable["Vertex"]) -> Sequence[int]:
        """Add new `vertices` only, if no vertex with identical (x, y, z)
        coordinates already exist, else the index of the existing vertex is
        returned as index of the added vertices.

        Args:
            vertices: list of vertices, vertex as (x, y, z) tuple or
                :class:`~ezdxf.math.Vec3` objects

        Returns:
            indices of the added `vertices`

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

    def index(self, vertex: "Vertex") -> int:
        """Get index of `vertex`, raise :class:`KeyError` if not found.

        Args:
            vertex: ``(x, y, z)`` tuple or :class:`~ezdxf.math.Vec3` object

        (internal API)
        """
        try:
            return self.ledger[self.key(vertex)]
        except KeyError:
            raise IndexError(f"Vertex {str(vertex)} not found.")

    @classmethod
    def from_builder(cls: Type[T], other: "MeshBuilder") -> T:
        """Create new mesh from other mesh builder."""
        # rebuild from scratch to crate a valid ledger
        return cls.from_mesh(other)  # type: ignore


class MeshAverageVertexMerger(MeshBuilder):
    """Subclass of :class:`MeshBuilder`

    Mesh with unique vertices and no doublets, but needs extra memory for
    bookkeeping and runtime for calculation of average vertex location.

    :class:`MeshAverageVertexMerger` creates a key for every vertex by rounding
    its components by the Python :func:`round` function and a given `precision`
    value. Each vertex with the same key gets the same vertex index, which is the
    index of first vertex with this key, the difference to the
    :class:`MeshVertexMerger` class is the calculation of the average location
    for all vertices with the same key, this needs extra memory to keep track of
    the count of vertices for each key and extra runtime for updating the vertex
    location each time a vertex with an existing key is added.

    Args:
        precision: floating point precision for vertex rounding

    """

    # can not support vertex transformation
    def __init__(self, precision: int = 6):
        super().__init__()
        self.ledger: Dict[
            Vec3, Tuple[int, int]
        ] = {}  # each key points to a tuple (vertex index, vertex count)
        self.precision: int = precision

    def add_vertices(self, vertices: Iterable["Vertex"]) -> Sequence[int]:
        """Add new `vertices` only, if no vertex with identical ``(x, y, z)``
        coordinates already exist, else the index of the existing vertex is
        returned as index of the added vertices.

        Args:
            vertices: list of vertices, vertex as ``(x, y, z)`` tuple or
            :class:`~ezdxf.math.Vec3` objects

        Returns:
            tuple: indices of the `vertices` added to the
            :attr:`~MeshBuilder.vertices` list

        """
        indices = []
        precision = self.precision
        for vertex in vertices:
            vertex = Vec3(vertex)
            key = vertex.round(precision)  # type: ignore
            try:
                index, count = self.ledger[key]
            except KeyError:  # new key
                index = len(self.vertices)
                self.vertices.append(vertex)
                self.ledger[key] = (index, 1)
            else:  # update key entry
                # calculate new average location
                average = (self.vertices[index] * count) + vertex
                count += 1
                # update vertex location
                self.vertices[index] = average / count
                # update ledger
                self.ledger[key] = (index, count)
            indices.append(index)
        return tuple(indices)

    def index(self, vertex: "Vertex") -> int:
        """Get index of `vertex`, raise :class:`KeyError` if not found.

        Args:
            vertex: ``(x, y, z)`` tuple or :class:`~ezdxf.math.Vec3` object

        (internal API)
        """
        try:
            return self.ledger[Vec3(vertex).round(self.precision)][0]
        except KeyError:
            raise IndexError(f"Vertex {str(vertex)} not found.")

    @classmethod
    def from_builder(cls: Type[T], other: "MeshBuilder") -> T:
        """Create new mesh from other mesh builder."""
        # rebuild from scratch to crate a valid ledger
        return cls.from_mesh(other)  # type: ignore
