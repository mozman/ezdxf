#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
"""
Implementation of the `__geo_interface__`: https://gist.github.com/sgillies/2217756

Which is also supported by Shapely: https://pypi.org/project/Shapely/

Type definitions see GeoJson Standard: https://tools.ietf.org/html/rfc7946
and examples : https://tools.ietf.org/html/rfc7946#appendix-A

"""
from typing import (
    TYPE_CHECKING, Dict, Iterable, List, Union, cast, Callable, Sequence, Tuple,
)
import numbers
import copy
import math
from ezdxf.math import Vector, has_clockwise_orientation
from ezdxf.render import Path
from ezdxf.entities import DXFGraphic, LWPolyline, Hatch, Point
from ezdxf.lldxf import const
from ezdxf.entities import factory

if TYPE_CHECKING:
    from ezdxf.eztypes import Matrix44

__all__ = ['proxy', 'dxf_entities', 'gfilter', 'GeoProxy']

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
FEATURE = 'Feature'
FEATURE_COLLECTION = 'FeatureCollection'
MAX_FLATTENING_DISTANCE = 0.1
SUPPORTED_DXF_TYPES = {
    'POINT', 'LINE', 'LWPOLYLINE', 'POLYLINE', 'HATCH',
    'SOLID', 'TRACE', '3DFACE', 'CIRCLE', 'ARC', 'ELLIPSE', 'SPLINE',
}


def proxy(entity: Union[DXFGraphic, Iterable[DXFGraphic]],
          distance: float = MAX_FLATTENING_DISTANCE,
          force_line_string: bool = False) -> 'GeoProxy':
    """ Returns a :class:`GeoProxy` object.

    Args:
        entity: a single DXF entity or iterable of DXF entities
        distance: maximum flattening distance for curve approximations
        force_line_string: by default this function returns Polygon objects for
            closed geometries like CIRCLE, SOLID, closed POLYLINE and so on,
            by setting argument `force_line_string` to ``True``, this entities
            will be returned as LineString objects.

    """
    return GeoProxy.from_dxf_entities(entity, distance, force_line_string)


def dxf_entities(geo_mapping, polygon: int = 1,
                 dxfattribs: Dict = None) -> Iterable[DXFGraphic]:
    """ Returns ``__geo_interface__`` mappings as DXF entities.

    The `polygon` argument determines the method to convert polygons,
    use 1 for :class:`~ezdxf.entities.Hatch` entity, 2 for
    :class:`~ezdxf.entities.LWPolyline` or 3 for both.
    Option 2 returns for the exterior path and each hole a separated
    :class:`LWPolyline` entity. The :class:`Hatch` entity supports holes,
    but has no explicit border line.

    Yields :class:`Hatch` always before :class:`LWPolyline` entities.

    The returned DXF entities can be added to a layout by the
    :meth:`Layout.add_entity` method.

    Args:
        geo_mapping: ``__geo__interface__`` mapping as :class:`dict` or a Python
            object with a :attr:`__geo__interface__` property
        polygon: method to convert polygons (1-2-3)
        dxfattribs: dict with additional DXF attributes
    """
    return GeoProxy.parse(geo_mapping).to_dxf_entities(polygon, dxfattribs)


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


TFunc = Callable[[Vector], Vector]


