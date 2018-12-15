# Created: 20.03.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable
from ezdxf.lldxf.const import DXFStructureError

from .graphics import none_subclass, entity_subclass, DXFAttr, DXFAttributes, DefSubclass, ExtendedTags, XType
from .solid3d import Body, modeler_geometry_subclass
from . import matrix_accessors

if TYPE_CHECKING:
    from ezdxf.eztypes import Matrix44

_SURFACE_TPL = """0
SURFACE
5
0
330
0
100
AcDbEntity
8
0
100
AcDbModelerGeometry
70
1
100
AcDbSurface
71
0
72
0
"""

_SURFACE_CLS = """0
CLASS
1
SURFACE
2
AcDbSurface
3
ObjectDBX Classes
90
4095
91
0
280
0
281
1
"""

surface_subclass = DefSubclass('AcDbSurface', {
    'u_count': DXFAttr(71),
    'v_count': DXFAttr(72),
})


class Surface(Body):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_SURFACE_TPL)
    CLASS = ExtendedTags.from_text(_SURFACE_CLS)
    DXFATTRIBS = DXFAttributes(
        none_subclass,
        entity_subclass,
        modeler_geometry_subclass,
        surface_subclass,
    )

    def _get_matrix(self, code: int) -> 'Matrix44':
        subclass = self.tags.subclasses[4]  # always 5th subclass, Surface has no transform matrix, but inherited classes
        try:
            return matrix_accessors.get_matrix(subclass, code)
        except DXFStructureError:
            raise DXFStructureError('Invalid transformation matrix in entity ' + self.__str__())

    def _set_matrix(self, code: int, data: Iterable[float]):
        subclass = self.tags.subclasses[4]  # always 5th subclass, Surface has no transform matrix, but inherited classes
        matrix_accessors.set_matrix(subclass, code, list(data))


_EXTRUDEDSURFACE_TPL = """0
EXTRUDEDSURFACE
5
0
330
0
100
AcDbEntity
8
0
100
AcDbModelerGeometry
70
1
100
AcDbSurface
71
0
72
0
100
AcDbExtrudedSurface
90
18
10
0.0
20
0.0
30
0.0
40
1.0
40
0.0
40
0.0
40
0.0
40
0.0
40
1.0
40
0.0
40
0.0
40
0.0
40
0.0
40
1.0
40
0.0
40
0.0
40
0.0
40
0.0
40
1.0
42
0.0
43
0.0
44
0.0
45
0.0
48
1.0
49
0.0
46
1.0
46
0.0
46
0.0
46
0.0
46
0.0
46
1.0
46
0.0
46
0.0
46
0.0
46
0.0
46
1.0
46 
0.0
46
0.0
46
0.0
46
0.0
46
1.0
47
1.0
47
0.0
47
0.0
47
0.0
47
0.0
47
1.0
47
0.0
47
0.0
47
0.0
47
0.0
47
1.0
47
0.0
47
0.0
47
0.0
47
0.0
47
1.0
290
0
70
0
71
2
292
1
293
0
294
0
295
1
296
0
11
0.0
21
0.0
31
0.0
"""

_EXTRUDEDSURFACE_CLS = """0
CLASS
1
EXTRUDEDSURFACE
2
AcDbExtrudedSurface
3
ObjectDBX Classes
90
0
91
0
280
0
281
1
"""

_ACDBASSOCEXTRUDEDSURFACEACTIONBODY_CLS = """0
CLASS
1
ACDBASSOCEXTRUDEDSURFACEACTIONBODY
2
AcDbAssocExtrudedSurfaceActionBody
3
ObjectDBX Classes
90
1025
91
0
280
0
281
0
"""

extruded_surface_subclass = DefSubclass('AcDbExtrudedSurface', {
    'class_id': DXFAttr(90),
    'sweep_vector': DXFAttr(10, xtype=XType.point3d),
    # 16x group code 40: Transform matrix of extruded entity (16 floats; row major format; default = identity matrix)
    'draft_angle': DXFAttr(42, default=0.),  # in radians
    'draft_start_distance': DXFAttr(43, default=0.),
    'draft_end_distance': DXFAttr(44, default=0.),
    'twist_angle': DXFAttr(45, default=0.),  # in radians?
    'scale_factor': DXFAttr(48, default=0.),
    'align_angle': DXFAttr(49, default=0.),  # in radians
    # 16x group code 46: Transform matrix of sweep entity (16 floats; row major format; default = identity matrix)
    # 16x group code 47: Transform matrix of path entity (16 floats; row major format; default = identity matrix)
    'solid': DXFAttr(290, default=0),  # true/false
    'sweep_alignment_flags': DXFAttr(290, default=0),  # 0=No alignment; 1=Align sweep entity to path
    # 2=Translate sweep entity to path; 3=Translate path to sweep entity
    'align_start': DXFAttr(292, default=0),  # true/false
    'bank': DXFAttr(293, default=0),  # true/false
    'base_point_set': DXFAttr(294, default=0),  # true/false
    'sweep_entity_transform_computed': DXFAttr(295, default=0),  # true/false
    'path_entity_transform_computed': DXFAttr(296, default=0),  # true/false
    'reference_vector_for_controlling_twist': DXFAttr(11, xtype=XType.point3d),
})


