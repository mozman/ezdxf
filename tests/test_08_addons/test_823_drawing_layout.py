#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pytest

from ezdxf.math import Vec2
from ezdxf.addons.drawing import layout


class TestPage:
    def test_ISO_A0(self):
        page = layout.Page(*layout.PAGE_SIZES["ISO A0"])
        assert page.width == 1189
        assert page.height == 841
        assert page.units == layout.Units.mm
        assert page.width_in_mm == 1189
        assert page.height_in_mm == 841

    def test_ANSI_A(self):
        page = layout.Page(*layout.PAGE_SIZES["ANSI A"])
        assert page.width == 11
        assert page.height == 8.5
        assert page.units == layout.Units.inch
        assert page.width_in_mm == 279.4
        assert page.height_in_mm == 215.9

    def test_screen_size_in_pixels(self):
        page = layout.Page(800, 600, layout.Units.px)
        assert page.width_in_mm == 211.7
        assert page.height_in_mm == 158.8


class TestDetectFinalPage:
    """The page size detected automatically if Page.width or Page.height is 0."""

    def test_page_size_scale_1(self):
        """1 DXF drawing unit are represented by 1mm in the output drawing"""
        content_size = Vec2(100, 200)
        page = layout.final_page_size(
            content_size, layout.Page(0, 0, layout.Units.mm), layout.Settings(scale=1)
        )
        assert page.width == 100
        assert page.height == 200

    def test_page_size_scale_50(self):
        """50 DXF drawing unit are represented by 1mm in the output drawing"""
        content_size = Vec2(1000, 2000)
        page = layout.final_page_size(
            content_size,
            layout.Page(0, 0, layout.Units.mm),
            layout.Settings(scale=1 / 50),
        )
        assert page.width == 20
        assert page.height == 40

    def test_page_size_includes_margins_sc1(self):
        content_size = Vec2(100, 200)
        page = layout.final_page_size(
            content_size,
            layout.Page(0, 0, layout.Units.mm, layout.Margins.all2(20, 50)),
            layout.Settings(),
        )
        assert page.width == 100 + 50 + 50
        assert page.height == 200 + 20 + 20

    def test_page_size_includes_margins_sc50(self):
        content_size = Vec2(1000, 2000)
        page = layout.final_page_size(
            content_size,
            layout.Page(0, 0, layout.Units.mm, layout.Margins.all2(20, 50)),
            layout.Settings(scale=1 / 50),
        )
        assert page.width == 20 + 50 + 50
        assert page.height == 40 + 20 + 20

    def test_page_size_limited_page_height(self):
        content_size = Vec2(1000, 2000)
        page = layout.final_page_size(
            content_size,
            layout.Page(0, 0, layout.Units.mm, layout.Margins.all(0), max_height=841),
            layout.Settings(scale=1),
        )
        assert page.height == 841
        assert page.width == pytest.approx(420.5)

    def test_page_size_limited_page_width(self):
        content_size = Vec2(2000, 1000)
        page = layout.final_page_size(
            content_size,
            layout.Page(0, 0, layout.Units.mm, layout.Margins.all(0), max_width=841),
            layout.Settings(scale=1),
        )
        assert page.height == pytest.approx(420.5)
        assert page.width == 841


class TestFitToPage:
    @pytest.fixture(scope="class")
    def page(self):
        return layout.Page(200, 100)

    @pytest.fixture(scope="class")
    def page_with_margins(self):
        return layout.Page(220, 120, margins=layout.Margins.all(10))

    def test_stretch_width(self, page):
        factor = layout.fit_to_page(Vec2(100, 10), page)
        assert factor == pytest.approx(2)

    def test_stretch_height(self, page):
        factor = layout.fit_to_page(Vec2(10, 20), page)
        assert factor == pytest.approx(5)

    def test_shrink_width(self, page):
        factor = layout.fit_to_page(Vec2(400, 10), page)
        assert factor == pytest.approx(0.5)

    def test_shrink_height(self, page):
        factor = layout.fit_to_page(Vec2(50, 200), page)
        assert factor == pytest.approx(0.5)

    def test_stretch_width_margins(self, page_with_margins):
        factor = layout.fit_to_page(Vec2(100, 10), page_with_margins)
        assert factor == pytest.approx(2)

    def test_stretch_height_margins(self, page_with_margins):
        factor = layout.fit_to_page(Vec2(10, 20), page_with_margins)
        assert factor == pytest.approx(5)

    def test_shrink_width_margins(self, page_with_margins):
        factor = layout.fit_to_page(Vec2(400, 10), page_with_margins)
        assert factor == pytest.approx(0.5)

    def test_shrink_height_margins(self, page_with_margins):
        factor = layout.fit_to_page(Vec2(50, 200), page_with_margins)
        assert factor == pytest.approx(0.5)


class TestSettings:
    def test_rotate_content(self):
        settings = layout.Settings(content_rotation=90)
        assert settings.content_rotation == 90

    def test_invalid_rotate_content_angle_raises_exception(self):
        with pytest.raises(ValueError):
            _ = layout.Settings(content_rotation=45)


if __name__ == "__main__":
    pytest.main([__file__])
