#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.tools.text import FontMeasurements


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
    assert fm.baseline == 1.3
    assert fm.total_height == 2.5


def test_shift(default):
    fm = default.shift(1.0)
    assert fm.baseline == 2.3
    assert fm.total_height == 1.25


def test_scale_from_baseline(default):
    fm = default.scale_from_baseline(desired_cap_height=2.0)
    assert fm.baseline == 1.3
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


if __name__ == '__main__':
    pytest.main([__file__])
