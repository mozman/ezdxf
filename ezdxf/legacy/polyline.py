# Created: 25.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, List, cast, Sequence, Union
from ezdxf.lldxf.const import DXFValueError, DXFIndexError
from ezdxf.lldxf import const

from .graphics import GraphicEntity, ExtendedTags, make_attribs, DXFAttr, XType
from .facemixins import PolyfaceMixin, PolymeshMixin
from .trace import QuadrilateralMixin

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex, TagValue, Vertex

_POLYLINE_TPL = """0
POLYLINE
5
0
8
0
66
1
70
0
10
0.0
20
0.0
30
0.0
"""


class Polyline(GraphicEntity):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_POLYLINE_TPL)
    DXFATTRIBS = make_attribs({
        'elevation': DXFAttr(10, xtype=XType.any_point),
        'flags': DXFAttr(70, default=0),
        'default_start_width': DXFAttr(40, default=0.0),
        'default_end_width': DXFAttr(41, default=0.0),
        'm_count': DXFAttr(71, default=0),
        'n_count': DXFAttr(72, default=0),
        'm_smooth_density': DXFAttr(73, default=0),
        'n_smooth_density': DXFAttr(74, default=0),
        'smooth_type': DXFAttr(75, default=0),
    })
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

    def post_new_hook(self) -> None:
        seqend = self._new_entity('SEQEND', {})
        self.tags.link = seqend.dxf.handle

    def set_dxf_attrib(self, key: str, value: 'TagValue') -> None:
        super(Polyline, self).set_dxf_attrib(key, value)
        if key == 'layer':  # if layer of POLYLINE changed, also change layer of VERTEX entities
            self._set_vertices_layer(value)

    def _set_vertices_layer(self, layer_name: str) -> None:
        for vertex in self.vertices():
            vertex.dxf.layer = layer_name

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
        count = 0
        db = self.entitydb
        tags = db[self.tags.link]
        while tags.link is not None:
            count += 1
            tags = db[tags.link]
        return count

    def __getitem__(self, pos) -> 'DXFVertex':
        count = 0
        db = self.entitydb
        tags = db[self.tags.link]
        while tags.link is not None:
            if count == pos:
                return self.dxffactory.wrap_entity(tags)  # type: ignore
            count += 1
            tags = db[tags.link]
        raise DXFIndexError("vertex index out of range")

    def vertices(self) -> Iterable['DXFVertex']:
        return (entity for entity in self.linked_entities() if entity.dxftype() == 'VERTEX')  # type: ignore

    def points(self) -> Iterable['Vertex']:
        return (vertex.dxf.location for vertex in self.vertices())

    def append_vertices(self, points: Sequence['Vertex'], dxfattribs: dict = None) -> None:
        dxfattribs = dxfattribs or {}
        if len(points) > 0:
            last_vertex = self._get_last_vertex()
            for new_vertex in self._points_to_dxf_vertices(points, dxfattribs):
                self._insert_after(last_vertex, new_vertex)
                last_vertex = new_vertex

    @staticmethod
    def _insert_after(prev_vertex: 'DXFVertex', new_vertex: 'DXFVertex') -> None:
        succ = prev_vertex.tags.link
        prev_vertex.tags.link = new_vertex.dxf.handle
        new_vertex.tags.link = succ

    def _get_last_vertex(self) -> 'DXFVertex':
        db = self.entitydb
        tags = self.tags
        handle = self.dxf.handle
        while tags.link is not None:  # while not SEQEND
            prev_handle = handle
            handle = tags.link
            tags = db[handle]
        return self.dxffactory.wrap_handle(prev_handle)  # type: DXFVertex

    def insert_vertices(self, pos: int, points: Iterable['Vertex'], dxfattribs: dict = None) -> None:
        """ Insert *points* at position *pos*.

        :param pos: insertion position
        :param points: list of (x, y, z)-tuples
        :param dxfattribs: dict of DXF attributes

        """
        dxfattribs = dxfattribs or {}
        if pos > 0:
            insert_vertex = self.__getitem__(pos - 1)
        else:
            insert_vertex = self
        for new_vertex in self._points_to_dxf_vertices(points, dxfattribs):
            self._insert_after(insert_vertex, new_vertex)
            insert_vertex = new_vertex

    def _append_vertices(self, vertices: Iterable['DXFVertex']) -> None:
        """ Append DXFVertex objects.

        :param vertices: iterable of DXFVertex objects
        """
        last_vertex = self._get_last_vertex()
        for vertex in vertices:
            self._insert_after(last_vertex, vertex)
            last_vertex = vertex

    def _points_to_dxf_vertices(self, points: Iterable['Vertex'], dxfattribs: dict) -> List['DXFVertex']:
        """ Converts point (x,y, z)-tuples into DXFVertex objects.

        :param points: list of (x, y,z)-tuples
        :param dxfattribs: dict of DXF attributes
        """
        dxfattribs['flags'] = dxfattribs.get('flags', 0) | self.get_vertex_flags()
        dxfattribs['layer'] = self.get_dxf_attrib('layer', '0')  # all vertices on the same layer as the POLYLINE entity
        vertices = []  # type: List[DXFVertex]
        for point in points:
            dxfattribs['location'] = point
            vertices.append(cast('DXFVertex', self._new_entity('VERTEX', dxfattribs)))
        return vertices

    def delete_vertices(self, pos: int, count=1) -> None:
        db = self.entitydb
        prev_vertex = self.__getitem__(pos - 1).tags if pos > 0 else self.tags
        vertex = db[prev_vertex.link]
        while vertex.dxftype() == 'VERTEX':
            db.delete_handle(prev_vertex.link)  # remove from database
            prev_vertex.link = vertex.link  # remove vertex from list
            count -= 1
            if count == 0:
                return
            vertex = db[prev_vertex.link]
        raise DXFValueError("invalid count")

    def _unlink_all_vertices(self) -> None:
        # but don't delete it from database
        last_vertex = self._get_last_vertex()
        self.tags.link = last_vertex.tags.link  # link POLYLINE -> SEQEND

    def cast(self) -> Union['Polyline', 'Polymesh', 'Polyface']:
        mode = self.get_mode()
        if mode == 'AcDbPolyFaceMesh':
            return Polyface.convert(self)
        elif mode == 'AcDbPolygonMesh':
            return Polymesh.convert(self)
        else:
            return self

    def destroy(self) -> None:
        db = self.entitydb
        handle = self.tags.link
        while handle is not None:
            tags = db[handle]
            db.delete_handle(handle)
            handle = tags.link
        self.tags.link = None


class Polyface(Polyline, PolyfaceMixin):
    @staticmethod
    def convert(polyline: Polyline) -> 'Polyface':
        return Polyface(polyline.tags, polyline.drawing)


class Polymesh(Polyline, PolymeshMixin):
    @staticmethod
    def convert(polyline: Polyline) -> 'Polymesh':
        return Polymesh(polyline.tags, polyline.drawing)


_VERTEX_TPL = """0
VERTEX
5
0
8
0
10
0.0
20
0.0
30
0.0
40
0.0
41
0.0
42
0.0
70
0
"""


class DXFVertex(GraphicEntity, QuadrilateralMixin):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_VERTEX_TPL)
    DXFATTRIBS = make_attribs({
        'location': DXFAttr(10, xtype=XType.any_point),
        'start_width': DXFAttr(40, default=0.0),
        'end_width': DXFAttr(41, default=0.0),
        'bulge': DXFAttr(42, default=0),
        'flags': DXFAttr(70, default=0),
        'tangent': DXFAttr(50),
        'vtx0': DXFAttr(71),
        'vtx1': DXFAttr(72),
        'vtx2': DXFAttr(73),
        'vtx3': DXFAttr(74),
    })
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
