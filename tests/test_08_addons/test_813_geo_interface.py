#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
from typing import cast
import pytest
from ezdxf.entities import factory
from ezdxf.addons import geo


def test_point_mapping():
    assert geo.point_mapping((0, 0)) == {
        'type': 'Point',
        'coordinates': (0, 0)
    }


def test_line_string_mapping():
    assert geo.line_string_mapping([(0, 0), (1, 0), (2, 0)]) == {
        'type': 'LineString',
        'coordinates': [(0, 0), (1, 0), (2, 0)]
    }


def test_polygon_without_holes_mapping():
    assert geo.polygon_mapping([(0, 0), (1, 0), (2, 0)]) == {
        'type': 'Polygon',
        'coordinates': [(0, 0), (1, 0), (2, 0), (0, 0)]
    }


def test_polygon_with_holes_mapping():
    assert geo.polygon_mapping([(0, 0), (1, 0), (2, 0)],
                               holes=[[(2, 0), (1, 0), (0, 0)]]) == {
               'type': 'Polygon',
               'coordinates': [
                   [(0, 0), (1, 0), (2, 0), (0, 0)],
                   [(2, 0), (1, 0), (0, 0), (2, 0)],
               ]
           }


@pytest.mark.parametrize('points', [
    [],
    [(0, 0)],
    [(0, 0), (1, 0)],
])
def test_polygon_mapping_vertex_count_error(points):
    with pytest.raises(ValueError):
        geo.polygon_mapping(points)


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
        'coordinates': [(0, 0), (1, 0), (1, 1), (0, 0)]
    }
    assert geo.mapping(pline, force_line_string=True) == {
        'type': 'LineString',
        'coordinates': [(0, 0), (1, 0), (1, 1), (0, 0)]
    }


def test_map_circle():
    circle = factory.new('CIRCLE')
    m = geo.mapping(circle)
    assert m['type'] == 'Polygon'
    assert len(m['coordinates']) == 8
    m = geo.mapping(circle, force_line_string=True)
    assert m['type'] == 'LineString'


if __name__ == '__main__':
    pytest.main([__file__])
