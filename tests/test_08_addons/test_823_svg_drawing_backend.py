#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pytest
from xml.etree import ElementTree as ET

from ezdxf.math import Vec2, BoundingBox2d
from ezdxf.addons.drawing import svg
from ezdxf.addons.drawing.properties import BackendProperties


class TestPage:
    def test_ISO_A0(self):
        page = svg.Page(*svg.PAGE_SIZES["ISO A0"])
        assert page.width == 1189
        assert page.height == 841
        assert page.units == "mm"
        assert page.width_in_mm == 1189
        assert page.height_in_mm == 841

    def test_ANSI_A(self):
        page = svg.Page(*svg.PAGE_SIZES["ANSI A"])
        assert page.width == 11
        assert page.height == 8.5
        assert page.units == "in"
        assert page.width_in_mm == 279
        assert page.height_in_mm == 216

    def test_screen_size_in_pixels(self):
        page = svg.Page(800, 600, "px")
        assert page.width_in_mm == 212
        assert page.height_in_mm == 159


class TestSettings:
    def test_rotate_content(self):
        settings = svg.Settings(content_rotation=90)
        assert settings.content_rotation == 90

    def test_invalid_rotate_content_angle_raises_exception(self):
        with pytest.raises(ValueError):
            _ = svg.Settings(content_rotation=45)


class TestSVGBackend:
    def test_draw_polygon(self):
        backend = svg.SVGBackend()
        properties = BackendProperties(color="#ff0000", lineweight=0.25)
        points = Vec2.list([(0, 0), (100, 0), (100, 100), (0, 100)])
        backend.draw_filled_polygon(points, properties)
        result = backend.get_string(svg.Page(400, 300))
        assert isinstance(result, str) is True
        assert len(result) > 1
        xml = ET.fromstring(result)
        assert xml.tag.endswith("svg") is True
        assert xml.attrib["width"] == "400mm"
        assert xml.attrib["height"] == "300mm"
        assert xml.attrib["viewBox"] == "0 0 100000 75000"


if __name__ == "__main__":
    pytest.main([__file__])