class ExtrudedSurface(Surface):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_EXTRUDEDSURFACE_TPL)
    CLASS = (
        ExtendedTags.from_text(_EXTRUDEDSURFACE_CLS),
        ExtendedTags.from_text(_ACDBASSOCEXTRUDEDSURFACEACTIONBODY_CLS),
    )
    DXFATTRIBS = DXFAttributes(
        none_subclass,
        entity_subclass,
        modeler_geometry_subclass,
        surface_subclass,
        extruded_surface_subclass,
    )

    def set_transformation_matrix_extruded_entity(self, matrix: 'Matrix44') -> None:
        self._set_matrix(code=40, data=matrix)

    def get_transformation_matrix_extruded_entity(self) -> 'Matrix44':
        return self._get_matrix(code=40)

    def set_sweep_entity_transformation_matrix(self, matrix: 'Matrix44') -> None:
        self._set_matrix(code=46, data=matrix)

    def get_sweep_entity_transformation_matrix(self) -> 'Matrix44':
        return self._get_matrix(code=46)

    def set_path_entity_transformation_matrix(self, matrix: 'Matrix44') -> None:
        self._set_matrix(code=47, data=matrix)

    def get_path_entity_transformation_matrix(self) -> 'Matrix44':
        return self._get_matrix(code=47)


_LOFTEDSURFACE_TPL = """0
LOFTEDSURFACE
5
0
330
0
100
AcDbEntity
8
0
100
AcDbModelerGeometry
70
1
100
AcDbSurface
71
0
72
0
100
AcDbLoftedSurface
40
1.0
40
0.0
40
0.0
40
0.0
40
0.0
40
1.0
40
0.0
40
0.0
40
0.0
40
0.0
40
1.0
40
0.0
40
0.0
40
0.0
40
0.0
40
1.0
70
0
41
0.0
42
0.0
43
0.0
44
0.0
290
0
291
1
292
1
293
1
294
0
295
0
296
0
297
1
"""


_LOFTEDSURFACE_CLS = """0
CLASS
1
LOFTEDSURFACE
2
AcDbLoftedSurface
3
ObjectDBX Classes
90
0
91
0
280
0
281
1
"""

_ACDBASSOCLOFTEDSURFACEACTIONBODY_CLS = """0
CLASS
1
ACDBASSOCLOFTEDSURFACEACTIONBODY
2
AcDbAssocLoftedSurfaceActionBody
3
ObjectDBX Classes
90
1025
91
0
280
0
281
0
"""

lofted_surface_subclass = DefSubclass('AcDbLoftedSurface', {
    # 16x group code 40: Transform matrix of loft entity (16 floats; row major format; default = identity matrix)
    'plane_normal_lofting_type': DXFAttr(70),
    'start_draft_angle': DXFAttr(41, default=0.),  # in radians
    'end_draft_angle': DXFAttr(42, default=0.),  # in radians
    'start_draft_magnitude': DXFAttr(43, default=0.),
    'end_draft_magnitude': DXFAttr(44, default=0.),
    'arc_length_parameterization': DXFAttr(290, default=0),  # true/false
    'no_twist': DXFAttr(291, default=1),  # true/false
    'align_direction': DXFAttr(292, default=1),  # true/false
    'simple_surfaces': DXFAttr(293, default=1),  # true/false
    'closed_surfaces': DXFAttr(294, default=0),  # true/false
    'solid': DXFAttr(295, default=0),  # true/false
    'ruled_surface': DXFAttr(296, default=0),  # true/false
    'virtual_guide': DXFAttr(297, default=0),  # true/false
})


