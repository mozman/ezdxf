#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf
from ezdxf.lldxf import const
from ezdxf.math import (
    required_fit_points, required_control_points,
    required_knot_values, uniform_knot_vector,
)
from ezdxf.audit import Auditor, AuditError


@pytest.fixture(scope='module')
def doc():
    return ezdxf.new()


@pytest.fixture
def auditor(doc):
    return Auditor(doc)


@pytest.fixture
def spline(doc):
    msp = doc.modelspace()
    return msp.add_spline()


@pytest.mark.parametrize('order, expected', [
    (0, 2), (1, 2), (2, 2), (3, 3), (4, 4), (5, 5)
])
def test_required_fit_points_without_given_end_tangents(order, expected):
    assert required_fit_points(order, tangents=False) == expected


@pytest.mark.parametrize('order, expected', [
    (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 3)
])
def test_required_fit_points_with_given_end_tangents(order, expected):
    assert required_fit_points(order, tangents=True) == expected


@pytest.mark.parametrize('order, expected', [
    (0, 2), (1, 2), (2, 2), (3, 3), (4, 4),
])
def test_required_control_points_calculation(order, expected):
    assert required_control_points(order) == expected


def test_any_points_present(auditor, spline):
    spline.audit(auditor)
    assert len(auditor.fixes) == 1
    assert auditor.fixes[0].code == AuditError.INVALID_SPLINE_DEFINITION

    # Test if invalid spline will be destroyed:
    auditor.empty_trashcan()
    assert spline.is_alive is False


def test_degree_of_spline(auditor, spline):
    # Attribute validator prevents setting an invalid degree:
    with pytest.raises(const.DXFValueError):
        spline.dxf.degree = 0

    # But could be loaded from DXF file:
    # Hack to test entity validator for degree < 1
    spline.dxf.__dict__['degree'] = 0
    spline.audit(auditor)
    assert len(auditor.fixes) == 1
    assert auditor.fixes[0].code == AuditError.INVALID_SPLINE_DEFINITION

    # Test if invalid spline will be destroyed:
    auditor.empty_trashcan()
    assert spline.is_alive is False


def add_n_fit_points(s, count: int):
    for x in range(count):
        s.fit_points.append([x, 0, 0])


class TestFitPoints:

    @pytest.mark.parametrize('degree', [1, 2, 3, 4])
    def test_if_fit_point_count_is_valid(self, auditor, spline, degree):
        order = degree + 1
        spline.dxf.degree = degree
        add_n_fit_points(spline, required_fit_points(order, tangents=True) - 1)

        spline.audit(auditor)
        assert len(auditor.fixes) == 1
        assert auditor.fixes[
                   0].code == AuditError.INVALID_SPLINE_FIT_POINT_COUNT

        # Test if invalid spline will be destroyed:
        auditor.empty_trashcan()
        assert spline.is_alive is False

    def test_remove_unused_knot_values(self, auditor, spline):
        add_n_fit_points(spline, 4)
        # Add arbitrary knot values -- have no meaning for splines defined
        # by fit points:
        spline.knots = [1, 2, 3, 4]
        spline.audit(auditor)
        assert len(auditor.fixes) == 1
        assert auditor.fixes[0].code == \
               AuditError.INVALID_SPLINE_KNOT_VALUE_COUNT
        assert len(spline.knots) == 0

        # Spline is usable, test if spline will not be destroyed:
        auditor.empty_trashcan()
        assert spline.is_alive is True

    def test_remove_unused_weights(self, auditor, spline):
        add_n_fit_points(spline, 4)
        # Add arbitrary weights -- have no meaning for splines defined by fit
        # points:
        spline.weights = [1, 2, 2, 1]
        spline.audit(auditor)
        assert len(auditor.fixes) == 1
        assert auditor.fixes[0].code == AuditError.INVALID_SPLINE_WEIGHT_COUNT
        assert len(spline.weights) == 0

        # Spline is usable, test if spline will not be destroyed:
        auditor.empty_trashcan()
        assert spline.is_alive is True


def add_n_control_points(s, count: int):
    for x in range(count):
        s.control_points.append([x, 0, 0])


class TestControlPoints:
    @pytest.mark.parametrize('degree', [1, 2, 3, 4])
    def test_auditing_control_point_count(self, auditor, spline, degree):
        order = degree + 1
        spline.dxf.degree = degree
        add_n_control_points(spline, required_control_points(order) - 1)

        spline.audit(auditor)
        assert len(auditor.fixes) == 1
        assert auditor.fixes[0].code == \
               AuditError.INVALID_SPLINE_CONTROL_POINT_COUNT

        # Test if invalid spline will be destroyed:
        auditor.empty_trashcan()
        assert spline.is_alive is False

    @pytest.mark.parametrize('degree', [1, 2, 3, 4])
    def test_auditing_knot_value_count(self, auditor, spline, degree):
        order = degree + 1
        spline.dxf.degree = degree
        add_n_control_points(spline, required_control_points(order))
        spline.knots = [1, 2, 3]

        spline.audit(auditor)
        assert len(auditor.fixes) == 1
        assert auditor.fixes[0].code == \
               AuditError.INVALID_SPLINE_KNOT_VALUE_COUNT

        # Test if invalid spline will be destroyed:
        auditor.empty_trashcan()
        assert spline.is_alive is False

    @pytest.mark.parametrize('degree', [1, 2, 3, 4])
    def test_auditing_weight_count(self, auditor, spline, degree):
        order = degree + 1
        spline.dxf.degree = degree
        count = required_control_points(order)
        add_n_control_points(spline, count)
        spline.knots = uniform_knot_vector(count, order)
        spline.weights = range(count - 1)

        spline.audit(auditor)
        assert len(auditor.fixes) == 1
        assert auditor.fixes[0].code == \
               AuditError.INVALID_SPLINE_WEIGHT_COUNT

        # Test if invalid spline will be destroyed:
        auditor.empty_trashcan()
        assert spline.is_alive is False


if __name__ == '__main__':
    pytest.main([__file__])
