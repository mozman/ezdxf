# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-16
from typing import TYPE_CHECKING, Iterable, Union, List, cast, Tuple, Sequence, Dict
from itertools import chain
from ezdxf.math import Vector
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER, VERTEXNAMES
from ezdxf.lldxf import const
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity, SeqEnd
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, Vertex, FaceType, DXFNamespace, DXFEntity, Drawing

__all__ = ['Polyline', 'Polyface']

acdb_polyline = DefSubclass('AcDbPolylineDummy', {  # AcDbPolylineDummy is a temp solution while importing
    # 66: obsolete - not read and not written, because POLYLINE without vertices makes no sense
    # a “dummy” point; the X and Y values are always 0, and the Z value is the polyline's elevation
    # (in OCS when 2D, WCS when 3D) x, y ALWAYS 0
    'elevation': DXFAttr(10, xtype=XType.point3d),
    # Polyline flag (bit-coded):
    'flags': DXFAttr(70, default=0),
    # 1 = This is a closed polyline (or a polygon mesh closed in the M direction)
    # 2 = Curve-fit vertices have been added
    # 4 = Spline-fit vertices have been added
    # 8 = This is a 3D polyline
    # 16 = This is a 3D polygon mesh
    # 32 = The polygon mesh is closed in the N direction
    # 64 = The polyline is a polyface mesh
    # 128 = The linetype pattern is generated continuously around the vertices of this polyline
    'default_start_width': DXFAttr(40, default=0, optional=True),
    'default_end_width': DXFAttr(41, default=0, optional=True),
    'm_count': DXFAttr(71, default=0, optional=True),
    'n_count': DXFAttr(72, default=0, optional=True),
    'm_smooth_density': DXFAttr(73, default=0, optional=True),
    'n_smooth_density': DXFAttr(74, default=0, optional=True),
    # Curves and smooth surface type; integer codes, not bit-coded:
    'smooth_type': DXFAttr(75, default=0, optional=True),
    # 0 = No smooth surface fitted
    # 5 = Quadratic B-spline surface
    # 6 = Cubic B-spline surface
    # 8 = Bezier surface
    'thickness': DXFAttr(39, default=0, optional=True),
    'extrusion': DXFAttr(210, xtype=XType.point3d, default=Vector(0, 0, 1), optional=True),
})


