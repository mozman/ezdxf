# Copyright (c) 2019-2020, Manfred Moitzi
# License: MIT-License
# Created: 2019-03-11
from typing import TYPE_CHECKING, List, Sequence, Iterable
from ezdxf.lldxf import validator
from ezdxf.lldxf.const import (
    SUBCLASS_MARKER, DXFStructureError, DXF2010, DXFTypeError,
)
from ezdxf.lldxf.attributes import (
    DXFAttributes, DefSubclass, DXFAttr, XType, RETURN_DEFAULT,
)
from ezdxf.lldxf.packedtags import VertexArray
from ezdxf.lldxf.tags import Tags, DXFTag
from ezdxf.math.vector import Vector, NULLVEC, Z_AXIS, Y_AXIS
from .dxfentity import base_class, SubclassProcessor
from .dxfobj import DXFObject
from .factory import register_entity
from .mtext import split_mtext_string

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, Drawing, DXFNamespace

__all__ = ['GeoData']

acdb_geo_data = DefSubclass('AcDbGeoData', {
    # 1 = R2009, but this release has no DXF version,
    # 2 = R2010
    'version': DXFAttr(90, default=2),

    # Handle to host block table record
    'block_record_handle': DXFAttr(330, default='0'),

    # 0 = unknown
    # 1 = local grid
    # 2 = projected grid
    # 3 = geographic (latitude/longitude)
    'coordinate_type': DXFAttr(
        70, default=3,
        validator=validator.is_in_integer_range(0, 4),
        fixer=RETURN_DEFAULT,
    ),

    # Design point, reference point in WCS coordinates:
    'design_point': DXFAttr(10, xtype=XType.point3d, default=NULLVEC),

    # Reference point in coordinate system coordinates, valid only when
    # coordinate type is Local Grid:
    'reference_point': DXFAttr(11, xtype=XType.point3d, default=NULLVEC),

    # Horizontal unit scale, factor which converts horizontal design coordinates
    # to meters by multiplication:
    'horizontal_unit_scale': DXFAttr(
        40, default=1,
        validator=validator.is_not_zero,
        fixer=RETURN_DEFAULT,
    ),

    # Horizontal units per UnitsValue enumeration. Will be kUnitsUndefined if
    # units specified by horizontal unit scale is not supported by AutoCAD
    # enumeration:
    'horizontal_units': DXFAttr(91, default=1),

    # Vertical unit scale, factor which converts vertical design coordinates
    # to meters by multiplication:
    'vertical_unit_scale': DXFAttr(41, default=1),

    # Vertical units per UnitsValue enumeration. Will be kUnitsUndefined if
    # units specified by vertical unit scale is not supported by AutoCAD
    # enumeration:
    'vertical_units': DXFAttr(92, default=1),

    'up_direction': DXFAttr(
        210, xtype=XType.point3d, default=Z_AXIS,
        validator=validator.is_not_null_vector,
        fixer=RETURN_DEFAULT,
    ),

    # North direction vector (2D)
    'north_direction': DXFAttr(
        12, xtype=XType.point2d, default=Y_AXIS,
        validator=validator.is_not_null_vector,
        fixer=RETURN_DEFAULT,
    ),

    # Scale estimation methods:
    # 1 = None
    # 2 = User specified scale factor;
    # 3 = Grid scale at reference point;
    # 4 = Prismoidal
    'scale_estimation_method': DXFAttr(
        95, default=1,
        validator=validator.is_in_integer_range(0, 5),
        fixer=RETURN_DEFAULT,
    ),

    'user_scale_factor': DXFAttr(
        141, default=1,
        validator=validator.is_not_zero,
        fixer=RETURN_DEFAULT,
    ),

    # Bool flag specifying whether to do sea level correction:
    'sea_level_correction': DXFAttr(
        294, default=0,
        validator=validator.is_integer_bool,
        fixer=RETURN_DEFAULT,
    ),

    'sea_level_elevation': DXFAttr(142, default=0),
    'coordinate_projection_radius': DXFAttr(143, default=0),
    # 303, 303, ..., 301: Coordinate system definition string
    'geo_rss_tag': DXFAttr(302, default='', optional=True),
    'observation_from_tag': DXFAttr(305, default='', optional=True),
    'observation_to_tag': DXFAttr(306, default='', optional=True),
    'observation_coverage_tag': DXFAttr(307, default='', optional=True),
    # 93: Number of Geo-Mesh points
    # mesh definition:
    # source mesh point (13, 23) repeat, mesh_point_count?
    # target mesh point (14, 24) repeat, mesh_point_count?
    # 96:  # Number of faces
    # face index 97 repeat, faces_count
    # face index 98 repeat, faces_count
    # face index 99 repeat, faces_count

})


