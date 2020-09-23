#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
"""
Implementation of the `__geo_interface__`: https://gist.github.com/sgillies/2217756

Which is also supported by Shapely: https://pypi.org/project/Shapely/

Type definitions see GeoJson Standard: https://tools.ietf.org/html/rfc7946
and examples : https://tools.ietf.org/html/rfc7946#appendix-A

"""
from typing import (
    TYPE_CHECKING, Dict, Iterable, List, Union, cast, Callable, Sequence,
)
import numbers
from ezdxf.math import Vector, Vertex, has_clockwise_orientation
from ezdxf.render import Path
from ezdxf.entities import DXFGraphic, LWPolyline, Hatch, Point
from ezdxf.lldxf import const
from ezdxf.entities import factory

if TYPE_CHECKING:
    from ezdxf.eztypes import Matrix44

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
GEOMETRY = 'geometry'
FEATURES = 'features'
MAX_FLATTENING_DISTANCE = 0.1
SUPPORTED_DXF_TYPES = {
    'POINT', 'LINE', 'LWPOLYLINE', 'POLYLINE', 'HATCH',
    'SOLID', 'TRACE', '3DFACE', 'CIRCLE', 'ARC', 'ELLIPSE', 'SPLINE',
}


def gfilter(entities: Iterable[DXFGraphic]) -> Iterable[DXFGraphic]:
    """ Filter DXF entities from iterable `entities`, which are incompatible to
    the ``__geo_reference__`` interface.
    """
    for e in entities:
        dxftype = e.dxftype()
        if dxftype == 'POLYLINE':
            e = cast('Polyline', e)
            if e.is_2d_polyline or e.is_3d_polyline:
                yield e
        elif dxftype in SUPPORTED_DXF_TYPES:
            yield e