@register_entity
class Polyline(DXFGraphic):
    """ DXF POLYLINE entity """
    DXFTYPE = 'POLYLINE'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_polyline)
    # polyline flags (70)
    CLOSED = 1
    MESH_CLOSED_M_DIRECTION = CLOSED
    CURVE_FIT_VERTICES_ADDED = 2
    SPLINE_FIT_VERTICES_ADDED = 4
    POLYLINE_3D = 8
    POLYMESH = 16
    MESH_CLOSED_N_DIRECTION = 32
    POLYFACE = 64
    GENERATE_LINETYPE_PATTERN = 128
    # polymesh smooth type (75)
    NO_SMOOTH = 0
    QUADRATIC_BSPLINE = 5
    CUBIC_BSPLINE = 6
    BEZIER_SURFACE = 8
    ANY3D = POLYLINE_3D | POLYMESH | POLYFACE

    def __init__(self, doc: 'Drawing' = None):
        super().__init__(doc)
        self.vertices = []  # type: List[DXFVertex]
        self.seqend = None  # type: SeqEnd

    def linked_entities(self) -> Iterable['DXFVertex']:
        # dont't yield seqend here, because it is not a DXFGraphic entity
        return self.vertices

    def link_entity(self, entity: 'DXFEntity') -> None:
        assert isinstance(entity, DXFVertex)
        entity.set_owner(self.dxf.owner, self.dxf.paperspace)
        self.vertices.append(entity)

    def link_seqend(self, seqend: 'DXFEntity') -> None:
        seqend.dxf.owner = self.dxf.owner
        self.seqend = seqend

    def _copy_data(self, entity: 'Polyline') -> None:
        """ Copy vertices and store the copies into the entity database. """
        entity.vertices = [vertex.copy() for vertex in self.vertices]
        entity.seqend = self.seqend.copy()

    def set_owner(self, owner: str, paperspace: int = 0):
        # At loading form file, POLYLINE will be added to layout before vertices are linked, so set_owner() of POLYLINE
        # does not set owner of vertices
        super().set_owner(owner, paperspace)
        # vertices handled by super class by linked_entities() interface
        if self.seqend:  # has no paperspace flag
            self.seqend.dxf.owner = owner

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        """
        Adds subclass processing for 'AcDbLine', requires previous base class and 'AcDbEntity' processing by parent
        class.
        """
        dxf = super().load_dxf_attribs(processor)
        if processor is None:
            return dxf
        if processor.r12:
            processor.load_dxfattribs_into_namespace(dxf, acdb_polyline, index=0)
        else:
            tags = processor.load_dxfattribs_into_namespace(dxf, acdb_polyline, index=2)
            name = processor.subclasses[2][0].value
            if len(tags):
                # do not log:
                # 66: attribs follow, not required
                processor.log_unprocessed_tags(tags.filter((66, )), subclass=name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, self.get_mode())

        tagwriter.write_tag2(66, 1)  # entities follow, required for R12? (sure not for R2000+)
        # for all DXF versions
        self.dxf.export_dxf_attribs(tagwriter, [
            'elevation',
            'flags',
            'default_start_width',
            'default_end_width',
            'm_count',
            'n_count',
            'm_smooth_density',
            'n_smooth_density',
            'smooth_type',
            'thickness',
            'extrusion',
        ])
        # xdata and embedded objects export will be done by parent class
        # following VERTEX entities and SEQEND is exported by EntitySpace()

    def export_seqend(self, tagwriter: 'TagWriter'):
        self.seqend.dxf.layer = self.dxf.layer
        self.seqend.export_dxf(tagwriter)

    def destroy(self) -> None:
        """
        Delete all data and references.

        """
        for v in self.vertices:
            self.entitydb.delete_entity(v)
        del self.vertices
        self.entitydb.delete_entity(self.seqend)
        super().destroy()

    def on_layer_change(self, layer: str):
        """
        Event handler for layer change. Changes also the layer of all vertices.

        Args:
            layer: new layer as string

        """
        for v in self.vertices:
            v.dxf.layer = layer

    def get_vertex_flags(self) -> int:
        return const.VERTEX_FLAGS[self.get_mode()]

    def get_mode(self) -> str:
        if self.is_3d_polyline:
            return 'AcDb3dPolyline'
        elif self.is_polygon_mesh:
            return 'AcDbPolygonMesh'
        elif self.is_poly_face_mesh:
            return 'AcDbPolyFaceMesh'
        else:
            return 'AcDb2dPolyline'

    @property
    def is_2d_polyline(self) -> bool:
        return self.dxf.flags & self.ANY3D == 0

    @property
    def is_3d_polyline(self) -> bool:
        return bool(self.dxf.flags & self.POLYLINE_3D)

    @property
    def is_polygon_mesh(self) -> bool:
        return bool(self.dxf.flags & self.POLYMESH)

    @property
    def is_poly_face_mesh(self) -> bool:
        return bool(self.dxf.flags & self.POLYFACE)

    @property
    def is_closed(self) -> bool:
        return bool(self.dxf.flags & self.CLOSED)

    @property
    def is_m_closed(self) -> bool:
        return bool(self.dxf.flags & self.MESH_CLOSED_M_DIRECTION)

    @property
    def is_n_closed(self) -> bool:
        return bool(self.dxf.flags & self.MESH_CLOSED_N_DIRECTION)

    def m_close(self) -> None:
        self.dxf.flags = self.dxf.flags | self.MESH_CLOSED_M_DIRECTION

    def n_close(self) -> None:
        self.dxf.flags = self.dxf.flags | self.MESH_CLOSED_N_DIRECTION

    def close(self, m_close, n_close=False) -> None:
        if m_close:
            self.m_close()
        if n_close:
            self.n_close()

    def __len__(self) -> int:
        return len(self.vertices)

    def __getitem__(self, pos) -> 'DXFVertex':
        return self.vertices[pos]

    def points(self) -> Iterable[Vector]:
        return (vertex.dxf.location for vertex in self.vertices)

    def extend(self, points: Iterable['Vertex'], dxfattribs: dict = None) -> None:
        dxfattribs = dxfattribs or {}
        self.vertices.extend(self._build_dxf_vertices(points, dxfattribs))

    append_vertices = extend

    def insert_vertices(self, pos: int, points: Iterable['Vertex'], dxfattribs: dict = None) -> None:
        """ Insert `points` at position `pos``.
        Args:
            pos: insertion position
            points: list of (x, y, z)-tuples
            dxfattribs: dict of DXF attributes

        """
        dxfattribs = dxfattribs or {}
        self.vertices[pos:pos] = list(self._build_dxf_vertices(points, dxfattribs))

    def _build_dxf_vertices(self, points: Iterable['Vertex'], dxfattribs: dict) -> List['DXFVertex']:
        """ Converts point (x, y, z)-tuples into DXFVertex objects.

        Args:
            points: list of (x, y,z)-tuples
            dxfattribs: dict of DXF attributes
        """
        dxfattribs['flags'] = dxfattribs.get('flags', 0) | self.get_vertex_flags()
        dxfattribs['layer'] = self.dxf.layer
        create_vertex = self.doc.dxffactory.create_db_entry
        for point in points:
            dxfattribs['location'] = point
            yield create_vertex('VERTEX', dxfattribs)

    def cast(self) -> Union['Polyline', 'Polymesh', 'Polyface']:
        mode = self.get_mode()
        if mode == 'AcDbPolyFaceMesh':
            return Polyface.from_polyline(self)
        elif mode == 'AcDbPolygonMesh':
            return Polymesh.from_polyline(self)
        else:
            return self


