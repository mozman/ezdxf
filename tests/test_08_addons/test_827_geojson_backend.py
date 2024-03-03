# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
from typing import Any
import pytest

from ezdxf.math import Vec2
from ezdxf.addons.drawing.backend import BackendProperties, BkPoints2d, BkPath2d
from ezdxf.addons.drawing import json
from ezdxf import path


def test_properties():
    backend = json.GeoJSONBackend()
    properties = BackendProperties(color="#ff0000", lineweight=0.25, layer="One")
    backend.draw_point(Vec2(13, 17), properties)
    result = backend.get_json_data()
    assert result["type"] == "FeatureCollection"
    point = result["features"][0]
    assert point["type"] == "Feature"
    assert point["properties"]["color"] == "#ff0000"
    assert point["properties"]["stroke-width"] == 0.25
    assert point["properties"]["layer"] == "One"
    assert point["geometry"] == {"type": "Point", "coordinates": [13, 17]}


def no_properties(color: str, stroke_width: float, layer: str) -> dict[str, Any]:
    return {}


class TestGeoJSONBackendNoProperties:
    @pytest.fixture
    def backend(self):
        return json.GeoJSONBackend(properties_maker=no_properties)

    @pytest.fixture
    def properties(self):
        return BackendProperties(color="#ff0000", lineweight=0.25, layer="One")

    def test_draw_point(
        self, backend: json.GeoJSONBackend, properties: BackendProperties
    ):
        backend.draw_point(Vec2(13, 17), properties)
        result = backend.get_json_data()
        assert result["type"] == "GeometryCollection"
        point = result["geometries"][0]
        assert point["type"] == "Point"
        assert point["coordinates"] == [13, 17]

    def test_draw_solid_lines(
        self, backend: json.GeoJSONBackend, properties: BackendProperties
    ):
        backend.draw_solid_lines(
            [
                (Vec2(0, 0), Vec2(1, 0)),
                (Vec2(2, 0), Vec2(3, 0)),
                (Vec2(4, 0), Vec2(5, 0)),
            ],
            properties,
        )
        result = backend.get_json_data()
        lines = result["geometries"][0]
        assert lines["type"] == "MultiLineString"
        assert lines["coordinates"] == [
            ((0, 0), (1, 0)),
            ((2, 0), (3, 0)),
            ((4, 0), (5, 0)),
        ]

    def test_draw_path(
        self, backend: json.GeoJSONBackend, properties: BackendProperties
    ):
        p = path.Path((2, 2))
        p.line_to((4, 2))
        p.curve3_to((8, 2), (6, 3))
        p.curve4_to((11, 2), (9, 3), (10, 3))

        backend.draw_path(BkPath2d(p), properties)
        result = backend.get_json_data()
        json_path = result["geometries"][0]
        assert json_path["type"] == "LineString"
        coordinates = json_path["coordinates"]

        assert coordinates[0] == (2, 2)
        assert coordinates[-1] == (11, 2)

    def test_draw_filled_polygon(
        self, backend: json.GeoJSONBackend, properties: BackendProperties
    ):
        polygon = BkPoints2d(Vec2.list([(0, 0), (2, 0), (1, 1)]))
        backend.draw_filled_polygon(polygon, properties)
        result = backend.get_json_data()
        json_polygon = result["geometries"][0]
        assert json_polygon["type"] == "Polygon"
        assert json_polygon["coordinates"] == [[(0, 0), (2, 0), (1, 1), (0, 0)]]


if __name__ == "__main__":
    pytest.main([__file__])
