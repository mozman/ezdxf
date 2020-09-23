# Copyright (c) 2019-2020, Manfred Moitzi
# License: MIT-License
import math
import re
from typing import TYPE_CHECKING, List, Sequence, Iterable
from typing import Tuple, Optional
from xml.etree import ElementTree

from ezdxf.lldxf import validator
from ezdxf.lldxf.attributes import (
    DXFAttributes, DefSubclass, DXFAttr, XType, RETURN_DEFAULT,
)
from ezdxf.lldxf.const import (
    SUBCLASS_MARKER, DXFStructureError, DXF2010, DXFTypeError,
    InvalidGeoDataException
)
from ezdxf.lldxf.packedtags import VertexArray
from ezdxf.lldxf.tags import Tags, DXFTag
from ezdxf.math.vector import NULLVEC, Z_AXIS, Y_AXIS
from .dxfentity import base_class, SubclassProcessor
from .dxfobj import DXFObject
from .factory import register_entity
from .mtext import split_mtext_string
from .. import units
from ..math import Matrix44

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, DXFNamespace

__all__ = ['GeoData', 'MeshVertices']

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

    def __init__(self):
        super().__init__()
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

    def decoded_units(self) -> Tuple[Optional[str], Optional[str]]:
        return units.decode(self.dxf.horizontal_units), \
               units.decode(self.dxf.vertical_units)

    def get_crs(self) -> Tuple[int, bool]:
        """ Returns the EPSG index and axis-ordering, axis-ordering is ``True``
        if fist axis is labeled "E" or "W" and ``False`` if first axis is
        labeled "N" or "S".

        If axis-ordering is ``False`` the CRS is not compatible with the
        ``__geo_reference__`` interface or GeoJSON (see chapter 3.1.1).

        Raises:
            InvalidGeoDataException: for invalid or unknown XML data

        The EPSG number is stored in a tag like:

        .. code::

            <Alias id="27700" type="CoordinateSystem">
              <ObjectId>OSGB1936.NationalGrid</ObjectId>
              <Namespace>EPSG Code</Namespace>
            </Alias>

        The axis-ordering is stored in a tag like:

        .. code::

            <Axis uom="METER">
              <CoordinateSystemAxis>
                <AxisOrder>1</AxisOrder>
                <AxisName>Easting</AxisName>
                <AxisAbbreviation>E</AxisAbbreviation>
                <AxisDirection>east</AxisDirection>
              </CoordinateSystemAxis>
              <CoordinateSystemAxis>
                <AxisOrder>2</AxisOrder>
                <AxisName>Northing</AxisName>
                <AxisAbbreviation>N</AxisAbbreviation>
                <AxisDirection>north</AxisDirection>
              </CoordinateSystemAxis>
            </Axis>

        """
        definition = self.coordinate_system_definition
        try:
            # Remove namespaces so that tags can be searched without prefixing
            # their namespace:
            definition = _remove_xml_namespaces(definition)
            root = ElementTree.fromstring(definition)
        except ElementTree.ParseError:
            raise InvalidGeoDataException(
                'failed to parse coordinate_system_definition as xml')

        crs = None
        for alias in root.findall('Alias'):
            if alias.get('type') == 'CoordinateSystem' and \
                    alias.find('Namespace').text == 'EPSG Code':
                try:
                    crs = int(alias.get('id'))
                except ValueError:
                    raise InvalidGeoDataException(
                        f'invalid epsg number: {alias.get("id")}')
                break

        xy_ordering = None
        for axis in root.findall('.//CoordinateSystemAxis'):
            if axis.find('AxisOrder').text == '1':
                first_axis = axis.find('AxisAbbreviation').text
                if first_axis in ('E', 'W'):
                    xy_ordering = True
                elif first_axis in ('N', 'S'):
                    xy_ordering = False
                else:
                    raise InvalidGeoDataException(
                        f'unknown first axis: {first_axis}')
                break

        if crs is None:
            raise InvalidGeoDataException('no EPSG code associated with CRS')
        elif xy_ordering is None:
            raise InvalidGeoDataException('could not determine axis ordering')
        else:
            return crs, xy_ordering

    def get_crs_transformation(
            self, *, no_checks: bool = False) -> Tuple[Matrix44, int]:
        """ Returns the transformation matrix and the EPSG index to transform
        WCS coordinates into CRS coordinates. Because of the lack of proper
        documentation this method works only for tested configurations, set
        argument `no_checks` to ``True`` to use the method for untested geodata
        configurations, but the results may be incorrect.

        Supports only "Local Grid" transformation!

        Raises:
            InvalidGeoDataException: for untested geodata configurations

        """
        epsg, xy_ordering = self.get_crs()

        if not no_checks:
            if (self.dxf.coordinate_type != GeoData.LOCAL_GRID or
                    self.dxf.scale_estimation_method != GeoData.NONE or
                    not math.isclose(self.dxf.user_scale_factor, 1.0) or
                    self.dxf.sea_level_correction != 0 or
                    not math.isclose(self.dxf.sea_level_elevation, 0) or
                    self.faces or
                    not self.dxf.up_direction.isclose((0, 0, 1)) or
                    self.dxf.observation_coverage_tag != '' or
                    self.dxf.observation_from_tag != '' or
                    self.dxf.observation_to_tag != '' or
                    not xy_ordering):
                raise InvalidGeoDataException(
                    f'Untested geodata configuration: '
                    f'{self.dxf.all_existing_dxf_attribs()}.\n'
                    f'You can try with no_checks=True but the '
                    f'results may be incorrect.'
                )

        source = self.dxf.design_point  # in CAD WCS coordinates
        target = self.dxf.reference_point  # in the CRS of the geodata
        north = self.dxf.north_direction

        # -pi/2 because north is at pi/2 so if the given north is at pi/2, no
        # rotation is necessary:
        theta = -(math.atan2(north.y, north.x) - math.pi / 2)
        transformation = (
                Matrix44.translate(-source.x, -source.y, 0) @
                Matrix44.scale(self.dxf.horizontal_unit_scale,
                               self.dxf.vertical_unit_scale, 1) @
                Matrix44.z_rotate(theta) @
                Matrix44.translate(target.x, target.y, 0))
        return transformation, epsg


def _remove_xml_namespaces(xml_string: str) -> str:
    return re.sub('xmlns=\"[^\"]*\"', '', xml_string)
