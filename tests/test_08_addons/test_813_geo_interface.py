#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
from typing import cast
import pytest
from ezdxf.math import Vector
from ezdxf.entities import factory, Hatch, LWPolyline
from ezdxf.addons import geo

EXTERIOR = [(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]
HOLE1 = [(1, 1), (1, 2), (2, 2), (2, 1), (1, 1)]
HOLE2 = [(3, 3), (3, 4), (4, 4), (4, 3), (3, 3)]

POINT = {
    'type': 'Point',
    'coordinates': (0, 0)
}
LINE_STRING = {
    'type': 'LineString',
    'coordinates': EXTERIOR
}
POLYGON_0 = {
    'type': 'Polygon',
    'coordinates': EXTERIOR
}
POLYGON_1 = {
    'type': 'Polygon',
    'coordinates': [EXTERIOR, HOLE1]
}
POLYGON_2 = {
    'type': 'Polygon',
    'coordinates': [EXTERIOR, HOLE1, HOLE2]
}
MULTI_POINT = {
    'type': 'MultiPoint',
    'coordinates': EXTERIOR,
}
MULTI_LINE_STRING = {
    'type': 'MultiLineString',
    'coordinates': [EXTERIOR, HOLE1, HOLE2]
}
MULTI_POLYGON = {
    'type': 'MultiPolygon',
    'coordinates': [
        EXTERIOR,
        [EXTERIOR, HOLE1],
        [EXTERIOR, HOLE1, HOLE2],
    ]
}

GEOMETRY_COLLECTION = {
    'type': 'GeometryCollection',
    'geometries': [
        POINT,
        LINE_STRING,
        POLYGON_0,
    ]
}
FEATURE = {
    'type': 'Feature',
    'prop0': 'property',
    'geometry': LINE_STRING,
}
FEATURE_COLLECTION = {
    'type': 'FeatureCollection',
    'features': [FEATURE, FEATURE]
}


@pytest.mark.parametrize('points', [
    [],
    [(0, 0)],
    [(0, 0), (1, 0)],
])
def test_polygon_mapping_vertex_count_error(points):
    with pytest.raises(ValueError):
        geo.polygon_mapping(Vector.list(points), [])


def test_map_dxf_point():
    point = factory.new('POINT', dxfattribs={'location': (0, 0)})
    assert geo.mapping(point) == {
        'type': 'Point',
        'coordinates': (0, 0)
    }


def test_map_dxf_line():
    point = factory.new('LINE', dxfattribs={'start': (0, 0), 'end': (1, 0)})
    assert geo.mapping(point) == {
        'type': 'LineString',
        'coordinates': [(0, 0), (1, 0)]
    }


def test_map_polyline():
    pline = cast('Polyline', factory.new('POLYLINE'))
    pline.append_vertices([(0, 0), (1, 0), (1, 1)])
    pline.close()
    assert geo.mapping(pline) == {
        'type': 'Polygon',
        'coordinates': ([(0, 0), (1, 0), (1, 1), (0, 0)], [])
    }
    assert geo.mapping(pline, force_line_string=True) == {
        'type': 'LineString',
        'coordinates': [(0, 0), (1, 0), (1, 1), (0, 0)]
    }


def test_map_circle():
    circle = factory.new('CIRCLE')
    m = geo.mapping(circle)
    assert m['type'] == 'Polygon'
    assert len(m['coordinates'][0]) == 8
    m = geo.mapping(circle, force_line_string=True)
    assert m['type'] == 'LineString'


@pytest.mark.parametrize('entity', [
    {'type': 'Point', 'coordinates': (0, 0)},
    {'type': 'LineString', 'coordinates': [(0, 0), (1, 0)]},
    {'type': 'MultiPoint', 'coordinates': [(0, 0), (1, 0)]},
    {'type': 'MultiLineString',
     'coordinates': [[(0, 0), (1, 0)], [(0, 0), (1, 0)]]},
    {'type': 'Feature',
     'geometry': {'type': 'Point', 'coordinates': (0, 0)}},
    {'type': 'GeometryCollection',
     'geometries': [{'type': 'Point', 'coordinates': (0, 0)}]},
    {'type': 'FeatureCollection',
     'features': [
         {'type': 'Feature',
          'geometry': {'type': 'Point', 'coordinates': (0, 0)}}
     ]},
])
def test_parse_types(entity):
    # Parser does basic structure validation and converts all coordinates into
    # Vector objects.
    assert geo.parse(entity) == entity


def test_parsing_type_error():
    with pytest.raises(TypeError):
        geo.parse({'type': 'XXX'})


@pytest.mark.parametrize('entity', [
    {'type': 'Point'},  # no coordinates key
    {'type': 'Point', 'coordinates': None},  # no coordinates
    {'type': 'Feature'},  # no geometry key
    {'type': 'GeometryCollection'},  # no geometries key
    {'type': 'FeatureCollection'},  # no features key
])
def test_parsing_value_error(entity):
    with pytest.raises(ValueError):
        geo.parse(entity)


def test_parse_polygon_without_holes():
    polygon = geo.parse(POLYGON_0)
    assert polygon['coordinates'] == (EXTERIOR, []
                                      )


def test_parse_polygon_1_hole():
    polygon = geo.parse(POLYGON_1)
    assert polygon['coordinates'] == (EXTERIOR, [HOLE1])


def test_parse_polygon_2_holes():
    polygon = geo.parse(POLYGON_2)
    assert polygon['coordinates'] == (EXTERIOR, [HOLE1, HOLE2])


def test_parse_geometry_collection():
    geometry_collection = geo.parse(GEOMETRY_COLLECTION)
    assert len(geometry_collection['geometries']) == 3


def test_parse_feature():
    feature = geo.parse(FEATURE)
    assert feature['geometry'] == LINE_STRING


def test_parse_feature_collection():
    feature_collection = geo.parse(FEATURE_COLLECTION)
    assert len(feature_collection['features']) == 2


@pytest.mark.parametrize('entity', [
    POINT, LINE_STRING, POLYGON_0, POLYGON_1, POLYGON_2, GEOMETRY_COLLECTION,
    FEATURE, FEATURE_COLLECTION, MULTI_POINT, MULTI_LINE_STRING, MULTI_POLYGON,
])
def test_geo_interface_builder(entity):
    assert geo.GeoProxy.parse(entity).__geo_interface__ == entity


def test_point_to_dxf_entity():
    point = list(geo.dxf_entities(POINT))[0]
    assert point.dxftype() == 'POINT'
    assert point.dxf.location == (0, 0)


def test_line_string_to_dxf_entity():
    res = cast(LWPolyline, list(geo.dxf_entities(LINE_STRING))[0])
    assert res.dxftype() == 'LWPOLYLINE'
    assert list(res.vertices()) == Vector.list(EXTERIOR)


def test_polygon_without_holes_to_dxf_entity():
    res = cast(Hatch, list(geo.dxf_entities(POLYGON_0))[0])
    assert res.dxftype() == 'HATCH'
    assert len(res.paths) == 1
    p = res.paths[0]
    assert p.PATH_TYPE == 'PolylinePath'
    assert p.vertices == Vector.list(EXTERIOR)


def test_polygon_with_holes_to_dxf_entity():
    res = cast(Hatch, list(geo.dxf_entities(POLYGON_2))[0])
    assert len(res.paths) == 3
    p = res.paths[1]
    assert p.PATH_TYPE == 'PolylinePath'
    assert p.vertices == Vector.list(HOLE1)
    p = res.paths[2]
    assert p.PATH_TYPE == 'PolylinePath'
    assert p.vertices == Vector.list(HOLE2)


def test_geometry_collection_to_dxf_entities():
    collection = list(geo.dxf_entities(GEOMETRY_COLLECTION))
    assert len(collection) == 3


def test_feature_to_dxf_entities():
    entities = list(geo.dxf_entities(FEATURE))
    assert entities[0].dxftype() == 'LWPOLYLINE'


def test_feature_collection_to_dxf_entities():
    collection = list(geo.dxf_entities(FEATURE_COLLECTION))
    assert len(collection) == 2
    assert collection[0].dxftype() == 'LWPOLYLINE'


if __name__ == '__main__':
    pytest.main([__file__])
