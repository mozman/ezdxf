# Created: 17.03.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT-License
from typing import TYPE_CHECKING, Optional, List, Tuple
from ezdxf.lldxf.const import DXFStructureError, DXFValueError
from ezdxf.lldxf.types import DXFTag, DXFVertex
from ezdxf.lldxf.tags import multi_tags_to_text, text_to_multi_tags

from .dxfobjects import DXFEntity, none_subclass, DXFAttr, DXFAttributes, DefSubclass, ExtendedTags, XType

if TYPE_CHECKING:
    from ezdxf.eztypes import Tags, Vertex

_GEODATA_CLS = """0
CLASS
1
GEODATA
2
AcDbGeoData
3
ObjectDBX Classes
90
4095
91
0
280
0
281
0
"""

_GEODATA_TPL = """0
GEODATA
5
0
102
{ACAD_REACTORS
330
0
102
}
330
DEAD
100
AcDbGeoData
90
3
330
70
70
2
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
0.0
40
1.0
91
1
41
1.0
92
1
210
0.0
220
0.0
230
1.0
12
0
22
1
95
3
141
1.0
294
0
142
0.0
143
0.0
301
COORDINATE_SYSTEM_DEFINITION
"""


class GeoData(DXFEntity):
    # works in R2009 but this release release has not a new DXF version, so official required DXF version is:
    # AC1024/R2010
    # new entity not supported yet
    # DXF structure:
    # BLOCK_RECORD (e.g. Model Space) has an (102, ACAD_XDICTIONARY) with an entry ACAD_GEOGRAPHICDATA which points to
    # a GEODATA entity, GEODATA ACAD_REACTORS and owner points to this ACAD_XDICTIONARY, block_record points
    # to BLOCK_RECORD entry
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_GEODATA_TPL)
    CLASS = ExtendedTags.from_text(_GEODATA_CLS)
    DXFATTRIBS = DXFAttributes(
        none_subclass,
        DefSubclass('AcDbGeoData', {
            'version': DXFAttr(90, default=2),  # works in R2009=1 but this release has no DXF version, R2010=2
            'coordinate_type': DXFAttr(70, default=3),
            # 0=unknown; 1=local grid; 2= projected grid; 3=geographic (latitude/longitude)
            'block_record': DXFAttr(330),  # handle to host block table record
            'design_point': DXFAttr(10, xtype=XType.point3d),  # Design point, reference point in WCS coordinates
            'reference_point': DXFAttr(11, xtype=XType.point3d),
            # Reference point in coordinate system coordinates, valid only when coordinate type is Local Grid.
            'north_direction': DXFAttr(12, xtype=XType.point2d),  # North direction vector (2D)
            'horizontal_unit_scale': DXFAttr(40),
            # Horizontal unit scale, factor which converts horizontal design coordinates to meters by multiplication.
            'vertical_unit_scale': DXFAttr(41),
            # Vertical unit scale, factor which converts vertical design coordinates to meters by multiplication.
            'horizontal_units': DXFAttr(91),
            # Horizontal units per UnitsValue enumeration. Will be kUnitsUndefined if units specified by horizontal unit scale is not supported by AutoCAD enumeration.
            'vertical_units': DXFAttr(92),
            # Vertical units per UnitsValue enumeration. Will be kUnitsUndefined if units specified by vertical unit scale is not supported by AutoCAD enumeration.
            'up_direction': DXFAttr(210, xtype=XType.point3d),  # Up direction
            'scale_estimation_method': DXFAttr(95, default=1),
            # 1=None; 2=User specified scale factor; 3=Grid scale at reference point; 4=Prismoidal
            'sea_level_correction': DXFAttr(294, default=0),  # Bool flag specifying whether to do sea level correction
            'user_scale_factor': DXFAttr(141, default=1),  # User specified scale factor
            'sea_level_elevation': DXFAttr(142, default=0),  # Sea level elevation
            'coordinate_projection_radius': DXFAttr(143, default=0),  # Coordinate projection radius
            'geo_rss_tag': DXFAttr(302, default=''),  # GeoRSS tag
            'observation_from_tag': DXFAttr(305, default=''),  # Observation from tag
            'observation_to_tag': DXFAttr(306, default=''),  # Observation to tag
            'mesh_point_count': DXFAttr(93),  # Number of Geo-Mesh points
            # mesh definition:
            # source mesh point (13, 23) repeat, mesh_point_count?
            # target mesh point (14, 24) repeat, mesh_point_count?
            'mesh_faces_count': DXFAttr(96),  # Number of faces
            # face index 97 repeat, faces_count
            # face index 98 repeat, faces_count
            # face index 99 repeat, faces_count

        }),

    )
    # coordinate_type const
    UNKNOWN = 0
    LOCAL_GRID = 1
    PROJECTED_GRID = 2
    GEOGRAPHIC = 3

    # scale_estimation_method const
    NONE = 1
    USER_SCALE = 2
    GRID_SCALE = 3
    PRISMOIDEAL = 4

    @property
    def AcDbGeoData(self) -> 'Tags':
        return self.tags.get_subclass('AcDbGeoData')

    def get_coordinate_system_definition(self) -> str:
        # 303, 303, 301, Coordinate system definition string, always XML?
        start = self._get_start_of_coordinate_system_definition()
        if start is not None:
            tags = self.AcDbGeoData.collect_consecutive_tags((303, 301), start=start)
            return multi_tags_to_text(tags, line_ending='^J')
        else:
            return ""

    def set_coordinate_system_definition(self, text: str) -> None:
        tags = text_to_multi_tags(text, code=303, size=255, line_ending='^J')
        if len(tags):
            last_value = tags[-1].value
            tags[-1] = DXFTag(code=301, value=last_value)  # change group code of last tag 303 -> 301
            insert_pos = self._get_start_of_coordinate_system_definition()
            geodata = self.AcDbGeoData
            if insert_pos is None:
                insert_pos = geodata.tag_index(330) + 1  # 330 host block record is required
            self.AcDbGeoData.remove_tags((301, 303))
            geodata[insert_pos:insert_pos] = tags

    def _get_start_of_coordinate_system_definition(self) -> Optional[int]:
        try:
            start = self.AcDbGeoData.tag_index(303)
        except DXFValueError:
            try:
                start = self.AcDbGeoData.tag_index(301)
            except DXFValueError:
                return None
        return start

    def get_mesh_data(self) -> Tuple[List[Tuple['Vertex', 'Vertex']], List[List['Vertex']]]:
        geo_data = self.AcDbGeoData

        def get_vertices() -> List[Tuple['Vertex', 'Vertex']]:
            try:
                start = geo_data.tag_index(93)
            except DXFValueError:
                return []

            vertex_tags = geo_data.collect_consecutive_tags((13, 14), start=start + 1)
            source_vertices = []  # type: List[Vertex]
            target_vertices = []  # type: List[Vertex]
            for vertex in vertex_tags:
                if vertex.code == 13:
                    source_vertices.append(vertex.value)
                else:
                    target_vertices.append(vertex.value)
            if len(source_vertices) != len(target_vertices):
                raise DXFStructureError(
                    "GEODATA(#{}) mesh definition error: source and target point count does not match ().".format(
                        self.dxf.handle))

            return list(zip(source_vertices, target_vertices))

        def get_faces() -> List[List['Vertex']]:
            try:
                start = geo_data.tag_index(96)
            except DXFValueError:
                return []

            face_tags = geo_data.collect_consecutive_tags((97, 98, 99), start=start + 1)
            faces = []  # type: List[List[Vertex]]
            face = []  # type: List[Vertex]
            for face_tag in face_tags:
                if face_tag.code == 97:
                    if len(face):
                        faces.append(face)
                        face = []
                face.append(face_tag.value)
            if len(face):  # add last face
                faces.append(face)
            return faces

        return get_vertices(), get_faces()

    def set_mesh_data(self,
                      vertices: List[Tuple['Vertex', 'Vertex']] = None,
                      faces: List[List['Vertex']] = None) -> None:
        if vertices is None:
            vertices = []
        else:
            vertices = list(vertices)
        if faces is None:
            faces = []
        else:
            faces = list(faces)
        self._remove_mesh_data()
        geodata = self.AcDbGeoData
        geodata.append(DXFTag(93, len(vertices)))
        for source, target in vertices:
            geodata.append(DXFVertex(13, (source[0], source[1])))
            geodata.append(DXFVertex(14, (target[0], target[1])))
        geodata.append(DXFTag(96, len(faces)))
        for face in faces:
            geodata.extend(DXFTag(code, index) for code, index in zip((97, 98, 99), face))

    def _remove_mesh_data(self) -> None:
        self.AcDbGeoData.remove_tags(codes=(93, 13, 14, 96, 97, 98, 99))