class Polyface(Polyline):
    pass
    """
    PolyFace structure:

    POLYLINE
      AcDbEntity
      AcDbPolyFaceMesh
    VERTEX - Vertex
      AcDbEntity
      AcDbVertex
      AcDbPolyFaceMeshVertex
    VERTEX - Face
      AcDbEntity
      AcDbFaceRecord
    SEQEND

    Order of mesh_vertices and face_records is important (DXF R2010):

        1. mesh_vertices: the polyface mesh vertex locations
        2. face_records: indices of the face forming vertices

    """

    @classmethod
    def from_polyline(cls, polyline: Polyline) -> 'Polyface':
        polyface = cls.shallow_copy(polyline)
        polyface.vertices = polyline.vertices
        polyface.seqend = polyline.seqend
        # do not destroy polyline - all data would be lost
        return polyface

    def append_face(self, face: 'FaceType', dxfattribs: dict = None) -> None:
        """
        Appends a single face. Appending single faces is very inefficient, try collecting single faces and use
        Polyface.append_faces().

        Args:
            face: list of (x, y, z)-tuples
            dxfattribs: dict of DXF attributes

        """
        self.append_faces([face], dxfattribs)

    def _points_to_dxf_vertices(self, points: Iterable['Vertex'], dxfattribs: dict) -> List['DXFVertex']:
        """ Converts point (x,y, z)-tuples into DXFVertex objects.

        Args:
            points: list of (x, y,z)-tuples
            dxfattribs: dict of DXF attributes

        """
        dxfattribs['flags'] = dxfattribs.get('flags', 0) | self.get_vertex_flags()
        dxfattribs['layer'] = self.get_dxf_attrib('layer', '0')  # all vertices on the same layer as the POLYLINE entity
        vertices = []  # type: List[DXFVertex]
        for point in points:
            dxfattribs['location'] = point
            vertices.append(cast('DXFVertex', self._new_compound_entity('VERTEX', dxfattribs)))
        return vertices

    def append_faces(self, faces: Iterable['FaceType'], dxfattribs: dict = None) -> None:
        """
        Append multiple *faces*. *faces* is a list of single faces and a single face is a list of (x, y, z)-tuples.

        Args:
            faces: list of (list of (x, y, z)-tuples)
            dxfattribs: dict of DXF attributes

        """

        def new_face_record() -> 'DXFVertex':
            dxfattribs['flags'] = const.VTX_3D_POLYFACE_MESH_VERTEX
            # location of face record vertex is always (0, 0, 0)
            dxfattribs['location'] = Vector()
            return self._new_compound_entity('VERTEX', dxfattribs)

        dxfattribs = dxfattribs or {}

        existing_vertices, existing_faces = self.indexed_faces()
        # existing_faces is a generator, can't append new data
        new_faces = []  # type: List[FaceProxy]
        for face in faces:
            # convert face point coordinates to DXF Vertex() objects.
            face_mesh_vertices = self._points_to_dxf_vertices(face, {})  # type: List[DXFVertex]
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
        self.vertices = []
        # polyline._unlink_all_vertices()  # but don't remove it from database
        self.vertices = polyface_builder.get_vertices()
        self.update_count(polyface_builder.nvertices, polyface_builder.nfaces)

    def update_count(self, nvertices: int, nfaces: int) -> None:
        self.dxf.m_count = nvertices
        self.dxf.n_count = nfaces

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
        vertices = []
        face_records = []
        for vertex in self.vertices:  # type: DXFVertex
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


