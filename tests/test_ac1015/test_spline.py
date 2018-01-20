# Created: 12.04.2014, 2018 rewritten for pytest
# Copyright (C) 2014-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest
from ezdxf.modern.spline import Spline, _SPLINE_TPL
from ezdxf.lldxf.extendedtags import ExtendedTags


@pytest.fixture
def spline():
    return Spline(ExtendedTags.from_text(_SPLINE_TPL))


def test_default_settings(spline):
    spline = spline
    assert '0' == spline.dxf.layer
    assert 256 == spline.dxf.color
    assert 'BYLAYER' == spline.dxf.linetype
    assert 1.0 == spline.dxf.ltscale
    assert 0 == spline.dxf.invisible
    assert (0.0, 0.0, 1.0) == spline.dxf.extrusion

    assert 0 == len(spline.get_knot_values())
    assert 0 == len(spline.get_weights())
    assert 0 == len(spline.get_control_points())
    assert 0 == len(spline.get_fit_points())


def test_start_tangent(spline):
    spline = spline
    spline.dxf.start_tangent = (1, 2, 3)
    assert (1, 2, 3) == spline.dxf.start_tangent


def test_end_tangent(spline):
    spline = spline
    spline.dxf.end_tangent = (4, 5, 6)
    assert (4, 5, 6) == spline.dxf.end_tangent


def test_knot_values(spline):
    spline = spline
    values = [1, 2, 3, 4, 5, 6, 7]
    spline.set_knot_values(values)
    assert 7 == spline.dxf.n_knots
    assert values == spline.get_knot_values()


def test_knots_ctx_manager(spline):
    spline = spline
    values = [1, 2, 3, 4, 5, 6, 7]
    spline.set_knot_values(values)
    with spline.edit_data() as data:
        data.knot_values.extend([8, 9])
    assert [1, 2, 3, 4, 5, 6, 7, 8, 9] == spline.get_knot_values()


def test_weights(spline):
    spline = spline
    weights = [1, 2, 3, 4, 5, 6, 7]
    spline.set_weights(weights)
    assert weights == spline.get_weights()


def test_weights_ctx_manager(spline):
    spline = spline
    values = [1, 2, 3, 4, 5, 6, 7]
    spline.set_weights(values)
    with spline.edit_data() as data:
        data.weights.extend([8, 9])
    assert [1, 2, 3, 4, 5, 6, 7, 8, 9] == spline.get_weights()


def test_control_points(spline):
    spline = spline
    points = [(1, 2, 3), (4, 5, 6), (7, 8, 9)]
    spline.set_control_points(points)
    assert 3 == spline.dxf.n_control_points
    assert points == spline.get_control_points()


def test_fit_points(spline):
    spline = spline
    points = [(1, 2, 3), (4, 5, 6), (7, 8, 9)]
    spline.set_fit_points(points)
    assert 3 == spline.dxf.n_fit_points
    assert points == spline.get_fit_points()
