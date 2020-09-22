#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
"""
Implementation of the `__geo_interface__`: https://gist.github.com/sgillies/2217756

Which is also supported by Shapely: https://pypi.org/project/Shapely/

Type definitions see GeoJson Standard: https://tools.ietf.org/html/rfc7946
and examples : https://tools.ietf.org/html/rfc7946#appendix-A

"""
from typing import Dict, Iterable, List, Union, cast, TYPE_CHECKING
from ezdxf.math import Vector, Vertex, has_clockwise_orientation
from ezdxf.render import Path
from ezdxf.entities import DXFEntity
from ezdxf.lldxf import const

if TYPE_CHECKING:
    from ezdxf.eztypes import Hatch

TYPE = 'type'
COORDINATES = 'coordinates'
POINT = 'Point'
MULTI_POINT = 'MultiPoint'
LINE_STRING = 'LineString'
MULTI_LINE_STRING = 'MultiLineString'
POLYGON = 'Polygon'
MULTI_POLYGON = 'MultiPolygon'
GEOMETRY_COLLECTION = 'GeometryCollection'
GEOMETRIES = 'geometries'
MAX_FLATTENING_DISTANCE = 0.1
SUPPORTED_DXF_TYPES = {
    'POINT', 'LINE', 'LWPOLYLINE', 'POLYLINE', 'HATCH',
    'SOLID', 'TRACE', '3DFACE', 'CIRCLE', 'ARC', 'ELLIPSE', 'SPLINE',
}


def gfilter(entities: Iterable[DXFEntity]) -> Iterable[DXFEntity]:
    for e in entities:
        dxftype = e.dxftype()
        if dxftype == 'POLYLINE':
            e = cast('Polyline', e)
            if e.is_2d_polyline or e.is_3d_polyline:
                yield e
        elif dxftype in SUPPORTED_DXF_TYPES:
            yield e


def mapping(entity: DXFEntity,
            distance: float = MAX_FLATTENING_DISTANCE,
            force_line_string: bool = False) -> Dict:
    """ Create the ``__geo_interface__`` mapping as :class:`dict` for the
    given DXF `entity`, see https://gist.github.com/sgillies/2217756

    Args:
        entity: DXF entity
        distance: maximum flattening distance for curve approximations
        force_line_string: by default this function returns Polygon objects for
            closed geometries like CIRCLE, SOLID, closed POLYLINE and so on,
            by setting argument `force_line_string` to ``True``, this entities
            will be returned as LineString objects.

    """

    dxftype = entity.dxftype()
    if dxftype == 'POINT':
        return point_mapping(Vector(entity.dxf.location))
    elif dxftype == 'LINE':
        return line_string_mapping([entity.dxf.start, entity.dxf.end])
    elif dxftype == 'POLYLINE':
        entity = cast('Polyline', entity)
        if entity.is_3d_polyline or entity.is_2d_polyline:
            # May contain arcs as bulge values:
            path = Path.from_polyline(entity)
            points = list(path.flattening(distance))
            return _line_string_or_polygon_mapping(points, force_line_string)
        else:
            raise TypeError('Polymesh and Polyface not supported.')
    elif dxftype == 'LWPOLYLINE':
        # May contain arcs as bulge values:
        path = Path.from_lwpolyline(cast('LWPolyline', entity))
        points = list(path.flattening(distance))
        return _line_string_or_polygon_mapping(points, force_line_string)
    elif dxftype in {'CIRCLE', 'ARC', 'ELLIPSE', 'SPLINE'}:
        return _line_string_or_polygon_mapping(
            list(entity.flattening(distance)), force_line_string)
    elif dxftype in {'SOLID', 'TRACE', '3DFACE'}:
        return _line_string_or_polygon_mapping(
            entity.wcs_vertices(close=True), force_line_string)
    elif dxftype == 'HATCH':
        return _hatch_as_polygon(entity, distance, force_line_string)
    else:
        raise TypeError(dxftype)


def _line_string_or_polygon_mapping(points, force_line_string: bool):
    len_ = len(points)
    if len_ < 2:
        raise ValueError('Invalid vertex count.')
    if len_ == 2 or force_line_string:
        return line_string_mapping(points)
    else:
        if is_linear_ring(points):
            return polygon_mapping(points)
        else:
            return line_string_mapping(points)


