# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
import math
from ezdxf.math import Matrix44, Vec3, Z_AXIS, arc_angle_span_deg
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
        assert ocs.transform_thickness(thickness) == pytest.approx(
            -thickness
        ), "thickness value should be inverted"

    @pytest.mark.parametrize("thickness", [-2, 0, +2])
    def test_reflection_in_y_axis(self, thickness):
        ocs = OCSTransform(Z_AXIS, Matrix44.scale(1, -2, 1))
        assert ocs.new_ocs.uz.isclose(-Z_AXIS)  # flip extrusion vector
        assert ocs.transform_thickness(thickness) == pytest.approx(
            -thickness
        ), "thickness value should be inverted"

    @pytest.mark.parametrize("thickness", [-2, 0, +2])
    def test_reflection_in_z_axis(self, thickness):
        ocs = OCSTransform(Z_AXIS, Matrix44.scale(1, 1, -2))
        assert ocs.new_ocs.uz.isclose(Z_AXIS)  # extrusion vector unchanged
        assert ocs.transform_thickness(thickness) == pytest.approx(
            -2 * thickness
        ), "thickness value should be -2x"

    @pytest.mark.parametrize("thickness", [-2, 0, +2])
    def test_reflection_in_x_and_y_axis(self, thickness):
        ocs = OCSTransform(Z_AXIS, Matrix44.scale(-2, -2, 1))
        assert ocs.new_ocs.uz.isclose(Z_AXIS)  # extrusion vector unchanged
        assert ocs.transform_thickness(thickness) == pytest.approx(
            thickness
        ), "thickness value should be unchanged"

    @pytest.mark.parametrize("thickness", [-2, 0, +2])
    def test_reflection_in_x_and_z_axis(self, thickness):
        ocs = OCSTransform(Z_AXIS, Matrix44.scale(-2, 1, -2))
        assert ocs.new_ocs.uz.isclose(-Z_AXIS)  # flipped extrusion vector
        assert ocs.transform_thickness(thickness) == pytest.approx(
            2 * thickness
        ), "thickness value should be 2x"

    @pytest.mark.parametrize("thickness", [-2, 0, +2])
    def test_reflection_in_y_and_z_axis(self, thickness):
        ocs = OCSTransform(Z_AXIS, Matrix44.scale(1, -2, -2))
        assert ocs.new_ocs.uz.isclose(-Z_AXIS)  # flipped extrusion vector
        assert ocs.transform_thickness(thickness) == pytest.approx(
            2 * thickness
        ), "thickness value should be 2x"

    @pytest.mark.parametrize("thickness", [-2, 0, +2])
    def test_reflection_in_x_y_and_z_axis(self, thickness):
        ocs = OCSTransform(Z_AXIS, Matrix44.scale(-2, -2, -2))
        assert ocs.new_ocs.uz.isclose(Z_AXIS)  # unchanged extrusion vector
        assert ocs.transform_thickness(thickness) == pytest.approx(
            -2 * thickness
        ), "thickness value should be -2x"


class TestTransformWidth:
    @pytest.mark.parametrize("width", [-2, 0, +2])
    def test_no_transformation(self, width):
        ocs = OCSTransform(Z_AXIS, Matrix44())
        assert ocs.transform_width(width) == pytest.approx(abs(width))

    @pytest.mark.parametrize("width", [-2, 0, +2])
    def test_uniform_scaling_for_all_axis(self, width):
        ocs = OCSTransform(Z_AXIS, Matrix44.scale(-2, -2, -2))
        assert ocs.transform_width(width) == pytest.approx(
            2 * abs(width)
        ), "width should always be >= 0"

    @pytest.mark.parametrize("width", [-2, 0, +2])
    def test_x_scaling(self, width):
        ocs = OCSTransform(Z_AXIS, Matrix44.scale(2, 1, 1))
        assert ocs.transform_width(width) == pytest.approx(
            2 * abs(width)
        ), "current implementation scales by biggest x- or y-axis factor"

    @pytest.mark.parametrize("width", [-2, 0, +2])
    def test_y_scaling(self, width):
        ocs = OCSTransform(Z_AXIS, Matrix44.scale(1, 2, 1))
        assert ocs.transform_width(width) == pytest.approx(
            2 * abs(width)
        ), "current implementation scales by biggest x- or y-axis factor"

    @pytest.mark.parametrize("width", [-2, 0, +2])
    def test_non_uniform_xy_scaling_for_x(self, width):
        ocs = OCSTransform(Z_AXIS, Matrix44.scale(-3, -2, 1))
        assert ocs.transform_width(width) == pytest.approx(
            3 * abs(width)
        ), "current implementation scales by biggest x- or y-axis factor"

    @pytest.mark.parametrize("width", [-2, 0, +2])
    def test_non_uniform_xy_scaling_for_y(self, width):
        ocs = OCSTransform(Z_AXIS, Matrix44.scale(-2, -3, 1))
        assert ocs.transform_width(width) == pytest.approx(
            3 * abs(width)
        ), "current implementation scales by biggest x- or y-axis factor"


TEST_ANGLES = [
    (0, 0),
    (0, 90),
    (0, 180),
    (0, 360),
    (0, 0),
    (0, -90),
    (0, -180),
]


def normalize_angles(s, e):
    s = s % 360.0
    e = e % 360.0
    while e < s:
        e += 360
    return s, e


class TestTransformCCWAngles:
    @pytest.mark.parametrize("s,e", TEST_ANGLES)
    def test_no_transformation(self, s, e):
        ocs = OCSTransform(Z_AXIS, Matrix44())
        assert ocs.transform_ccw_arc_angles_deg(s, e) == pytest.approx([s, e])

    @pytest.mark.parametrize("s,e", TEST_ANGLES)
    @pytest.mark.parametrize(
        "rotation", [45, 90, 180, 270, -45, -90, -180]
    )
    def test_rotation(self, s, e, rotation):
        ocs = OCSTransform(Z_AXIS, Matrix44.z_rotate(math.radians(rotation)))
        new_angles = normalize_angles(*ocs.transform_ccw_arc_angles_deg(s, e))
        assert new_angles == pytest.approx(
            normalize_angles(s + rotation, e + rotation)
        )

    @pytest.mark.parametrize("s,e", TEST_ANGLES)
    @pytest.mark.parametrize(
        "rotation", [45, 90, 180, 270, -45, -90, -180, -270]
    )
    @pytest.mark.parametrize(
        "sx,sy",
        [(-1, 1), (1, -1), (-1, -1)],
        ids=["x", "y", "xy"],
    )
    def test_reflections(self, s, e, rotation, sx, sy):
        m = Matrix44.chain(
            Matrix44.scale(sx, sy, 1),
            Matrix44.z_rotate(rotation),
        )
        expected_start = m.transform(Vec3.from_deg_angle(s))
        expected_end = m.transform(Vec3.from_deg_angle(e))
        expected_angle_span = arc_angle_span_deg(s, e)

        ocs = OCSTransform(Z_AXIS, m)
        new_s, new_e = ocs.transform_ccw_arc_angles_deg(s, e)
        wcs_start = ocs.new_ocs.to_wcs(Vec3.from_deg_angle(new_s))
        wcs_end = ocs.new_ocs.to_wcs(Vec3.from_deg_angle(new_e))
        assert arc_angle_span_deg(new_s, new_e) == pytest.approx(
            expected_angle_span
        )
        assert wcs_start.isclose(expected_start)
        assert wcs_end.isclose(expected_end)


if __name__ == "__main__":
    pytest.main([__file__])
