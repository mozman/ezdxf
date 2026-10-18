import pytest


import re


from ezdxf.query import EntityQuery


from ezdxf.entities import Text, Line, Circle


from ezdxf.math import Vec3


class TestRegexMatch:
    @pytest.fixture
    def base(self):
        return EntityQuery(
            [
                Line.new(dxfattribs={"layer": "Lay_line", "color": 1}),
                Circle.new(dxfattribs={"layer": "lAy_circle", "center": Vec3(0, 0)}),
                Text.new(dxfattribs={"layer": "laY_text"}),
            ]
        )

    @pytest.mark.parametrize("ignore_case", [True, False])
    def test_invalid_regex_preserves_case_policy(self, base, ignore_case):
        layers = base["layer"]
        layers.ignore_case = ignore_case
        before = list(layers == "LAY_LINE")
        with pytest.raises(re.error):
            layers.match("[")
        assert layers.ignore_case is ignore_case
        assert list(layers == "LAY_LINE") == before

    @pytest.mark.parametrize("ignore_case", [True, False])
    def test_non_string_attribute_preserves_case_policy(self, base, ignore_case):
        query = base["color"]
        query.ignore_case = ignore_case
        with pytest.raises(TypeError):
            query.match(".*")
        assert query.ignore_case is ignore_case
