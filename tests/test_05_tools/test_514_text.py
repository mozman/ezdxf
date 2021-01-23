#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.tools.text import FontMeasurements, MonospaceFont, TextLine
from ezdxf.math import Vec3
from ezdxf.lldxf import const


@pytest.fixture
def default():
    return FontMeasurements(
        baseline=1.3,
        cap_height=1.0,
        x_height=0.5,
        descender_height=0.25
    )


def test_total_heigth(default):
    assert default.total_height == 1.25


def test_scale(default):
    fm = default.scale(2)
    assert fm.baseline == 2.6, "expected scaled baseline"
    assert fm.total_height == 2.5, "expected scaled total height"


def test_shift(default):
    fm = default.shift(1.0)
    assert fm.baseline == 2.3
    assert fm.total_height == 1.25


def test_scale_from_baseline(default):
    fm = default.scale_from_baseline(desired_cap_height=2.0)
    assert fm.baseline == 1.3, "expected unchanged baseline value"
    assert fm.cap_height == 2.0
    assert fm.x_height == 1.0
    assert fm.descender_height == 0.50
    assert fm.total_height == 2.5


def test_cap_top(default):
    assert default.cap_top == 2.3


def test_x_top(default):
    assert default.x_top == 1.8


def test_bottom(default):
    assert default.bottom == 1.05


def test_monospace_font():
    font = MonospaceFont(2.5, 0.75)
    assert font.text_width("1234") == 7.5


class TestTextLine:
    @pytest.fixture
    def font(self):
        return MonospaceFont(2.5, descender_factor=0.333)

    @pytest.fixture
    def text_line(self, font):
        return TextLine("text", font)

    def test_text_width_and_height(self, text_line):
        assert text_line.width == 10
        assert text_line.height == 2.5 * 1.333  # 1 + descender factor

    def test_shrink_to_fit(self, text_line):
        text_line.stretch("FIT", Vec3(0, 0), Vec3(5, 0))  # 50% shrink
        assert text_line.width == 5.0, "should shrink width"
        # cap height * 1.333 = 3.3325
        assert text_line.height == 3.3325, "should not shrink height"

    def test_stretch_to_aligned(self, text_line):
        text_line.stretch("ALIGNED", Vec3(0, 0), Vec3(15, 0))  # 50% stretch
        assert text_line.width == 15.0, "should stretch width"
        # cap height * 1.333 * 1.5 = 4.99875
        assert text_line.height == 4.99875, "should stretch height"

    def test_baseline_vertices_left_aligned(self, text_line):
        assert text_line.baseline_vertices(Vec3(0, 0)) == [
            Vec3(0, 0), Vec3(10, 0)]

    def test_baseline_vertices_center_aligned(self, text_line):
        assert text_line.baseline_vertices(Vec3(0, 0), halign=const.CENTER) == [
            Vec3(-5, 0), Vec3(5, 0)]

    def test_baseline_vertices_right_aligned(self, text_line):
        assert text_line.baseline_vertices(Vec3(0, 0), halign=const.RIGHT) == [
            Vec3(-10, 0), Vec3(0, 0)]

    def test_corner_vertices_baseline_aligned(self, text_line):
        fm = text_line.font_measurements()
        top = fm.cap_height
        bottom = -fm.descender_height
        assert text_line.corner_vertices(Vec3(0, 0), valign=const.BASELINE) == [
            Vec3(0, bottom), Vec3(10, bottom), Vec3(10, top), Vec3(0, top)]

    def test_corner_vertices_top_aligned(self, text_line):
        bottom = -text_line.height
        assert text_line.corner_vertices(Vec3(0, 0), valign=const.TOP) == [
            Vec3(0, bottom), Vec3(10, bottom), Vec3(10, 0), Vec3(0, 0)]

    def test_corner_vertices_bottom_aligned(self, text_line):
        top = text_line.height
        assert text_line.corner_vertices(Vec3(0, 0), valign=const.BOTTOM) == [
            Vec3(0, 0), Vec3(10, 0), Vec3(10, top), Vec3(0, top)]

    def test_corner_vertices_middle_aligned(self, text_line):
        fm = text_line.font_measurements()
        top = fm.cap_height / 2
        bottom = -(fm.descender_height + top)
        assert text_line.corner_vertices(Vec3(0, 0), valign=const.MIDDLE) == [
            Vec3(0, bottom), Vec3(10, bottom), Vec3(10, top), Vec3(0, top)
        ]


if __name__ == '__main__':
    pytest.main([__file__])
