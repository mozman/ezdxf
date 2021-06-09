# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
import math
from ezdxf.math import Matrix44, Vec3, Z_AXIS
from ezdxf.math.transformtools import OCSTransform


def test_transform_angle_without_ocs():
    ocs = OCSTransform(Vec3(0, 0, 1), Matrix44.z_rotate(math.pi / 2))
    assert math.isclose(ocs.transform_angle(0), math.pi / 2)


def test_transform_length_without_ocs():
    ocs = OCSTransform(Z_AXIS, Matrix44.scale(2, 3, 4))
    assert math.isclose(ocs.transform_length((2, 0, 0)), 2 * 2)
    assert math.isclose(ocs.transform_length((0, 2, 0)), 2 * 3)
    assert math.isclose(ocs.transform_length((0, 0, 2)), 2 * 4)


class TestTransformThickness:
    @pytest.mark.parametrize("thickness", [-2, 0, +2])
    def test_no_transformation(self, thickness):
        ocs = OCSTransform(Z_AXIS, Matrix44())
        assert ocs.transform_thickness(thickness) == pytest.approx(thickness)

    @pytest.mark.parametrize("thickness", [-2, 0, +2])
    def test_reflection_in_x_axis(self, thickness):
        ocs = OCSTransform(Z_AXIS, Matrix44.scale(-2, 1, 1))
        assert ocs.new_ocs.uz.isclose(-Z_AXIS)  # flip extrusion vector
        assert (
            ocs.transform_thickness(thickness) == pytest.approx(-thickness)
        ), "thickness value should be inverted"

    @pytest.mark.parametrize("thickness", [-2, 0, +2])
    def test_reflection_in_y_axis(self, thickness):
        ocs = OCSTransform(Z_AXIS, Matrix44.scale(1, -2, 1))
        assert ocs.new_ocs.uz.isclose(-Z_AXIS)  # flip extrusion vector
        assert (
            ocs.transform_thickness(thickness) == pytest.approx(-thickness)
        ), "thickness value should be inverted"

    @pytest.mark.parametrize("thickness", [-2, 0, +2])
    def test_reflection_in_z_axis(self, thickness):
        ocs = OCSTransform(Z_AXIS, Matrix44.scale(1, 1, -2))
        assert ocs.new_ocs.uz.isclose(Z_AXIS)  # extrusion vector unchanged
        assert (
            ocs.transform_thickness(thickness) == pytest.approx(-2 * thickness)
        ), "thickness value should be -2x"

    @pytest.mark.parametrize("thickness", [-2, 0, +2])
    def test_reflection_in_x_and_y_axis(self, thickness):
        ocs = OCSTransform(Z_AXIS, Matrix44.scale(-2, -2, 1))
        assert ocs.new_ocs.uz.isclose(Z_AXIS)  # extrusion vector unchanged
        assert (
            ocs.transform_thickness(thickness) == pytest.approx(thickness)
        ), "thickness value should be unchanged"

    @pytest.mark.parametrize("thickness", [-2, 0, +2])
    def test_reflection_in_x_and_z_axis(self, thickness):
        ocs = OCSTransform(Z_AXIS, Matrix44.scale(-2, 1, -2))
        assert ocs.new_ocs.uz.isclose(-Z_AXIS)  # flipped extrusion vector
        assert (
            ocs.transform_thickness(thickness) == pytest.approx(2 * thickness)
        ), "thickness value should be 2x"

    @pytest.mark.parametrize("thickness", [-2, 0, +2])
    def test_reflection_in_y_and_z_axis(self, thickness):
        ocs = OCSTransform(Z_AXIS, Matrix44.scale(1, -2, -2))
        assert ocs.new_ocs.uz.isclose(-Z_AXIS)  # flipped extrusion vector
        assert (
            ocs.transform_thickness(thickness) == pytest.approx(2 * thickness)
        ), "thickness value should be 2x"

    @pytest.mark.parametrize("thickness", [-2, 0, +2])
    def test_reflection_in_x_y_and_z_axis(self, thickness):
        ocs = OCSTransform(Z_AXIS, Matrix44.scale(-2, -2, -2))
        assert ocs.new_ocs.uz.isclose(Z_AXIS)  # unchanged extrusion vector
        assert (
            ocs.transform_thickness(thickness) == pytest.approx(-2 * thickness)
        ), "thickness value should be -2x"


if __name__ == '__main__':
    pytest.main([__file__])
