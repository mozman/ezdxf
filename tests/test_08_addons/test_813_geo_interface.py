#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
from typing import cast
import pytest
from ezdxf.math import Vector
from ezdxf.entities import factory, Hatch, LWPolyline
from ezdxf.addons import geo


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
    polygon = geo.parse({
        'type': 'Polygon',
        'coordinates': [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]
    })
    assert polygon['coordinates'] == (
        [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)], []
    )


def test_parse_polygon_with_holes():
    polygon = geo.parse({
        'type': 'Polygon',
        'coordinates': [
            [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)],
            [(0.5, 0.5), (0.7, 0.5), (0.7, 0.7), (0.5, .7), (0.5, 0.5)],
        ]
    })
    assert polygon['coordinates'] == (
        [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)],
        [
            [(0.5, 0.5), (0.7, 0.5), (0.7, 0.7), (0.5, .7), (0.5, 0.5)]
        ]
    )


def test_point_to_dxf_entity():
    proxy = geo.GeoProxy.parse({'type': 'Point', 'coordinates': (0, 0)})
    point = list(proxy.to_dxf_entities())[0]
    assert point.dxftype() == 'POINT'
    assert point.dxf.location == (0, 0)


def test_line_string_to_dxf_entity():
    proxy = geo.GeoProxy.parse({
        'type': 'LineString',
        'coordinates': [(0, 0), (1, 0)]
    })
    res = cast(LWPolyline, list(proxy.to_dxf_entities())[0])
    assert res.dxftype() == 'LWPOLYLINE'
    assert list(res.vertices()) == [(0, 0), (1, 0)]


def test_polygon_without_holes_to_dxf_entity():
    proxy = geo.GeoProxy.parse({
        'type': 'Polygon',
        'coordinates': [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]
    })
    res = cast(Hatch, list(proxy.to_dxf_entities())[0])
    assert res.dxftype() == 'HATCH'
    assert len(res.paths) == 1
    p = res.paths[0]
    assert p.PATH_TYPE == 'PolylinePath'
    assert p.vertices == Vector.list(
        [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])


def test_polygon_with_hole_to_dxf_entity():
    proxy = geo.GeoProxy.parse({
        'type': 'Polygon',
        'coordinates': [
            [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)],
            [(.5, .5), (.7, .5), (.7, .7), (.5, .7), (.5, .5)],
        ]
    })
    res = cast(Hatch, list(proxy.to_dxf_entities())[0])
    assert len(res.paths) == 2


if __name__ == '__main__':
    pytest.main([__file__])