class PolyfaceBuilder:
    def __init__(self, faces: Iterable['FaceProxy'], precision: int = 6):
        self.precision = precision
        self.faces = []
        self.vertices = []
        self.index_mapping = {}
        self.build(faces)

    @property
    def nvertices(self) -> int:
        return len(self.vertices)

    @property
    def nfaces(self) -> int:
        return len(self.faces)

    def get_vertices(self) -> List['DXFVertex']:
        vertices = self.vertices[:]
        vertices.extend(self.faces)
        return vertices

    def build(self, faces: Iterable['FaceProxy']) -> None:
        for face in faces:
            face_record = face.face_record
            for vertex, name in zip(face, VERTEXNAMES):
                index = self.add(vertex)
                # preserve sign of old index value
                sign = -1 if face_record.dxf.get(name, 0) < 0 else +1
                face_record.dxf.set(name, (index + 1) * sign)
            self.faces.append(face_record)

    def add(self, vertex: 'DXFVertex') -> int:
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


class Polymesh(Polyline):
    """
    PolyMesh structure:

    POLYLINE
      AcDbEntity
      AcDbPolygonMesh
    VERTEX
      AcDbEntity
      AcDbVertex
      AcDbPolygonMeshVertex
    """

    @classmethod
    def from_polyline(cls, polyline: Polyline) -> 'Polymesh':
        polymesh = cls.shallow_copy(polyline)
        polymesh.vertices = polyline.vertices
        polymesh.seqend = polyline.seqend
        # do not destroy polyline - all data would be lost
        return polymesh

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
        m_count = self.dxf.m_count
        n_count = self.dxf.n_count
        m, n = pos
        if 0 <= m < m_count and 0 <= n < n_count:
            pos = m * n_count + n
            return self.vertices[pos]
        else:
            raise const.DXFIndexError(repr(pos))

    def get_mesh_vertex_cache(self) -> 'MeshVertexCache':
        """
        Get a MeshVertexCache() object for this Polymesh. The caching object provides fast access to the location
        attributes of the mesh vertices.

        """
        return MeshVertexCache(self)


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
        vertices = iter(mesh.vertices)
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


acdb_vertex = DefSubclass('AcDbVertex', {  # last subclass index -1
    'location': DXFAttr(10, xtype=XType.point3d),  # Location point (in OCS when 2D, and WCS when 3D)
    'start_width': DXFAttr(40, default=0, optional=True),  # Starting width
    'end_width': DXFAttr(41, default=0, optional=True),  # Ending width
    # Bulge (optional; default is 0). The bulge is the tangent of one fourth the included angle for an arc segment, made
    # negative if the arc goes clockwise from the start point to the endpoint. A bulge of 0 indicates a straight
    # segment, and a bulge of 1 is a semicircle.
    'bulge': DXFAttr(42, default=0, optional=True),
    'flags': DXFAttr(70, default=0),
    'tangent': DXFAttr(50, optional=True),  # Curve fit tangent direction (in degrees?)
    'vtx0': DXFAttr(71, optional=True),
    'vtx1': DXFAttr(72, optional=True),
    'vtx2': DXFAttr(73, optional=True),
    'vtx3': DXFAttr(74, optional=True),
    'vertex_identifier': DXFAttr(91, optional=True),
})