class LoftedSurface(Surface):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_LOFTEDSURFACE_TPL)
    CLASS = (
        ExtendedTags.from_text(_LOFTEDSURFACE_CLS),
        ExtendedTags.from_text(_ACDBASSOCLOFTEDSURFACEACTIONBODY_CLS),
    )
    DXFATTRIBS = DXFAttributes(
        none_subclass,
        entity_subclass,
        modeler_geometry_subclass,
        surface_subclass,
        lofted_surface_subclass,
    )

    def set_transformation_matrix_lofted_entity(self, matrix: 'Matrix44') -> None:
        self._set_matrix(code=40, data=matrix)

    def get_transformation_matrix_lofted_entity(self) -> 'Matrix44':
        return self._get_matrix(code=40)


_REVOLVEDSURFACE_TPL = """0
REVOLVEDSURFACE
5
0
330
0
100
AcDbEntity
8
0
100
AcDbModelerGeometry
70
1
100
AcDbSurface
71
0
72
0
100
AcDbRevolvedSurface
90
36
10
0.0
20
0.0
30
0.0
11
0.0
21
0.0
31
1.0
40
0.0
41
0.0
42
1.0
42
0.0
42
0.0
42
0.0
42
0.0
42
1.0
42
0.0
42
0.0
42
0.0
42
0.0
42
1.0
42
0.0
42
0.0
42
0.0
42
0.0
42
1.0
43
0.0
44
0.0
45
0.0
46
0.0
290
0
291
0
"""

_REVOLVEDSURFACE_CLS = """0
CLASS
1
REVOLVEDSURFACE
2
AcDbRevolvedSurface
3
ObjectDBX Classes
90
0
91
2
280
0
281
1
"""


_ACDBASSOCREVOLVEDSURFACEACTIONBODY_CLS = """0
CLASS
1
ACDBASSOCREVOLVEDSURFACEACTIONBODY
2
AcDbAssocRevolvedSurfaceActionBody
3
ObjectDBX Classes
90
1025
91
2
280
0
281
0
"""

revolved_surface_subclass = DefSubclass('AcDbRevolvedSurface', {
    'class_id': DXFAttr(90, default=0.),
    'axis_point': DXFAttr(10, xtype=XType.point3d),
    'axis_vector': DXFAttr(11, xtype=XType.point3d),
    'revolve_angle': DXFAttr(40),  # in radians
    'start_angle': DXFAttr(41),  # in radians
    # 16x group code 42: Transform matrix of revolved entity (16 floats; row major format; default = identity matrix)
    'draft_angle': DXFAttr(43),  # in radians
    'start_draft_distance': DXFAttr(44, default=0),
    'end_draft_distance': DXFAttr(45, default=0),
    'twist_angle': DXFAttr(46, default=0),  # in radians
    'solid': DXFAttr(290, default=0),  # true/false
    'close_to_axis': DXFAttr(210, default=0),  # true/false
})


class RevolvedSurface(Surface):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_REVOLVEDSURFACE_TPL)
    CLASS = (
        ExtendedTags.from_text(_REVOLVEDSURFACE_CLS),
        ExtendedTags.from_text(_ACDBASSOCREVOLVEDSURFACEACTIONBODY_CLS),
    )
    DXFATTRIBS = DXFAttributes(
        none_subclass,
        entity_subclass,
        modeler_geometry_subclass,
        surface_subclass,
        revolved_surface_subclass,
    )

    def set_transformation_matrix_revolved_entity(self, matrix: 'Matrix44') -> None:
        self._set_matrix(code=42, data=matrix)

    def get_transformation_matrix_revolved_entity(self) -> 'Matrix44':
        return self._get_matrix(code=42)


_SWEPTSURFACE_TPL = """0
SWEPTSURFACE
5
0
330
0
100
AcDbEntity
8
0
100
AcDbModelerGeometry
70
1
100
AcDbSurface
71
0
72
0
100
AcDbSweptSurface
90
36
91
36
40
1.0
40
0.0
40
0.0
40
0.0
40
0.0
40
1.0
40
0.0
40
0.0
40
0.0
40
0.0
40
1.0
40
0.0
40
0.0
40
0.0
40
0.0
40
1.0
41
1.0
41
0.0
41
0.0
41
0.0
41
0.0
41
1.0
41
0.0
41
0.0
41
0.0
41
0.0
41
1.0
41
0.0
41
0.0
41
0.0
41
0.0
41
1.0
42
0.0
43
0.0
44
0.0
45
0.0
48
1.0
49
0.0
46
1.0
46
0.0
46
0.0
46
0.0
46
0.0
46
1.0
46
0.0
46
0.0
46
0.0
46
0.0
46
1.0
46
0.0
46
0.0
46
0.0
46
0.0
46
1.0
47
1.0
47
0.0
47
0.0
47
0.0
47
0.0
47
1.0
47
0.0
47
0.0
47
0.0
47
0.0
47
1.0
47
0.0
47
0.0
47
0.0
47
0.0
47
1.0
290
0
70
1
71
2
292
0
293
0
294
1
295
1
296
1
11
0.0
21
0.0
31
0.0
"""