class GeoProxy:
    """ Stores the ``__geo_interface__`` mapping in a parsed and compiled form.

    Stores coordinates as :class:`Vector` objects and represents "Polygon"
    always as tuple (exterior, holes) even without holes.

    Args:
        geo_mapping: parsed and compiled ``__geo_interface__`` mapping

    """

    def __init__(self, geo_mapping: Dict):
        self._root = geo_mapping

    @classmethod
    def parse(cls, geo_mapping: Dict) -> 'GeoProxy':
        """ Parse and compile a ``__geo_interface__`` mapping as :class:`dict`
        or a Python object with a ``__geo_interface__`` property, does some
        basic syntax checks, converts all coordinates into :class:`Vector`
        objects, represents "Polygon" always as tuple (exterior, holes) even
        without holes.

        """
        if hasattr(geo_mapping, '__geo_interface__'):
            geo_mapping = geo_mapping.__geo_interface__
        return cls(parse(geo_mapping))

    @property
    def root(self) -> Dict:
        return self._root

    def __copy__(self) -> 'GeoProxy':
        """ Returns a deep copy. """
        return copy.deepcopy(self)

    copy = __copy__

    @property
    def __geo_interface__(self) -> Dict:
        """ Returns the ``__geo_interface__`` compatible mapping as
        :class:`dict`.
        """
        return _rebuild(self._root)

    def __iter__(self) -> Iterable[Dict]:
        """ Iterate over all geo content objects.

        Yields only "Point", "LineString", "Polygon", "MultiPoint",
        "MultiLineString" and "MultiPolygon" objects, returns the content of
        "GeometryCollection", "FeatureCollection" and "Feature" as geometry
        objects ("Point", ...).

        """

        def _iter(root):
            type_ = root[TYPE]
            if type_ == FEATURE_COLLECTION:
                for feature in root[FEATURES]:
                    yield from _iter(feature)
            elif type_ == GEOMETRY_COLLECTION:
                for geometry in root[GEOMETRIES]:
                    yield from _iter(geometry)
            elif type_ == FEATURE:
                yield root[GEOMETRY]
            else:
                yield root

        yield from _iter(self._root)

    def globe_to_map(self, func: TFunc = None) -> None:
        """ Transform all coordinates recursive from globe representation
        in longitude and latitude in decimal degrees into 2D map representation
        in meters.

        Default is WGS84 `EPSG:4326 <https://epsg.io/4326>`_ (GPS) to WGS84
        `EPSG:3395 <https://epsg.io/3395>`_ World Mercator function
        :func:`wgs84_4326_to_3395`.

        To use different output units than meters, create a custom
        transformation function::

            my_proxy.globe_to_map(lambda x: geo.wgs84_4326_to_3395(x) * 39.37)

        or use the `pyproj <https://pypi.org/project/pyproj/>`_ package to write
        a complete custom projection function as needed.

        Args:
            func: custom transformation function, which takes one
                :class:`Vector` object as argument and returns the result as
                a :class:`Vector` object.

        """
        if func is None:
            func = wgs84_4326_to_3395
        self._transform(func)

    def map_to_globe(self, func: TFunc = None) -> None:
        """ Transform all coordinates recursive from 2D map representation in
        meters into globe representation as longitude and latitude in decimal
        degrees.

        Default is WGS84 `EPSG:3395 <https://epsg.io/3395>`_ World Mercator
        to WGS84 `EPSG:4326 <https://epsg.io/4326>`_ GPS function
        :func:`wgs84_3395_to_4326`.

        To use different input units than meters, create a custom transformation
        function::

            my_proxy.map_to_globe(lambda x: geo.wgs84_3395_to_4326(x * 0.0254))

        or use the `pyproj <https://pypi.org/project/pyproj/>`_ package to write
        a complete custom projection function as needed.

        Args:
            func: custom transformation function, which takes one
                :class:`Vector` object as argument and returns the result as
                a :class:`Vector` object.

        """
        if func is None:
            func = wgs84_3395_to_4326
        self._transform(func)

    def crs_to_wcs(self, crs: 'Matrix44') -> None:
        """ Transform all coordinates recursive from CRS into
        :ref:`WCS` coordinates by transformation matrix `crs` inplace,
        see also :meth:`GeoProxy.wcs_to_crs`.

        Args:
            crs: transformation matrix of type :class:`~ezdxf.math.Matrix44`

        """
        self._transform(crs.transform)

    def wcs_to_crs(self, crs: 'Matrix44') -> None:
        """ Transform all coordinates recursive from :ref:`WCS` coordinates into
        Coordinate Reference System (CRS) by transformation matrix `crs`
        inplace.

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
            crs: transformation matrix of type :class:`~ezdxf.math.Matrix44`

        """

        self._transform(crs.ucs_vertex_from_wcs)

    def _transform(self, func: TFunc):
        def process(entity: Dict):
            def convert(coords):
                if isinstance(coords, Vector):
                    return func(coords)
                else:
                    return [convert(c) for c in coords]

            entity[COORDINATES] = convert(entity[COORDINATES])

        for entity in self.__iter__():
            process(entity)

    @classmethod
    def from_dxf_entities(cls, entity: Union[DXFGraphic, Iterable[DXFGraphic]],
                          distance: float = MAX_FLATTENING_DISTANCE,
                          force_line_string: bool = False) -> 'GeoProxy':
        """ Constructor from a single DXF entity or an iterable of DXF entities.

        Args:
            entity: DXF entity or entities
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
        return cls(m)

    def to_dxf_entities(self, polygon: int = 1,
                        dxfattribs: Dict = None) -> Iterable[DXFGraphic]:
        """ Returns stored ``__geo_interface__`` mappings as DXF entities.

        The `polygon` argument determines the method to convert polygons,
        use 1 for :class:`~ezdxf.entities.Hatch` entity, 2 for
        :class:`~ezdxf.entities.LWPolyline` or 3 for both.
        Option 2 returns for the exterior path and each hole a separated
        :class:`LWPolyline` entity. The :class:`Hatch` entity supports holes,
        but has no explicit border line.

        Yields :class:`Hatch` always before :class:`LWPolyline` entities.

        The returned DXF entities can be added to a layout by the
        :meth:`Layout.add_entity` method.

        Args:
            polygon: method to convert polygons (1-2-3)
            dxfattribs: dict with additional DXF attributes
        """

        def point(vertex: Sequence) -> Point:
            point = cast(Point, factory.new('POINT', dxfattribs=dxfattribs))
            point.dxf.location = vertex
            return point

        def lwpolyline(vertices: Sequence) -> LWPolyline:
            polyline = cast(LWPolyline,
                            factory.new('LWPOLYLINE', dxfattribs=dxfattribs))
            polyline.append_points(vertices, format='xy')
            return polyline

        def polygon_(exterior: List,
                     holes: List) -> Iterable[Union[Hatch, LWPolyline]]:
            if polygon & 1:  # hatches first
                yield hatch_(exterior, holes)
            if polygon & 2:
                for path in [exterior] + holes:
                    yield lwpolyline(path)

        def hatch_(exterior: Sequence, holes: Sequence) -> Hatch:
            hatch = cast(Hatch, factory.new('HATCH', dxfattribs=dxfattribs))
            hatch.dxf.hatch_style = const.HATCH_STYLE_OUTERMOST
            hatch.paths.add_polyline_path(
                exterior, flags=const.BOUNDARY_PATH_EXTERNAL)
            for hole in holes:
                hatch.paths.add_polyline_path(
                    hole, flags=const.BOUNDARY_PATH_OUTERMOST)
            return hatch

        def entity(type_, coordinates) -> DXFGraphic:
            if type_ == POINT:
                yield point(coordinates)
            elif type_ == LINE_STRING:
                yield lwpolyline(coordinates)
            elif type_ == POLYGON:
                exterior, holes = coordinates
                yield from polygon_(exterior, holes)
            elif type_ == MULTI_POINT:
                for data in coordinates:
                    yield point(data)
            elif type_ == MULTI_LINE_STRING:
                for data in coordinates:
                    yield lwpolyline(data)
            elif type_ == MULTI_POLYGON:
                for data in coordinates:
                    exterior, holes = data
                    yield from polygon_(exterior, holes)

        dxfattribs = dxfattribs or dict()
        for _mapping in self.__iter__():
            yield from entity(_mapping.get(TYPE), _mapping.get(COORDINATES))


def parse(geo_mapping: Dict) -> Dict:
    """ Parse ``__geo_interface__`` convert all coordinates into
    :class:`Vector` objects, Polygon['coordinates'] is always a
    tuple (exterior, holes), holes maybe an empty list.

    """
    geo_mapping = copy.deepcopy(geo_mapping)
    type_ = geo_mapping.get(TYPE)
    if type_ is None:
        raise ValueError(f'Required key "{TYPE}" not found.')

    if type_ == FEATURE_COLLECTION:
        # It is possible for this array to be empty.
        features = geo_mapping.get(FEATURES)
        if features:
            geo_mapping[FEATURES] = [parse(f) for f in features]
        else:
            raise ValueError(
                f'Missing key "{FEATURES}" in FeatureCollection.')
    elif type_ == GEOMETRY_COLLECTION:
        # It is possible for this array to be empty.
        geometries = geo_mapping.get(GEOMETRIES)
        if geometries:
            geo_mapping[GEOMETRIES] = [parse(g) for g in geometries]
        else:
            raise ValueError(
                f'Missing key "{GEOMETRIES}" in GeometryCollection.')
    elif type_ == FEATURE:
        # The value of the geometry member SHALL be either a Geometry object
        # or, in the case that the Feature is unlocated, a JSON null value.
        if GEOMETRY in geo_mapping:
            geometry = geo_mapping.get(GEOMETRY)
            geo_mapping[GEOMETRY] = parse(geometry) if geometry else None
        else:
            raise ValueError(
                f'Missing key "{GEOMETRY}" in Feature.')
    elif type_ in {POINT, LINE_STRING, POLYGON, MULTI_POINT,
                   MULTI_LINE_STRING, MULTI_POLYGON}:
        coordinates = geo_mapping.get(COORDINATES)
        if coordinates is None:
            raise ValueError(
                f'Missing key "{COORDINATES}" in {type_}.')
        if type_ == POINT:
            coordinates = Vector(coordinates)
        elif type_ in (LINE_STRING, MULTI_POINT):
            coordinates = Vector.list(coordinates)
        elif type_ == POLYGON:
            coordinates = _parse_polygon(coordinates)
        elif type_ == MULTI_LINE_STRING:
            coordinates = [Vector.list(v) for v in coordinates]
        elif type_ == MULTI_POLYGON:
            coordinates = [_parse_polygon(v) for v in coordinates]
        geo_mapping[COORDINATES] = coordinates
    else:
        raise TypeError(f'Invalid type "{type_}".')
    return geo_mapping


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


def _parse_polygon(coordinates: Sequence) -> Sequence:
    """ Returns polygon definition as tuple (exterior, [holes]). """
    if _is_coordinate_sequence(coordinates):
        exterior = coordinates
        holes = []
    else:
        exterior = coordinates[0]
        holes = coordinates[1:]
    return Vector.list(exterior), [Vector.list(h) for h in holes]


def _rebuild(geo_mapping: Dict) -> Dict:
    """ Returns ``__geo_interface__`` compatible mapping as :class:`dict` from
    compiled internal representation.

    """

    def _polygon(exterior, holes):
        coordinates = [(v.x, v.y) for v in exterior]
        if holes:
            coordinates = [coordinates]
            coordinates.extend([(v.x, v.y) for v in hole] for hole in holes)
        return coordinates

    geo_interface = dict(geo_mapping)
    type_ = geo_interface[TYPE]
    if type_ == FEATURE_COLLECTION:
        geo_interface[FEATURES] = [
            _rebuild(f) for f in geo_interface[FEATURES]]
    elif type_ == GEOMETRY_COLLECTION:
        geo_interface[GEOMETRIES] = [
            _rebuild(g) for g in geo_interface[GEOMETRIES]]
    elif type_ == FEATURE:
        geo_interface[GEOMETRY] = _rebuild(geo_interface[GEOMETRY])
    elif type_ == POINT:
        v = geo_interface[COORDINATES]
        geo_interface[COORDINATES] = v.x, v.y
    elif type_ in (LINE_STRING, MULTI_POINT):
        coordinates = geo_interface[COORDINATES]
        geo_interface[COORDINATES] = [(v.x, v.y) for v in coordinates]
    elif type_ == MULTI_LINE_STRING:
        coordinates = []
        for line in geo_interface[COORDINATES]:
            coordinates.append([(v.x, v.y) for v in line])
    elif type_ == POLYGON:
        geo_interface[COORDINATES] = _polygon(*geo_interface[COORDINATES])
    elif type_ == MULTI_POLYGON:
        geo_interface[COORDINATES] = [
            _polygon(exterior, holes)
            for exterior, holes in geo_interface[COORDINATES]
        ]
    return geo_interface


def mapping(entity: DXFGraphic,
            distance: float = MAX_FLATTENING_DISTANCE,
            force_line_string: bool = False) -> Dict:
    """ Create the compiled ``__geo_interface__`` mapping as :class:`dict`
    for the given DXF `entity`, all coordinates are :class:`Vector` objects and
    represents "Polygon" always as tuple (exterior, holes) even without holes.


    Internal API - result is **not** a valid ``_geo_interface__`` mapping!

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
        return {TYPE: POINT, COORDINATES: entity.dxf.location}
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