@register_entity
class DXFVertex(DXFGraphic):
    """ DXF VERTEXE entity """
    DXFTYPE = 'VERTEX'

    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_vertex)
    EXTRA_VERTEX_CREATED = 1  # Extra vertex created by curve-fitting
    CURVE_FIT_TANGENT = 2  # Curve-fit tangent defined for this vertex.
    # A curve-fit tangent direction of 0 may be omitted from the DXF output, but is
    # significant if this bit is set.
    # 4 = unused, never set in dxf files
    SPLINE_VERTEX_CREATED = 8  # Spline vertex created by spline-fitting
    SPLINE_FRAME_CONTROL_POINT = 16
    POLYLINE_3D_VERTEX = 32
    POLYGON_MESH_VERTEX = 64
    POLYFACE_MESH_VERTEX = 128
    FACE_FLAGS = POLYGON_MESH_VERTEX + POLYFACE_MESH_VERTEX
    VTX3D = POLYLINE_3D_VERTEX + POLYGON_MESH_VERTEX + POLYFACE_MESH_VERTEX

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor is None:
            return dxf
        # VERTEX can have 3 subclasses if face record or 4 subclasses if vertex
        # just last one has data
        tags = processor.load_dxfattribs_into_namespace(dxf, acdb_vertex, index=-1)
        if len(tags) and not processor.r12:
            processor.log_unprocessed_tags(tags, subclass=acdb_polyline.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        if tagwriter.dxfversion > DXF12:
            if self.is_face_record:  # (flags & Vertex.FACE_FLAGS) == const.VTX_3D_POLYFACE_MESH_VERTEX:
                tagwriter.write_tag2(SUBCLASS_MARKER, 'AcDbFaceRecord')
            else:
                tagwriter.write_tag2(SUBCLASS_MARKER, 'AcDbVertex')
                if self.is_3d_polyline_vertex:  # flags & const.VTX_3D_POLYLINE_VERTEX
                    tagwriter.write_tag2(SUBCLASS_MARKER, 'AcDb3dPolylineVertex')
                elif self.is_poly_face_mesh_vertex:  # flags & Vertex.FACE_FLAGS == Vertex.FACE_FLAGS:
                    tagwriter.write_tag2(SUBCLASS_MARKER, 'AcDbPolyFaceMeshVertex')
                elif self.is_polygon_mesh_vertex:  # flags & const.VTX_3D_POLYGON_MESH_VERTEX
                    tagwriter.write_tag2(SUBCLASS_MARKER, 'AcDbPolygonMeshVertex')
                else:
                    tagwriter.write_tag2(SUBCLASS_MARKER, 'AcDb2dVertex')

        # for all DXF versions
        self.dxf.export_dxf_attribs(tagwriter, [
            'location', 'start_width', 'end_width', 'bulge', 'flags', 'tangent', 'vtx0', 'vtx1', 'vtx2', 'vtx3',
            'vertex_identifier'
        ])
        # xdata and embedded objects export will be done by parent class
        # following VERTEX entities and SEQEND is exported by EntitySpace()

    @property
    def is_2d_polyline_vertex(self) -> bool:
        return self.dxf.flags & self.VTX3D == 0

    @property
    def is_3d_polyline_vertex(self) -> bool:
        return self.dxf.flags & self.POLYLINE_3D_VERTEX

    @property
    def is_polygon_mesh_vertex(self) -> bool:
        return self.dxf.flags & self.POLYGON_MESH_VERTEX

    @property
    def is_poly_face_mesh_vertex(self) -> bool:
        return self.dxf.flags & self.FACE_FLAGS == self.FACE_FLAGS

    @property
    def is_face_record(self) -> bool:
        return (self.dxf.flags & self.FACE_FLAGS) == self.POLYFACE_MESH_VERTEX
