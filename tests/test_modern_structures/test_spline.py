# Created: 12.04.2014, 2018 rewritten for pytest
# Copyright (C) 2014-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import pytest
import ezdxf
from ezdxf.modern.spline import Spline, _SPLINE_TPL, tag_processor
from ezdxf.lldxf.extendedtags import ExtendedTags


@pytest.fixture
def spline():
    return Spline(tag_processor(ExtendedTags.from_text(_SPLINE_TPL)))


@pytest.fixture
def points():
    return [(1., 1., 0.), (2.5, 3., 0.), (4.5, 2., 0), (6.5, 4., 0)]


@pytest.fixture
def weights():
    return [1, 2, 3, 4]


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
    assert values == list(spline.get_knot_values())


def test_knots_ctx_manager(spline):
    spline = spline
    values = [1, 2, 3, 4, 5, 6, 7]
    spline.set_knot_values(values)
    with spline.edit_data() as data:
        data.knot_values.extend([8, 9])
    assert [1, 2, 3, 4, 5, 6, 7, 8, 9] == list(spline.get_knot_values())


def test_weights(spline):
    spline = spline
    weights = [1, 2, 3, 4, 5, 6, 7]
    spline.set_weights(weights)
    assert weights == list(spline.get_weights())


def test_weights_ctx_manager(spline):
    spline = spline
    values = [1, 2, 3, 4, 5, 6, 7]
    spline.set_weights(values)
    with spline.edit_data() as data:
        data.weights.extend([8, 9])
    assert [1, 2, 3, 4, 5, 6, 7, 8, 9] == list(spline.get_weights())


def test_control_points(spline, points):
    spline.set_control_points(points)
    assert spline.dxf.n_control_points == 4
    assert points == list(spline.get_control_points())


def test_fit_points(spline, points):
    spline.set_fit_points(points)
    assert spline.dxf.n_fit_points == 4
    assert points == list(spline.get_fit_points())


def test_set_open_uniform(spline, points):
    spline.set_open_uniform(points, degree=3)
    assert spline.dxf.degree == 3
    assert list(spline.get_control_points()) == points
    assert spline.dxf.n_control_points == len(points)
    assert spline.dxf.n_knots == len(points) + spline.dxf.degree + 1  # n + p + 2
    assert spline.closed is False


def test_set_uniform(spline, points):
    spline.set_uniform(points, degree=3)
    assert spline.dxf.degree == 3
    assert list(spline.get_control_points()) == points
    assert spline.dxf.n_control_points == len(points)
    assert spline.dxf.n_knots == len(points) + spline.dxf.degree + 1  # n + p + 2
    assert spline.closed is False


def test_set_periodic(spline, points):
    spline.set_periodic(points, degree=3)
    assert spline.dxf.degree == 3
    assert list(spline.get_control_points()) == points
    assert spline.dxf.n_control_points == len(points)
    assert spline.dxf.n_knots == len(points) + 1  # according the Autodesk developer documentation
    assert spline.closed is True


def test_set_open_rational(spline, points, weights):
    spline.set_open_rational(points, weights, degree=3)
    assert spline.dxf.degree == 3
    assert list(spline.get_control_points()) == points
    assert list(spline.get_weights()) == weights
    assert spline.dxf.n_control_points == len(points)
    assert len(spline.get_weights()) == len(points)
    assert spline.dxf.n_knots == len(points) + spline.dxf.degree + 1  # n + p + 2
    assert spline.closed is False


def test_set_uniform_rational(spline, points, weights):
    spline.set_uniform_rational(points, weights, degree=3)
    assert spline.dxf.degree == 3
    assert list(spline.get_control_points()) == points
    assert list(spline.get_weights()) == weights
    assert spline.dxf.n_control_points == len(points)
    assert len(spline.get_weights()) == len(points)
    assert spline.dxf.n_knots == len(points) + spline.dxf.degree + 1  # n + p + 2
    assert spline.closed is False


def test_set_periodic_rational(spline, points, weights):
    spline.set_periodic_rational(points, weights, degree=3)
    assert spline.dxf.degree == 3
    assert list(spline.get_control_points()) == points
    assert list(spline.get_weights()) == weights
    assert spline.dxf.n_control_points == len(points)
    assert len(spline.get_weights()) == len(points)
    assert spline.dxf.n_knots == len(points) + 1  # according the Autodesk developer documentation
    assert spline.closed is True


@pytest.fixture(scope='module')
def msp():
    dwg = ezdxf.new('R2000')
    return dwg.modelspace()


def test_open_spline(msp, points):
    spline = msp.add_open_spline(points, degree=3)
    assert spline.dxf.degree == 3
    assert list(spline.get_control_points()) == points
    assert spline.dxf.n_control_points == len(points)
    assert spline.dxf.n_knots == len(points) + spline.dxf.degree + 1  # n + p + 2
    assert spline.closed is False


def test_closed_spline(msp, points):
    spline = msp.add_closed_spline(points, degree=3)
    assert spline.dxf.degree == 3
    assert list(spline.get_control_points()) == points
    assert spline.dxf.n_control_points == len(points)
    assert spline.dxf.n_knots == len(points) + 1  # according the Autodesk developer documentation
    assert spline.closed is True


def test_open_rational_spline(msp, points, weights):
    spline = msp.add_rational_spline(points, weights, degree=3)
    assert spline.dxf.degree == 3
    assert list(spline.get_control_points()) == points
    assert list(spline.get_weights()) == weights
    assert spline.dxf.n_control_points == len(points)
    assert len(spline.get_weights()) == len(points)
    assert spline.dxf.n_knots == len(points) + spline.dxf.degree + 1  # n + p + 2
    assert spline.closed is False


def test_closed_rational_spline(msp, points, weights):
    spline = msp.add_closed_rational_spline(points, weights, degree=3)
    assert spline.dxf.degree == 3
    assert list(spline.get_control_points()) == points
    assert list(spline.get_weights()) == weights
    assert spline.dxf.n_control_points == len(points)
    assert len(spline.get_weights()) == len(points)
    assert spline.dxf.n_knots == len(points) + 1  # according the Autodesk developer documentation
    assert spline.closed is True
