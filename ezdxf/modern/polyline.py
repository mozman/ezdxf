# Created: 25.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from ezdxf.lldxf.types import DXFTag
from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf import loader
from ezdxf.legacy import polyline
from ezdxf.legacy.facemixins import PolyfaceMixin, PolymeshMixin

from .graphics import ExtendedTags, DXFAttr, DefSubclass, DXFAttributes
from .graphics import none_subclass, entity_subclass, ModernGraphicEntityExtension


_POLYLINE_TPL = """0
POLYLINE
5
0
330
0
100
AcDbEntity
8
0
100
AcDb2dPolyline
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

polyline_subclass = DefSubclass('AcDb2dPolyline', {
    'elevation': DXFAttr(10, xtype='Point3D'),
    'flags': DXFAttr(70, default=0),
    'default_start_width': DXFAttr(40, default=0.0),
    'default_end_width': DXFAttr(41, default=0.0),
    'm_count': DXFAttr(71, default=0),
    'n_count': DXFAttr(72, default=0),
    'm_smooth_density': DXFAttr(73, default=0),
    'n_smooth_density': DXFAttr(74, default=0),
    'smooth_type': DXFAttr(75, default=0),
    'thickness': DXFAttr(39, default=0.0),
    'extrusion': DXFAttr(210, xtype='Point3D', default=(0.0, 0.0, 1.0)),
})


class Polyline(polyline.Polyline, ModernGraphicEntityExtension):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_POLYLINE_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, polyline_subclass)

    def post_new_hook(self):
        super(Polyline, self).post_new_hook()
        self.update_subclass_specifier()

    def update_subclass_specifier(self):
        # For dxf attribute access not the name of the subclass is important, but
        # the order of the subclasses 1st, 2nd, 3rd and so on.
        # The 3rd subclass is the AcDb3dPolyline or AcDb2dPolyline subclass
        subclass = self.tags.subclasses[2]
        subclass[0] = DXFTag(100, self.get_mode())

    def cast(self):
        mode = self.get_mode()
        if mode == 'AcDbPolyFaceMesh':
            return Polyface.convert(self)
        elif mode == 'AcDbPolygonMesh':
            return Polymesh.convert(self)
        else:
            return self


class Polyface(Polyline, PolyfaceMixin):
    __slots__ = ()
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

    """
    @staticmethod
    def convert(polyline):
        return Polyface(polyline.tags, polyline.drawing)


class Polymesh(Polyline, PolymeshMixin):
    __slots__ = ()
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
    @staticmethod
    def convert(polyline):
        return Polymesh(polyline.tags, polyline.drawing)


_VERTEX_TPL = """0
VERTEX
5
0
330
0
100
AcDbEntity
8
0
100
AcDbVertex
100
AcDb2dVertex
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
vertex_subclass = (
    DefSubclass('AcDbVertex', {}),  # subclasses[2]
    DefSubclass('AcDb2dVertex', {  # subclasses[3]
        'location': DXFAttr(10, xtype='Point2D/3D'),
        'start_width': DXFAttr(40, default=0.0),
        'end_width': DXFAttr(41, default=0.0),
        'bulge': DXFAttr(42, default=0),
        'flags': DXFAttr(70),
        'tangent': DXFAttr(50),
        'vtx0': DXFAttr(71),
        'vtx1': DXFAttr(72),
        'vtx2': DXFAttr(73),
        'vtx3': DXFAttr(74),
    })
)


EMPTY_VERTEX_SUBCLASS = Tags()


class Vertex(polyline.Vertex, ModernGraphicEntityExtension):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_VERTEX_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, *vertex_subclass)

    def post_new_hook(self):
        self.update_subclass_specifier()

    def update_subclass_specifier(self):
        def set_subclass(subclassname):
            subclass = self.tags.subclasses[3]
            subclass[0] = DXFTag(100, subclassname)

        if self.is_3d_polyline_vertex:  # flags & const.VTX_3D_POLYLINE_VERTEX
            set_subclass('AcDb3dPolylineVertex')
        elif self.is_face_record:  # (flags & Vertex.FACE_FLAGS) == const.VTX_3D_POLYFACE_MESH_VERTEX:
            set_subclass('AcDbFaceRecord')
            self.tags.subclasses[2] = EMPTY_VERTEX_SUBCLASS  # clear subclass AcDbVertex
        elif self.is_poly_face_mesh_vertex:  # flags & Vertex.FACE_FLAGS == Vertex.FACE_FLAGS:
            set_subclass('AcDbPolyFaceMeshVertex')
        elif self.is_polygon_mesh_vertex:  # flags & const.VTX_3D_POLYGON_MESH_VERTEX:
            set_subclass('AcDbPolygonMeshVertex')
        else:
            set_subclass('AcDb2dVertex')


@loader.register('VERTEX', legacy=False)
def vertex_tags_processor(tags):
    """
    If subclass[2] is not 'AcDbVertex', insert empty subclass

    """
    if not isinstance(tags, ExtendedTags):
        return
    if tags.subclasses[2][0].value != 'AcDbVertex':
        tags.subclasses.insert(2, EMPTY_VERTEX_SUBCLASS)
    return tags
