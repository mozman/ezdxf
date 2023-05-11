#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pytest
from xml.etree import ElementTree as ET

from ezdxf.math import Vec2
from ezdxf.addons.drawing import svg
from ezdxf.addons.drawing.properties import BackendProperties


class TestPage:
    def test_ISO_A0(self):
        page = svg.Page(*svg.PAGE_SIZES["ISO A0"])
        assert page.width == 1189
        assert page.height == 841
        assert page.units == svg.Units.mm
        assert page.width_in_mm == 1189
        assert page.height_in_mm == 841

    def test_ANSI_A(self):
        page = svg.Page(*svg.PAGE_SIZES["ANSI A"])
        assert page.width == 11
        assert page.height == 8.5
        assert page.units == svg.Units.inch
        assert page.width_in_mm == 279
        assert page.height_in_mm == 216

    def test_screen_size_in_pixels(self):
        page = svg.Page(800, 600, svg.Units.px)
        assert page.width_in_mm == 212
        assert page.height_in_mm == 159


class TestDetectFinalPage:
    """The page size detected automatically if Page.width or Page.height is 0."""

    def test_page_size_scale_1(self):
        """1 DXF drawing unit are represented by 1mm in the output drawing"""
        content_size = Vec2(100, 200)
        page = svg.final_page_size(
            content_size, svg.Page(0, 0, svg.Units.mm), svg.Settings(scale=1)
        )
        assert page.width == 100
        assert page.height == 200

    def test_page_size_scale_50(self):
        """50 DXF drawing unit are represented by 1mm in the output drawing"""
        content_size = Vec2(1000, 2000)
        page = svg.final_page_size(
            content_size, svg.Page(0, 0, svg.Units.mm), svg.Settings(scale=1 / 50)
        )
        assert page.width == 20
        assert page.height == 40

    def test_page_size_includes_margins_sc1(self):
        content_size = Vec2(100, 200)
        page = svg.final_page_size(
            content_size,
            svg.Page(0, 0, svg.Units.mm, svg.Margins.all2(20, 50)),
            svg.Settings(),
        )
        assert page.width == 100 + 50 + 50
        assert page.height == 200 + 20 + 20

    def test_page_size_includes_margins_sc50(self):
        content_size = Vec2(1000, 2000)
        page = svg.final_page_size(
            content_size,
            svg.Page(0, 0, svg.Units.mm, svg.Margins.all2(20, 50)),
            svg.Settings(scale=1 / 50),
        )
        assert page.width == 20 + 50 + 50
        assert page.height == 40 + 20 + 20

    def test_page_size_limited_page_height(self):
        content_size = Vec2(1000, 2000)
        page = svg.final_page_size(
            content_size,
            svg.Page(0, 0, svg.Units.mm, svg.Margins.all(0)),
            svg.Settings(scale=1, max_page_height=svg.Length(841, svg.Units.mm)),
        )
        assert page.height == 841
        assert page.width == pytest.approx(420.5)

    def test_page_size_limited_page_width(self):
        content_size = Vec2(2000, 1000)
        page = svg.final_page_size(
            content_size,
            svg.Page(0, 0, svg.Units.mm, svg.Margins.all(0)),
            svg.Settings(scale=1, max_page_width=svg.Length(841, svg.Units.mm)),
        )
        assert page.height == pytest.approx(420.5)
        assert page.width == 841


class TestFitToPage:
    @pytest.fixture(scope="class")
    def page(self):
        return svg.Page(200, 100)

    @pytest.fixture(scope="class")
    def page_with_margins(self):
        return svg.Page(220, 120, margins=svg.Margins.all(10))

    def test_stretch_width(self, page):
        factor = svg.fit_to_page(Vec2(100, 10), page)
        assert factor == pytest.approx(2)

    def test_stretch_height(self, page):
        factor = svg.fit_to_page(Vec2(10, 20), page)
        assert factor == pytest.approx(5)

    def test_shrink_width(self, page):
        factor = svg.fit_to_page(Vec2(400, 10), page)
        assert factor == pytest.approx(0.5)

    def test_shrink_height(self, page):
        factor = svg.fit_to_page(Vec2(50, 200), page)
        assert factor == pytest.approx(0.5)

    def test_stretch_width_margins(self, page_with_margins):
        factor = svg.fit_to_page(Vec2(100, 10), page_with_margins)
        assert factor == pytest.approx(2)

    def test_stretch_height_margins(self, page_with_margins):
        factor = svg.fit_to_page(Vec2(10, 20), page_with_margins)
        assert factor == pytest.approx(5)

    def test_shrink_width_margins(self, page_with_margins):
        factor = svg.fit_to_page(Vec2(400, 10), page_with_margins)
        assert factor == pytest.approx(0.5)

    def test_shrink_height_margins(self, page_with_margins):
        factor = svg.fit_to_page(Vec2(50, 200), page_with_margins)
        assert factor == pytest.approx(0.5)


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


class TestSettings:
    def test_rotate_content(self):
        settings = svg.Settings(content_rotation=90)
        assert settings.content_rotation == 90

    def test_invalid_rotate_content_angle_raises_exception(self):
        with pytest.raises(ValueError):
            _ = svg.Settings(content_rotation=45)


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
        xml = backend.get_xml_root_element(svg.Page(400, 300))
        assert xml.tag.endswith("svg") is True
        assert xml.attrib["width"] == "400mm"
        assert xml.attrib["height"] == "300mm"
        assert xml.attrib["viewBox"] == "0 0 1000000 750000"

    def test_get_string(self, backend):
        result = backend.get_string(svg.Page(400, 300))
        assert isinstance(result, str) is True
        xml = ET.fromstring(result)
        assert xml.tag.endswith("svg") is True
        assert xml.attrib["width"] == "400mm"
        assert xml.attrib["height"] == "300mm"
        assert xml.attrib["viewBox"] == "0 0 1000000 750000"

if __name__ == "__main__":
    pytest.main([__file__])
