#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pytest
from xml.etree import ElementTree as ET

from ezdxf.math import Vec2
from ezdxf.addons.drawing import svg, layout
from ezdxf.addons.drawing.properties import BackendProperties


class TestStyles:
    @pytest.fixture
    def xml(self):
        return ET.Element("defs")

    def test_create_stroke_style(self, xml):
        styles = svg.Styles(xml)
        cls = styles.get_class(stroke="black", stroke_width=10)
        assert cls == "C1"
        assert len(xml) == 1

        # repeat
        cls = styles.get_class(stroke="black", stroke_width=10)
        assert cls == "C1"
        assert len(xml) == 1

    def test_style_string(self, xml):
        styles = svg.Styles(xml)
        styles.get_class(stroke="black", stroke_width=10, stroke_opacity=0.5)

        string = ET.tostring(xml[0], encoding="unicode")
        assert (
            string
            == "<style>.C1 {stroke: black; stroke-width: 10; stroke-opacity: 0.500; "
            "fill: none; fill-opacity: 1.000;}</style>"
        )


class TestStrokeWidthMapping:
    def test_min_stroke_width(self):
        assert svg.map_lineweight_to_stroke_width(0.0, 10, 100) == 10

    def test_max_stroke_width(self):
        assert svg.map_lineweight_to_stroke_width(3.0, 10, 100) == 100

    def test_interpolation(self):
        # min_lineweight = 0.05 defined by DXF
        # max_lineweight = 2.11 defined by DXF
        assert svg.map_lineweight_to_stroke_width(0.25, 5, 211) == 25
        assert svg.map_lineweight_to_stroke_width(0.5, 5, 211) == 50
        assert svg.map_lineweight_to_stroke_width(1.0, 5, 211) == 100
        assert svg.map_lineweight_to_stroke_width(0.05, 5, 211) == 5
        assert svg.map_lineweight_to_stroke_width(2.11, 5, 211) == 211


NS = {
    "http://www.w3.org/2000/svg": "",
}


class TestSVGBackend:
    @pytest.fixture()
    def backend(self):
        backend_ = svg.SVGBackend()
        properties = BackendProperties(color="#ff0000", lineweight=0.25)
        points = Vec2.list([(0, 0), (100, 0), (100, 100), (0, 100)])
        backend_.draw_filled_polygon(points, properties)
        return backend_

    def test_get_xml_root_element(self, backend):
        xml = backend.get_xml_root_element(layout.Page(400, 300))
        assert xml.tag.endswith("svg") is True
        assert xml.attrib["width"] == "400mm"
        assert xml.attrib["height"] == "300mm"
        assert xml.attrib["viewBox"] == "0 0 1000000 750000"

    def test_get_string(self, backend):
        result = backend.get_string(layout.Page(400, 300))
        assert isinstance(result, str) is True
        xml = ET.fromstring(result)
        assert xml.tag.endswith("svg") is True
        assert xml.attrib["width"] == "400mm"
        assert xml.attrib["height"] == "300mm"
        assert xml.attrib["viewBox"] == "0 0 1000000 750000"


if __name__ == "__main__":
    pytest.main([__file__])
