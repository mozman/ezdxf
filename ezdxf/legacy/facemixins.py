# Created: 2011-04-30
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from typing import Tuple, TYPE_CHECKING, Iterable, Dict, Sequence, List, cast
from itertools import chain

from ezdxf.lldxf import const

from .polyfacebuilder import PolyfaceBuilder

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex, FaceType, DXFVertex, Polyline


class PolymeshMixin:
    __slots__ = ()

    def set_mesh_vertex(self, pos: Tuple[int, int], point: 'Vertex', dxfattribs: dict = None):
        """
        Set location and DXF attributes of a single mesh vertex.

        Args:
            pos: 0-based (row, col)-tuple, position of mesh vertex
            point: (x, y, z)-tuple, new 3D coordinates of the mesh vertex
            dxfattribs: dict of DXF attributes

        """
        dxfattribs = dxfattribs or {}
        dxfattribs['location'] = point
        vertex = self.get_mesh_vertex(pos)
        vertex.update_dxf_attribs(dxfattribs)

    def get_mesh_vertex(self, pos: Tuple[int, int]) -> 'DXFVertex':
        """
        Get location of a single mesh vertex.

        Args:
            pos: 0-based (row, col)-tuple, position of mesh vertex

        """
        polyline = cast('Polyline', self)
        m_count = polyline.dxf.m_count
        n_count = polyline.dxf.n_count
        m, n = pos
        if 0 <= m < m_count and 0 <= n < n_count:
            pos = m * n_count + n
            return polyline.__getitem__(pos)
        else:
            raise const.DXFIndexError(repr(pos))

    def get_mesh_vertex_cache(self) -> 'MeshVertexCache':
        """
        Get a MeshVertexCache() object for this Polymesh. The caching object provides fast access to the location
        attributes of the mesh vertices.

        """
        return MeshVertexCache(cast('Polyline', self))


class MeshVertexCache:
    __slots__ = ('vertices',)
    """
    Cache mesh vertices in a dict, keys are 0-based (row, col)-tuples.

    vertices:
       Dict of mesh vertices, keys are 0-based (row, col)-tuples. Writing to this dict doesn't change the DXF entity.

    """

    def __init__(self, mesh: 'Polyline'):
        self.vertices = self._setup(mesh, mesh.dxf.m_count, mesh.dxf.n_count)  # type: Dict[Tuple[int, int], DXFVertex]

    def _setup(self, mesh: 'Polyline', m_count: int, n_count: int) -> dict:
        cache = {}  # type: Dict[Tuple[int, int], DXFVertex]
        vertices = iter(mesh.vertices())
        for m in range(m_count):
            for n in range(n_count):
                cache[(m, n)] = next(vertices)
        return cache

    def __getitem__(self, pos: Tuple[int, int]) -> 'Vertex':
        """
        Get mesh vertex location as (x, y, z)-tuple.
        """
        try:
            return self.vertices[pos].dxf.location
        except KeyError:
            raise const.DXFIndexError(repr(pos))

    def __setitem__(self, pos: Tuple[int, int], location: 'Vertex') -> None:
        """
        Get mesh vertex location as (x, y, z)-tuple.
        """
        try:
            self.vertices[pos].dxf.location = location
        except KeyError:
            raise const.DXFIndexError(repr(pos))


