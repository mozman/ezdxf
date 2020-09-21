#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
"""
Implementation of the `__geo_interface__`: https://gist.github.com/sgillies/2217756

Which is also supported by Shapely: https://pypi.org/project/Shapely/

Type definitions see GeoJson Standard: https://tools.ietf.org/html/rfc7946
and examples : https://tools.ietf.org/html/rfc7946#appendix-A

"""
from typing import TYPE_CHECKING, Dict, Iterable, List, Union
from ezdxf.math import Vector, Vertex
from ezdxf.entities import DXFEntity

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFEntity

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
    return (e for e in entities if e.dxftype() in SUPPORTED_DXF_TYPES)


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
    else:
        raise TypeError(dxftype)


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


def linear_ring(points: Iterable[Vertex]) -> List[Vector]:
    points = Vector.list(points)
    if len(points) < 3:
        raise ValueError(f'Invalid vertex count: {len(points)}')
    if not points[0].isclose(points[-1]):
        points.append(points[0])
    return points


def polygon_mapping(points: Iterable[Vertex],
                    holes: Iterable[Iterable[Vertex]] = None) -> Dict:
    exterior = linear_ring(points)
    if holes:
        rings = [exterior]
        for hole in holes:
            rings.append(linear_ring(hole))
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
