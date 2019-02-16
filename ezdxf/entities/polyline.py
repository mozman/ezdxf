# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-02-16
from typing import TYPE_CHECKING, Iterable
from ezdxf.math import Vector
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter
    from .dxfentity import DXFNamespace, DXFEntity
    from ezdxf.drawing2 import Drawing

__all__ = ['Polyline']

acdb_polyline = DefSubclass('AcDbPolyline', {
    'elevation': DXFAttr(10, xtype=XType.point3d),
    'flags': DXFAttr(70, default=0),
    'default_start_width': DXFAttr(40, default=0.0),
    'default_end_width': DXFAttr(41, default=0.0),
    'm_count': DXFAttr(71, default=0),
    'n_count': DXFAttr(72, default=0),
    'm_smooth_density': DXFAttr(73, default=0),
    'n_smooth_density': DXFAttr(74, default=0),
    'smooth_type': DXFAttr(75, default=0),
    'thickness': DXFAttr(39, default=0.0),
    'extrusion': DXFAttr(210, xtype=XType.point3d, default=Vector(0.0, 0.0, 1.0)),
})


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
        self.vertices = []

    def linked_entities(self) -> Iterable['DXFEntity']:
        return self.vertices

    def link_entity(self, entity: 'DXFEntity') -> None:
        self.vertices.append(entity)

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        """
        Adds subclass processing for 'AcDbLine', requires previous base class and 'AcDbEntity' processing by parent
        class.
        """
        dxf = super().load_dxf_attribs(processor)
        if processor is None:
            return dxf
        processor.change_subclass_marker(2, 'AcDbPolyline')
        tags = processor.load_dxfattribs_into_namespace(dxf, acdb_polyline)
        if len(tags) and not processor.r12:
            processor.log_unprocessed_tags(tags, subclass=acdb_polyline.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, self.get_mode())
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
        # following SEQEND is exported by EntitySpace()

    def destroy(self) -> None:
        """
        Delete all data and references.

        """
        for v in self.vertices:
            v.destroy()
        del self.vertices
        super().destroy()

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
