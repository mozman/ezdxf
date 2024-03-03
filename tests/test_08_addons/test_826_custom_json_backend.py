# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
import pytest

from ezdxf.math import Vec2
from ezdxf.addons.drawing.backend import BackendProperties, BkPoints2d, BkPath2d
from ezdxf.addons.drawing import json
from ezdxf import path


class TestCustomJSONBackend:
    @pytest.fixture
    def backend(self):
        return json.CustomJSONBackend()

    @pytest.fixture
    def properties(self):
        return BackendProperties(color="#ff0000", lineweight=0.25, layer="One")

    def test_draw_point(
        self, backend: json.CustomJSONBackend, properties: BackendProperties
    ):
        backend.draw_point(Vec2(13, 17), properties)
        result = backend.get_json_data()
        point = result[0]
        assert point["type"] == "point"
        assert point["properties"]["color"] == "#ff0000"
        assert point["properties"]["stroke-width"] == 0.25
        assert point["properties"]["layer"] == "One"
        assert point["geometry"] == [13, 17]

    def test_draw_solid_lines(
        self, backend: json.CustomJSONBackend, properties: BackendProperties
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
        lines = result[0]
        assert lines["type"] == "lines"
        assert lines["geometry"] == [(0, 0, 1, 0), (2, 0, 3, 0), (4, 0, 5, 0)]

    def test_draw_path(
        self, backend: json.CustomJSONBackend, properties: BackendProperties
    ):
        p = path.Path((2, 2))
        p.line_to((4, 2))
        p.curve3_to((8, 2), (6, 3))
        p.curve4_to((11, 2), (9, 3), (10, 3))

        backend.draw_path(BkPath2d(p), properties)
        result = backend.get_json_data()
        json_path = result[0]
        assert json_path["type"] == "path"
        assert json_path["geometry"] == [
            ("M", 2, 2),
            ("L", 4, 2),
            ("Q", 6, 3, 8, 2),
            ("C", 9, 3, 10, 3, 11, 2),
        ]

    def test_draw_filled_polygon(
        self, backend: json.CustomJSONBackend, properties: BackendProperties
    ):  
        polygon = BkPoints2d(Vec2.list([(0, 0), (2, 0), (1, 1)]))
        backend.draw_filled_polygon(polygon, properties)
        result = backend.get_json_data()
        json_polygon = result[0]
        assert json_polygon["type"] == "filled-polygon"
        assert json_polygon["geometry"] == [(0, 0), (2, 0), (1, 1), (0, 0)]

    def test_json_str(
        self, backend: json.CustomJSONBackend, properties: BackendProperties
    ):
        backend.draw_point(Vec2(13, 17), properties)
        result = backend.get_string(indent=4)
        assert result == """[
    {
        "type": "point",
        "properties": {
            "color": "#ff0000",
            "stroke-width": 0.25,
            "layer": "One"
        },
        "geometry": [
            13.0,
            17.0
        ]
    }
]"""

if __name__ == "__main__":
    pytest.main([__file__])