def _line_string_or_polygon_mapping(points: List[Vector],
                                    force_line_string: bool):
    len_ = len(points)
    if len_ < 2:
        raise ValueError('Invalid vertex count.')
    if len_ == 2 or force_line_string:
        return line_string_mapping(points)
    else:
        if is_linear_ring(points):
            return polygon_mapping(points, [])
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

    Internal API - result is **not** a valid ``_geo_interface__`` mapping!

    Args:
        entities: iterable of DXF entities
        distance: maximum flattening distance for curve approximations
        force_line_string: by default this function returns "Polygon" objects for
            closed geometries like CIRCLE, SOLID, closed POLYLINE and so on,
            by setting argument `force_line_string` to ``True``, this entities
            will be returned as "LineString" objects.
    """
    m = [mapping(e, distance, force_line_string) for e in entities]
    types = set(g[TYPE] for g in m)
    if len(types) > 1:
        return geometry_collection_mapping(m)
    else:
        return join_multi_single_type_mappings(m)


def line_string_mapping(points: List[Vector]) -> Dict:
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
        COORDINATES: points
    }


def is_linear_ring(points: List[Vector]):
    return points[0].isclose(points[-1])


# GeoJSON : A linear ring MUST follow the right-hand rule with respect
# to the area it bounds, i.e., exterior rings are counterclockwise, and
# holes are clockwise.
def linear_ring(points: List[Vector], ccw=True) -> List[Vector]:
    """ Return `points` as linear ring (last vertex == first vertex),
    argument `ccw` defines the winding orientation, ``True`` for counter-clock
    wise and ``False`` for clock wise.

    """
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


def polygon_mapping(points: List[Vector], holes: List[List[Vector]]) -> Dict:
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
        holes = [linear_ring(hole, ccw=False) for hole in holes]
        rings = exterior, holes
    else:
        rings = exterior, []
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


# Values stored in GeoData RSS tag are not precise enough to match
# control calculation at epsg.io:
# Semi Major Axis: 6.37814e+06
# Semi Minor Axis: 6.35675e+06

WGS84_SEMI_MAJOR_AXIS = 6378137
WGS84_SEMI_MINOR_AXIS = 6356752.3142
WGS84_ELLIPSOID_ECCENTRIC = math.sqrt(
    1.0 - WGS84_SEMI_MINOR_AXIS ** 2 / WGS84_SEMI_MAJOR_AXIS ** 2)
CONST_E2 = math.e / 2.0
CONST_PI_2 = math.pi / 2.0
CONST_PI_4 = math.pi / 4.0


def wgs84_4326_to_3395(location: Vector) -> Vector:
    """ Transform WGS84 `EPSG:4326 <https://epsg.io/4326>`_ location given as
    latitude and longitude in decimal degrees as used by GPS into World Mercator
    cartesian 2D coordinates in meters `EPSG:3395 <https://epsg.io/3395>`_.

    Args:
        location: :class:`Vector` object, x-attribute represents the longitude
            value (East-West) in decimal degrees and the y-attribute
            represents the latitude value (North-South) in decimal degrees.
    """
    # From: https://epsg.io/4326
    # EPSG:4326 WGS84 - World Geodetic System 1984, used in GPS
    # To: https://epsg.io/3395
    # EPSG:3395 - World Mercator
    # Source: https://gis.stackexchange.com/questions/259121/transformation-functions-for-epsg3395-projection-vs-epsg3857
    longitude = math.radians(location.x)  # east
    latitude = math.radians(location.y)  # north
    a = WGS84_SEMI_MAJOR_AXIS
    e = WGS84_ELLIPSOID_ECCENTRIC
    e_sin_lat = math.sin(latitude) * e
    c = math.pow((1.0 - e_sin_lat) / (1.0 + e_sin_lat), e / 2.0)  # 7-7 p.44
    y = a * math.log(math.tan(CONST_PI_4 + latitude / 2.0) * c)  # 7-7 p.44
    x = a * longitude
    return Vector(x, y)


def wgs84_3395_to_4326(location: Vector, tol: float = 1e-6) -> Vector:
    """ Transform WGS84 World Mercator `EPSG:3395 <https://epsg.io/3395>`_
    location given as cartesian 2D coordinates x, y in meters into WGS84 decimal
    degrees as longitude and latitude `EPSG:4326 <https://epsg.io/4326>`_ as
    used by GPS.

    Args:
        location: :class:`Vector` object, z-axis is ignored
        tol: accuracy for latitude calculation

    """
    # From: https://epsg.io/3395
    # EPSG:3395 - World Mercator
    # To: https://epsg.io/4326
    # EPSG:4326 WGS84 - World Geodetic System 1984, used in GPS
    # Source: Map Projections - A Working Manual
    # https://pubs.usgs.gov/pp/1395/report.pdf
    a = WGS84_SEMI_MAJOR_AXIS
    e = WGS84_ELLIPSOID_ECCENTRIC
    e2 = e / 2.0
    pi2 = CONST_PI_2
    x, y, _ = location
    t = math.e ** (-y / a)  # 7-10 p.44
    latitude_ = pi2 - 2.0 * math.atan(t)  # 7-11 p.45
    while True:
        e_sin_lat = math.sin(latitude_) * e
        latitude = pi2 - 2.0 * math.atan(
            t * ((1.0 - e_sin_lat) / (1.0 + e_sin_lat)) ** e2)  # 7-9 p.44
        if abs(latitude - latitude_) < tol:
            break
        latitude_ = latitude

    longitude = x / a  # 7-12 p.45
    return Vector(math.degrees(longitude), math.degrees(latitude))


def dms2dd(d: float, m: float = 0, s: float = 0) -> float:
    """Convert degree, minutes, seconds into decimal degrees. """
    dd = d + float(m) / 60 + float(s) / 3600
    return dd


def dd2dms(dd: float) -> Tuple[float, float, float]:
    """Convert decimal degrees into degree, minutes, seconds. """
    m, s = divmod(dd * 3600, 60)
    d, m = divmod(m, 60)
    return d, m, s