def _hatch_as_polygon(hatch: 'Hatch', distance: float,
                      force_line_string: bool) -> Dict:
    def boundary_to_vertices(boundary) -> List[Vector]:
        if boundary.PATH_TYPE == 'PolylinePath':
            path = Path.from_hatch_polyline_path(boundary, ocs, elevation)
        else:
            path = Path.from_hatch_edge_path(boundary, ocs, elevation)

        vertices = list(path.flattening(distance))
        if not vertices[0].isclose(vertices[-1]):
            vertices.append(vertices[0])
        return vertices

    def filter_external(paths):
        if not has_explicit_external:
            external_id = id(external)
            paths = [p for p in paths if id(p) != external_id]
        return paths

    # Path vertex winding order can be ignored here, validation and
    # correction is done in polygon_mapping().

    elevation = hatch.dxf.elevation.z
    ocs = hatch.ocs()
    hatch_style = hatch.dxf.hath_style
    boundaries = hatch.paths
    count = len(boundaries)
    if count == 0:
        raise ValueError('HATCH without any boundary path.')

    has_explicit_external = True
    external = boundaries.external_path()
    if external is None:
        # This could be a male formed DXF file or just another lack of
        # information in the DXf reference.
        has_explicit_external = False
        external = boundaries[0]

    if count == 1 or hatch_style == const.HATCH_STYLE_IGNORE:
        points = boundary_to_vertices(external)
        return _line_string_or_polygon_mapping(points, force_line_string)
    else:
        # Result may be empty if no outer most boundaries are defined:
        holes = list(filter_external(boundaries.outer_most_paths()))
        if hatch_style == const.HATCH_STYLE_OUTERMOST and len(holes) == 0:
            # Hatch style is outer most, but no out most paths defined:
            hatch_style = const.HATCH_STYLE_NESTED
        if hatch_style == const.HATCH_STYLE_NESTED:
            # Nested style is not defined in GeoJSON Polygon type,
            # just add paths as additional holes and pray:
            holes.extend(filter_external(boundaries.default_paths()))

        if force_line_string:
            # Build a MultiString collection:
            points = boundary_to_vertices(external)
            geometries = [
                _line_string_or_polygon_mapping(points, force_line_string)
            ]
            for hole in holes:
                points = boundary_to_vertices(hole)
                geometries.append(
                    _line_string_or_polygon_mapping(points, force_line_string))
            return join_multi_single_type_mappings(geometries)
        else:
            points = boundary_to_vertices(external)
            return polygon_mapping(points, [
                boundary_to_vertices(h) for h in holes
            ])


def collection(entities: Iterable[DXFEntity],
               distance: float = MAX_FLATTENING_DISTANCE,
               force_line_string: bool = False) -> Dict:
    m = mappings(entities, distance, force_line_string)
    types = set(g[TYPE] for g in m)
    if len(types) > 1:
        return geometry_collection_mapping(m)
    else:
        return join_multi_single_type_mappings(m)


def mappings(entities: Iterable[DXFEntity],
             distance: float = MAX_FLATTENING_DISTANCE,
             force_line_string: bool = False) -> List[Dict]:
    """ Create the ``__geo_interface__`` mapping as :class:`dict` for all
    objects in `entities`. Returns just a list of individual mappings.

    Args:
        entities: multiple DXF entities
        distance: maximum flattening distance for curve approximations
        force_line_string: by default this function returns Polygon objects for
            closed geometries like CIRCLE, SOLID, closed POLYLINE and so on,
            by setting argument `force_line_string` to ``True``, this entities
            will be returned as LineString objects.

    """
    return [mapping(e, distance, force_line_string) for e in entities]


class GeoProxy:
    def __init__(self, d: Dict):
        self.__geo_interface__ = d


def proxy(entity: Union[DXFEntity, Iterable[DXFEntity]],
          distance: float = MAX_FLATTENING_DISTANCE,
          force_line_string: bool = False) -> GeoProxy:
    if isinstance(entity, DXFEntity):
        m = mapping(entity, distance, force_line_string)
    else:
        m = collection(entity, distance)
    return GeoProxy(m)


def point_mapping(point: Vertex) -> Dict:
    return {
        TYPE: POINT,
        COORDINATES: (point[0], point[1])
    }


def line_string_mapping(points: Iterable[Vertex]) -> Dict:
    return {
        TYPE: LINE_STRING,
        COORDINATES: [(v.x, v.y) for v in Vector.generate(points)]
    }


def is_linear_ring(points: List[Vertex]):
    return Vector(points[0]).isclose(points[-1])


# GeoJSON : A linear ring MUST follow the right-hand rule with respect
# to the area it bounds, i.e., exterior rings are counterclockwise, and
# holes are clockwise.
def linear_ring(points: Iterable[Vertex], ccw=True) -> List[Vector]:
    points = Vector.list(points)
    if len(points) < 3:
        raise ValueError(f'Invalid vertex count: {len(points)}')
    if not points[0].isclose(points[-1]):
        points.append(points[0])

    if has_clockwise_orientation(points):
        if ccw:
            points.reverse()
    else:
        if not ccw:
            points.reverse()

    return points


def polygon_mapping(points: Iterable[Vertex],
                    holes: Iterable[Iterable[Vertex]] = None) -> Dict:
    exterior = linear_ring(points, ccw=True)
    if holes:
        rings = [exterior]
        for hole in holes:
            rings.append(linear_ring(hole, ccw=False))
    else:
        rings = exterior
    return {
        TYPE: POLYGON,
        COORDINATES: rings,
    }


def join_multi_single_type_mappings(geometries: Iterable[Dict]) -> Dict:
    types = set()
    data = list()
    for g in geometries:
        types.add(g[TYPE])
        data.append(g[COORDINATES])

    if len(types) > 1:
        raise TypeError(f'Type mismatch: {str(types)}')
    elif len(types) == 0:
        return dict()
    else:
        return {
            TYPE: 'Multi' + tuple(types)[0],
            COORDINATES: data
        }


def geometry_collection_mapping(geometries: Iterable[Dict]) -> Dict:
    return {
        TYPE: GEOMETRY_COLLECTION,
        GEOMETRIES: list(geometries)
    }