class PolyfaceMixin:
    __slots__ = ()
    """
    Order of mesh_vertices and face_records is important (DXF R2010):

        1. mesh_vertices: the polyface mesh vertex locations
        2. face_records: indices of the face forming vertices

    """

    def append_face(self, face: 'FaceType', dxfattribs: dict = None) -> None:
        """
        Appends a single face. Appending single faces is very inefficient, try collecting single faces and use
        Polyface.append_faces().

        Args:
            face: list of (x, y, z)-tuples
            dxfattribs: dict of DXF attributes

        """
        self.append_faces([face], dxfattribs)

    def append_faces(self, faces: Iterable['FaceType'], dxfattribs: dict = None) -> None:
        """
        Append multiple *faces*. *faces* is a list of single faces and a single face is a list of (x, y, z)-tuples.

        Args:
            faces: list of (list of (x, y, z)-tuples)
            dxfattribs: dict of DXF attributes

        """

        def new_face_record() -> 'DXFVertex':
            dxfattribs['flags'] = const.VTX_3D_POLYFACE_MESH_VERTEX
            return self._new_entity('VERTEX', dxfattribs)

        dxfattribs = dxfattribs or {}

        existing_vertices, existing_faces = self.indexed_faces()
        # existing_faces is a generator, can't append new data
        new_faces = []  # type: List[FaceProxy]
        for face in faces:
            # convert face point coordinates to DXF Vertex() objects.
            face_mesh_vertices = cast('Polyline', self)._points_to_dxf_vertices(face, {})  # type: List[DXFVertex]
            # index of first new vertex
            index = len(existing_vertices)
            existing_vertices.extend(face_mesh_vertices)
            # create a new face_record with all indices set to 0
            face_record = FaceProxy(new_face_record(), existing_vertices)
            # set correct indices
            face_record.indices = tuple(range(index, index + len(face_mesh_vertices)))
            new_faces.append(face_record)
        self._rebuild(chain(existing_faces, new_faces))

    def _rebuild(self, faces: Iterable['FaceProxy'], precision: int = 6) -> None:
        """
        Build a valid Polyface structure out of *faces*.

        Args:
            faces: iterable of FaceProxy objects.

        """
        polyface_builder = PolyfaceBuilder(faces, precision=precision)
        polyline = cast('Polyline', self)
        polyline._unlink_all_vertices()  # but don't remove it from database
        polyline._append_vertices(polyface_builder.get_vertices())
        self.update_count(polyface_builder.nvertices, polyface_builder.nfaces)

    def update_count(self, nvertices: int, nfaces: int) -> None:
        polyline = cast('Polyline', self)
        polyline.dxf.m_count = nvertices
        polyline.dxf.n_count = nfaces

    def optimize(self, precision: int = 6) -> None:
        """
        Rebuilds polyface with vertex optimization. Merges vertices with nearly same vertex locations.
        Polyfaces created by *ezdxf* are optimized automatically.

        Args:
            precision: decimal precision for determining identical vertex locations

        """
        vertices, faces = self.indexed_faces()
        self._rebuild(faces, precision)

    def faces(self) -> Iterable['DXFVertex']:
        """
        Iterate over all faces, a face is a tuple of vertices.
        result is a list: vertex, vertex, vertex, [vertex,] face_record

        """
        _, faces = self.indexed_faces()  # just need the faces generator
        for face in faces:
            face_vertices = list(face)
            face_vertices.append(face.face_record)
            yield face_vertices

    def indexed_faces(self) -> Tuple[List['DXFVertex'], Iterable['FaceProxy']]:
        """
        Returns a list of all vertices and a generator of FaceProxy() objects.

        """
        polyline = cast('Polyline', self)
        vertices = []
        face_records = []
        for vertex in polyline.vertices():  # type: DXFVertex
            (vertices if vertex.is_poly_face_mesh_vertex else face_records).append(vertex)

        faces = (FaceProxy(face_record, vertices) for face_record in face_records)
        return vertices, faces


class FaceProxy:
    __slots__ = ('vertices', 'face_record', 'indices')
    """
    Represents a single face of a polyface structure.

    vertices:

        List of all polyface vertices.

    face_record:

        The face forming vertex of type ``AcDbFaceRecord``, contains the indices to the face building vertices. Indices
        of the DXF structure are 1-based and a negative index indicates the beginning of an invisible edge.
        Face.face_record.dxf.color determines the color of the face.

    indices:

        Indices to the face building vertices as tuple. This indices are 0-base and are used to get vertices from the
        list *Face.vertices*.

    """

    def __init__(self, face_record: 'DXFVertex', vertices: Sequence['DXFVertex']):
        self.vertices = vertices  # type: Sequence[DXFVertex]
        self.face_record = face_record  # type: DXFVertex
        self.indices = self._indices()  # type: Sequence[int]

    def __len__(self) -> int:
        return len(self.indices)

    def __getitem__(self, pos: int) -> 'DXFVertex':
        return self.vertices[self.indices[pos]]

    def __iter__(self) -> Iterable['DXFVertex']:
        return (self.vertices[index] for index in self.indices)

    def points(self) -> Iterable['Vertex']:
        return (vertex.dxf.location for vertex in self)

    def _raw_indices(self) -> Iterable[int]:
        return (self.face_record.get_dxf_attrib(name, 0) for name in const.VERTEXNAMES)

    def _indices(self) -> Sequence[int]:
        return tuple(abs(index) - 1 for index in self._raw_indices() if index != 0)

    def is_edge_visible(self, pos: int) -> bool:
        name = const.VERTEXNAMES[pos]
        return self.face_record.get_dxf_attrib(name) > 0