class MeshVertices(VertexArray):
    VERTEX_SIZE = 2


@register_entity
class GeoData(DXFObject):
    """ DXF GEODATA entity """
    DXFTYPE = 'GEODATA'
    DXFATTRIBS = DXFAttributes(base_class, acdb_geo_data)
    MIN_DXF_VERSION_FOR_EXPORT = DXF2010

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

    def __init__(self, doc: 'Drawing' = None):
        super().__init__(doc)
        self.source_vertices = MeshVertices()
        self.target_vertices = MeshVertices()
        self.faces: List[Sequence[int]] = []
        self.coordinate_system_definition = ""

    def copy(self):
        raise DXFTypeError(f'Cloning of {self.DXFTYPE} not supported.')

    def load_dxf_attribs(
            self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.load_dxfattribs_into_namespace(dxf, acdb_geo_data)
            tags = self.load_coordinate_system_definition(tags)
            self.load_mesh_data(tags)
        return dxf

    def load_coordinate_system_definition(self, tags: Tags) -> Iterable[DXFTag]:
        # 303, 303, 301, Coordinate system definition string, always XML?
        lines = []
        for tag in tags:
            if tag.code in (301, 303):
                lines.append(tag.value.replace('^J', '\n'))
            else:
                yield tag
        if len(lines):
            self.coordinate_system_definition = ''.join(lines)

    def load_mesh_data(self, tags: Iterable[DXFTag]):
        face = []
        for tag in tags:
            code, value = tag
            if code == 13:
                self.source_vertices.append(value)
            elif code == 14:
                self.target_vertices.append(value)
            elif code in {97, 98, 99}:
                if code == 97 and len(face):
                    if len(face) != 3:
                        raise DXFStructureError(
                            f"GEODATA face definition error: invalid index "
                            f"count {len(face)}.")
                    self.faces.append(tuple(face))
                    face = []
                face.append(value)
        if len(face):  # collect last face
            self.faces.append(tuple(face))
        if len(self.source_vertices) != len(self.target_vertices):
            raise DXFStructureError(
                "GEODATA mesh definition error: source and target point count "
                "does not match.")

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        super().export_entity(tagwriter)
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_geo_data.name)
        self.dxf.export_dxf_attribs(tagwriter, [
            'version', 'block_record_handle', 'coordinate_type', 'design_point',
            'reference_point', 'horizontal_unit_scale', 'horizontal_units',
            'vertical_unit_scale', 'vertical_units', 'up_direction',
            'north_direction', 'scale_estimation_method', 'user_scale_factor',
            'sea_level_correction', 'sea_level_elevation',
            'coordinate_projection_radius'
        ])
        self.export_coordinate_system_definition(tagwriter)
        self.dxf.export_dxf_attribs(tagwriter, [
            'geo_rss_tag', 'observation_from_tag', 'observation_to_tag',
            'observation_coverage_tag'
        ])
        self.export_mesh_data(tagwriter)

    def export_mesh_data(self, tagwriter: 'TagWriter'):
        if len(self.source_vertices) != len(self.target_vertices):
            raise DXFTypeError(
                "GEODATA mesh definition error: source and target point count "
                "does not match."
            )

        tagwriter.write_tag2(93, len(self.source_vertices))
        for s, t in zip(self.source_vertices, self.target_vertices):
            tagwriter.write_vertex(13, s)
            tagwriter.write_vertex(14, t)

        tagwriter.write_tag2(96, len(self.faces))
        for face in self.faces:
            if len(face) != 3:
                raise DXFTypeError(
                    f"GEODATA face definition error: invalid index "
                    f"count {len(face)}.")
            f1, f2, f3 = face
            tagwriter.write_tag2(97, f1)
            tagwriter.write_tag2(98, f2)
            tagwriter.write_tag2(99, f3)

    def export_coordinate_system_definition(self, tagwriter: 'TagWriter'):
        text = self.coordinate_system_definition.replace('\n', '^J')
        chunks = split_mtext_string(text, size=255)
        if len(chunks) == 0:
            chunks.append("")
        while len(chunks) > 1:
            tagwriter.write_tag2(303, chunks.pop(0))
        tagwriter.write_tag2(301, chunks[0])