def mapping(entity: DXFGraphic,
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


def _hatch_as_polygon(hatch: Hatch, distance: float,
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


def collection(entities: Iterable[DXFGraphic],
               distance: float = MAX_FLATTENING_DISTANCE,
               force_line_string: bool = False) -> Dict:
    """ Create the ``__geo_interface__`` mapping as :class:`dict` for the
    given DXF `entities`, see https://gist.github.com/sgillies/2217756

    Returns a "MultiPoint", "MultiLineString" or "MultiPolygon" collection if
    all entities return the same GeoJSON type ("Point", "LineString", "Polygon")
    else a "GeometryCollection".

    Args:
        entities: iterable of DXF entities
        distance: maximum flattening distance for curve approximations
        force_line_string: by default this function returns "Polygon" objects for
            closed geometries like CIRCLE, SOLID, closed POLYLINE and so on,
            by setting argument `force_line_string` to ``True``, this entities
            will be returned as "LineString" objects.
    """
    m = mappings(entities, distance, force_line_string)
    types = set(g[TYPE] for g in m)
    if len(types) > 1:
        return geometry_collection_mapping(m)
    else:
        return join_multi_single_type_mappings(m)


def mappings(entities: Iterable[DXFGraphic],
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


def transform_wcs_to_crs(geo_mapping: Dict, crs: 'Matrix44') -> Dict:
    """ Transform all coordinates in `geo_mapping` recursive from :ref:`WCS`
    coordinates into Coordinate Reference System (CRS) by transformation matrix
    `crs`.

    The CRS is defined by the :class:`~ezdxf.entities.GeoData` entity,
    get the :class:`GeoData` entity from the modelspace by method
    :meth:`~ezdxf.layouts.Modelspace.get_geodata`.
    The CRS transformation matrix can be acquired form the :class:`GeoData`
    object by :meth:`~ezdxf.entities.GeoData.get_crs_transformation` method:

    .. code:: Python

        doc = ezdxf.readfile('file.dxf')
        msp = doc.modelspace()
        geodata = msp.get_geodata()
        if geodata:
            matrix, axis_ordering = geodata.get_crs_transformation()

    If `axis_ordering` is ``False`` the CRS is not compatible with the
    ``__geo_interface__`` or GeoJSON (see chapter 3.1.1).

    Args:
        geo_mapping: geo reference mapping as dict like object.
        crs: transformation matrix of type :class:`~ezdxf.math.Matrix44`

    Returns:
        New geo mapping as :class:`dict`.

    """
    return _transform_mapping(geo_mapping, crs.ucs_vertex_from_wcs)


def transform_crs_to_wcs(geo_mapping: Dict, crs: 'Matrix44') -> Dict:
    """ Transform all coordinates in `geo_mapping` recursive from CRS into
    :ref:`WCS` coordinates by transformation matrix `crs`,
    see also :func:`transform_wcs_to_crs`.

    Args:
        geo_mapping: geo reference mapping as dict like object.
        crs: transformation matrix of type :class:`~ezdxf.math.Matrix44`

    Returns:
        New geo mapping as :class:`dict`.

    """
    return _transform_mapping(geo_mapping, crs.transform)


def _transform_mapping(geo_mapping: Dict, tfunc: Callable) -> Dict:
    def _transform_coordinates(coordinates: Sequence):
        if len(coordinates) == 0:
            # I am sure an empty coordinates list is not valid, but
            # for robustness return an empty list, a proper validator
            # should take care about it.
            return list()
        if isinstance(coordinates[0], numbers.Real):
            point = tfunc(Vector(coordinates))
            return point.x, point.y
        else:
            return [_transform_coordinates(c) for c in coordinates]

    new_mapping = dict()
    for key, value in geo_mapping.items():
        if key == GEOMETRIES:
            new_mapping[GEOMETRIES] = _transform_mapping(value, tfunc)
        elif key == COORDINATES:
            new_mapping[COORDINATES] = _transform_coordinates(value)
        else:
            new_mapping[key] = value
    return new_mapping


class GeoProxy:
    def __init__(self, d: Dict):
        self.__geo_interface__ = d


def proxy(entity: Union[DXFGraphic, Iterable[DXFGraphic]],
          distance: float = MAX_FLATTENING_DISTANCE,
          force_line_string: bool = False) -> GeoProxy:
    """ Returns a :class:`GeoProxy` object, which has ``__geo_interface__``
    support.

    Args:
        entity: a single DXF entity or iterable of DXF entities
        distance: maximum flattening distance for curve approximations
        force_line_string: by default this function returns Polygon objects for
            closed geometries like CIRCLE, SOLID, closed POLYLINE and so on,
            by setting argument `force_line_string` to ``True``, this entities
            will be returned as LineString objects.

    """
    if isinstance(entity, DXFGraphic):
        m = mapping(entity, distance, force_line_string)
    else:
        m = collection(entity, distance)
    return GeoProxy(m)


def load(geo_mapping, polygon: int = 1, dxfattribs: Dict = None,
         crs: 'Matrix44' = None) -> Iterable[DXFGraphic]:
    """ Load ``__geo_interface__`` mappings from a :class:`dict` or a
    Python object(s) with ``__geo_interface__`` as DXF entities.

    The `polygon` argument determines the method to convert polygons, use 1 for
    :class:`~ezdxf.entities.Hatch` entity, 2 for
    :class:`~ezdxf.entities.LWPolyline` or 3 for both.
    Option 2 returns for the exterior path and each hole a separated
    :class:`LWPolyline` entity. The :class:`Hatch` entity supports holes,
    but has no explicit border line.

    Yields :class:`Hatch` always before :class:`LWPolyline` entities.

    The returned DXF entities can be added to a layout by the
    :meth:`Layout.add_entity` method.

    Args:
        geo_mapping: ``__geo_interface__`` mapping data or Python object(s)
            with ``__geo_interface__`` support
        polygon: method to convert polygons (1-2-3)
        dxfattribs: dict with additional DXF attributes
        crs: CRS transformation matrix (CRS to WCS)

    """

    def _load(_mapping) -> Iterable[DXFGraphic]:
        geometries = None
        if FEATURES in _mapping:  # FeatureCollection
            # It is possible for this array to be empty.
            geometries = _mapping[FEATURES]
        elif GEOMETRIES in _mapping:  # GeometryCollection
            # It is possible for this array to be empty.
            geometries = _mapping[GEOMETRIES]
        elif GEOMETRY in _mapping:  # Feature
            # The value of the geometry member SHALL be either a Geometry object
            # or, in the case that the Feature is unlocated, a JSON null value.
            geometries = []
            value = _mapping[GEOMETRY]
            if value:
                geometries.append(value)

        if isinstance(geometries, Sequence):
            for geometry in geometries:
                yield from _load(geometry)
            return

        type_ = _mapping.get(TYPE)
        if type_ is None:
            raise ValueError(f'Required key "{TYPE}" not found.')

        coordinates = geo_mapping.get(COORDINATES)
        if coordinates is None:
            raise ValueError(f'Required key "{COORDINATES}" not found.')

        if type_ == POINT:
            yield _load_point(coordinates, dxfattribs, crs)
        elif type_ == LINE_STRING:
            yield _load_lwpolyline(coordinates, dxfattribs, crs)
        elif type_ == POLYGON:
            yield from _load_polygon(
                coordinates, polygon, dxfattribs, crs)
        elif type_ == MULTI_POINT:
            for data in coordinates:
                yield _load_point(data, dxfattribs, crs)
        elif type_ == MULTI_LINE_STRING:
            for data in coordinates:
                yield _load_lwpolyline(data, dxfattribs, crs)
        elif type_ == MULTI_POLYGON:
            for data in coordinates:
                yield from _load_polygon(data, polygon, dxfattribs, crs)

    dxfattribs = dxfattribs or dict()
    if isinstance(geo_mapping, Sequence):
        # Sequence of Python object with __geo_interface__
        for entity in geo_mapping:
            yield from _load(entity.__geo_interface__)
        return

    if hasattr(geo_mapping, '__geo_interface__'):
        geo_mapping = geo_mapping.__geo_interface__
    yield from _load(geo_mapping)


def _load_point(vertex: Sequence, dxfattribs: Dict, m: 'Matrix44') -> Point:
    point = cast(Point, factory.new('POINT', dxfattribs=dxfattribs))
    if m:
        vertex = m.transform(vertex)
    point.dxf.location = vertex
    return point


def _load_lwpolyline(vertices: Sequence, dxfattribs: Dict,
                     m: 'Matrix44') -> LWPolyline:
    polyline = cast(LWPolyline,
                    factory.new('LWPOLYLINE', dxfattribs=dxfattribs))
    if m:
        vertices = m.transform_vertices(vertices)
    polyline.append_points(vertices, format='xy')
    return polyline


def _is_coordinate_sequence(coordinates: Sequence) -> bool:
    """ Returns ``True`` for a sequence of coordinates like [(0, 0), (1, 0)]
    and ``False`` for a sequence of sequences:
    [[(0, 0), (1, 0)], [(2, 0), (3, 0)]]
    """
    if not isinstance(coordinates, Sequence):
        raise ValueError('Invalid coordinate sequence.')
    if len(coordinates) == 0:
        raise ValueError('Invalid coordinate sequence.')
    first_item = coordinates[0]
    if len(first_item) == 0:
        raise ValueError('Invalid coordinate sequence.')
    return isinstance(first_item[0], numbers.Real)


def _load_polygon(vertices: Sequence, polygon: int, dxfattribs: Dict,
                  m: 'Matrix44') -> Iterable[Union[Hatch, LWPolyline]]:
    if _is_coordinate_sequence(vertices):
        exterior = vertices
        holes = []
    else:
        exterior = vertices[0]
        holes = vertices[1:]

    if polygon & 2:  # hatches first
        yield _load_hatch(exterior, holes, dxfattribs, m)
    if polygon & 1:
        for path in [exterior] + holes:
            yield _load_lwpolyline(path, dxfattribs, m)


def _load_hatch(exterior: Sequence, holes: Sequence, dxfattribs: Dict,
                transform: 'Matrix44') -> Hatch:
    def add_boundary_path(points, flags):
        if transform:
            points = list(transform.transform_vertices(points))
        hatch.paths.add_polyline_path(points, flags=flags)

    hatch = cast(Hatch, factory.new('HATCH', dxfattribs=dxfattribs))
    hatch.dxf.hatch_style = const.HATCH_STYLE_OUTERMOST
    add_boundary_path(exterior, const.BOUNDARY_PATH_EXTERNAL)
    for hole in holes:
        add_boundary_path(hole, const.BOUNDARY_PATH_OUTERMOST)
    return hatch


def point_mapping(point: Vertex) -> Dict:
    """ Returns a "Point" mapping.

    .. code::

        {
            "type": "Point",
            "coordinates": (100.0, 0.0)
        }

    """
    return {
        TYPE: POINT,
        COORDINATES: (point[0], point[1])
    }


def line_string_mapping(points: Iterable[Vertex]) -> Dict:
    """ Returns a "LineString" mapping.

    .. code::

        {
            "type": "LineString",
            "coordinates": [
                (100.0, 0.0),
                (101.0, 1.0)
            ]
        }
    """

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
    """ Return `points` as linear ring (last vertex == first vertex),
    argument `ccw` defines the winding orientation, ``True`` for counter-clock
    wise and ``False`` for clock wise.

    """
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
    """ Returns a "Polygon" mapping.

    .. code::

        {
            "type": "Polygon",
            "coordinates": [
                 [
                     (100.0, 0.0),
                     (101.0, 0.0),
                     (101.0, 1.0),
                     (100.0, 1.0),
                     (100.0, 0.0)
                 ],
                 [
                     (100.8, 0.8),
                     (100.8, 0.2),
                     (100.2, 0.2),
                     (100.2, 0.8),
                     (100.8, 0.8)
                 ]
            ]
        }
    """

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
    """ Returns multiple geometries as a "MultiPoint", "MultiLineString" or
    "MultiPolygon" mapping.
    """
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
    """ Returns multiple geometries as a "GeometryCollection" mapping.
    """
    return {
        TYPE: GEOMETRY_COLLECTION,
        GEOMETRIES: list(geometries)
    }