_SWEPTSURFACE_CLS = """0
CLASS
1
SWEPTSURFACE
2
AcDbSweptSurface
3
ObjectDBX Classes
90
0
91
0
280
0
281
1
"""


_ACDBASSOCSWEPTSURFACEACTIONBODY_CLS = """0
CLASS
1
ACDBASSOCSWEPTSURFACEACTIONBODY
2
AcDbAssocSweptSurfaceActionBody
3
ObjectDBX Classes
90
1025
91
0
280
0
281
0
"""

swept_surface_subclass = DefSubclass('AcDbSweptSurface', {
    'swept_entity_id': DXFAttr(90),
    'path_entity_id': DXFAttr(91),
    # 16x group code 40: Transform matrix of sweep entity (16 floats; row major format; default = identity matrix)
    # 16x group code 41: Transform matrix of path entity (16 floats; row major format; default = identity matrix)

    # don't know the meaning of this matrices
    # 16x group code 46: Transform matrix of sweep entity (16 floats; row major format; default = identity matrix)
    # 16x group code 47: Transform matrix of path entity (16 floats; row major format; default = identity matrix)
    'draft_angle': DXFAttr(42),  # in radians
    'draft_start_distance': DXFAttr(43, default=0),
    'draft_end_distance': DXFAttr(44, default=0),
    'twist_angle': DXFAttr(45, default=0),  # in radians
    'scale_factor': DXFAttr(48, default=1),
    'align_angle': DXFAttr(49, default=0),  # in radians
    'solid': DXFAttr(90, default=0),  # in radians
    'sweep_alignment': DXFAttr(70, default=0),  # 0=No alignment; 1= align sweep entity to path;
    # 2=Translate sweep entity to path; 3=Translate path to sweep entity
    'align_start': DXFAttr(292, default=0),  # true/false
    'bank': DXFAttr(293, default=0),  # true/false
    'base_point_set': DXFAttr(294, default=0),  # true/false
    'sweep_entity_transform_computed': DXFAttr(295, default=0),  # true/false
    'path_entity_transform_computed': DXFAttr(296, default=0),  # true/false
    'reference_vector_for_controlling_twist': DXFAttr(11, xtype=XType.point3d),
})


class SweptSurface(Surface):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_SWEPTSURFACE_TPL)
    CLASS = (
        ExtendedTags.from_text(_SWEPTSURFACE_CLS),
        ExtendedTags.from_text(_ACDBASSOCSWEPTSURFACEACTIONBODY_CLS),
    )
    DXFATTRIBS = DXFAttributes(
        none_subclass,
        entity_subclass,
        modeler_geometry_subclass,
        surface_subclass,
        swept_surface_subclass,
    )

    def set_transformation_matrix_sweep_entity(self, matrix: 'Matrix44') -> None:
        self._set_matrix(code=40, data=matrix)

    def get_transformation_matrix_sweep_entity(self) -> 'Matrix44':
        return self._get_matrix(code=40)

    def set_transformation_matrix_path_entity(self, matrix: 'Matrix44') -> None:
        self._set_matrix(code=41, data=matrix)

    def get_transformation_matrix_path_entity(self) -> 'Matrix44':
        return self._get_matrix(code=41)

    # don't know the meaning of this matrices
    def set_sweep_entity_transformation_matrix(self, matrix: 'Matrix44') -> None:
        self._set_matrix(code=46, data=matrix)

    def get_sweep_entity_transformation_matrix(self) -> 'Matrix44':
        return self._get_matrix(code=46)

    def set_path_entity_transformation_matrix(self, matrix: 'Matrix44') -> None:
        self._set_matrix(code=47, data=matrix)

    def get_path_entity_transformation_matrix(self) -> 'Matrix44':
        return self._get_matrix(code=47)


_PLANESURFACE_CLS = """0
CLASS
1
PLANESURFACE
2
AcDbPlaneSurface
3
ObjectDBX Classes
90
4095
91
0
280
0
281
1
"""


# TODO: related by a handle to any surface entity
_NURBSURFACE_CLS = """0
CLASS
1
NURBSURFACE
2
AcDbNurbSurface
3
ObjectDBX Classes
90
0
91
0
280
0
281
1
"""