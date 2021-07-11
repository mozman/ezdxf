# Copyright (c) 2020-2021, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Tuple
import math
from ezdxf.math import (
    Vec3,
    Vec2,
    X_AXIS,
    Y_AXIS,
    Z_AXIS,
    Matrix44,
    sign,
    OCS,
    arc_angle_span_deg,
    ellipse_param_span,
)

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFGraphic, Vertex

__all__ = [
    "TransformError",
    "NonUniformScalingError",
    "InsertTransformationError",
    "transform_extrusion",
    "transform_thickness_and_extrusion_without_ocs",
    "OCSTransform",
]

_FLIPPED_Z_AXIS = Vec3(0, 0, -1)
_PLACEHOLDER_OCS = OCS()


class TransformError(Exception):
    pass


class NonUniformScalingError(TransformError):
    pass


class InsertTransformationError(TransformError):
    pass


def transform_thickness_and_extrusion_without_ocs(
    entity: "DXFGraphic", m: Matrix44
) -> None:
    if entity.dxf.hasattr("thickness"):
        thickness = entity.dxf.thickness
        reflection = sign(thickness)
        thickness = m.transform_direction(entity.dxf.extrusion * thickness)
        entity.dxf.thickness = thickness.magnitude * reflection
        entity.dxf.extrusion = thickness.normalize()
    elif entity.dxf.hasattr("extrusion"):  # without thickness?
        extrusion = m.transform_direction(entity.dxf.extrusion)
        entity.dxf.extrusion = extrusion.normalize()


def transform_extrusion(extrusion: "Vertex", m: Matrix44) -> Tuple[Vec3, bool]:
    """Transforms the old `extrusion` vector into a new extrusion vector.
    Returns the new extrusion vector and a boolean value: ``True`` if the new
    OCS established by the new extrusion vector has a uniform scaled xy-plane,
    else ``False``.

    The new extrusion vector is perpendicular to plane defined by the
    transformed x- and y-axis.

    Args:
        extrusion: extrusion vector of the old OCS
        m: transformation matrix

    Returns:

    """
    ocs = OCS(extrusion)
    ocs_x_axis_in_wcs = ocs.to_wcs(X_AXIS)
    ocs_y_axis_in_wcs = ocs.to_wcs(Y_AXIS)
    x_axis, y_axis = m.transform_directions(
        (ocs_x_axis_in_wcs, ocs_y_axis_in_wcs)
    )

    # Check for uniform scaled xy-plane:
    is_uniform = math.isclose(
        x_axis.magnitude_square, y_axis.magnitude_square, abs_tol=1e-9
    )
    new_extrusion = x_axis.cross(y_axis).normalize()
    # TODO: Avoid flipped extrusion vector (0, 0, -1)?
    # if new_extrusion.isclose(_FLIPPED_Z_AXIS):
    #    return Z_AXIS, is_uniform
    # else:
    #    return new_extrusion, is_uniform
    #
    # Current state: 91 tests fail, including explicit tests for an expected
    # extrusion vector of (0, 0, 1) or (0, 0, -1).
    return new_extrusion, is_uniform


class OCSTransform:
    def __init__(self, extrusion: Vec3 = None, m: Matrix44 = None):
        if m is None:
            self.m = Matrix44()
        else:
            self.m = m
        self.scale_uniform: bool = True
        if extrusion is None:  # fill in dummy values
            self._reset_ocs(_PLACEHOLDER_OCS, _PLACEHOLDER_OCS, True)
        else:
            new_extrusion, scale_uniform = transform_extrusion(extrusion, m)
            self._reset_ocs(OCS(extrusion), OCS(new_extrusion), scale_uniform)

    def _reset_ocs(
        self, old_ocs: OCS, new_ocs: OCS, scale_uniform: bool
    ) -> None:
        self.old_ocs = old_ocs
        self.new_ocs = new_ocs
        self.scale_uniform = scale_uniform

    @property
    def old_extrusion(self) -> Vec3:
        return self.old_ocs.uz

    @property
    def new_extrusion(self) -> Vec3:
        return self.new_ocs.uz

    @classmethod
    def from_ocs(
        cls, old: OCS, new: OCS, m: Matrix44, scale_uniform=True
    ) -> "OCSTransform":
        ocs = cls(m=m)
        ocs._reset_ocs(old, new, scale_uniform)
        return ocs

    def transform_length(self, length: "Vertex", reflection=1.0) -> float:
        """Returns magnitude of `length` direction vector transformed from
        old OCS into new OCS including `reflection` correction applied.
        """
        return self.m.transform_direction(
            self.old_ocs.to_wcs(length)
        ).magnitude * sign(reflection)

    def transform_width(self, width: float) -> float:
        """Transform the width of a linear OCS entity from the old OCS
        into the new OCS. (LWPOLYLINE!)
        """
        abs_width = abs(width)
        if abs_width > 1e-12:  # assume a uniform scaling!
            return max(
                self.transform_length((abs_width, 0, 0)),
                self.transform_length((0, abs_width, 0)),
            )
        return 0.0

    transform_scale_factor = transform_length

    def transform_ocs_direction(self, direction: Vec3) -> Vec3:
        """Transform an OCS direction from the old OCS into the new OCS."""
        # OCS origin is ALWAYS the WCS origin!
        old_wcs_direction = self.old_ocs.to_wcs(direction)
        new_wcs_direction = self.m.transform_direction(old_wcs_direction)
        return self.new_ocs.from_wcs(new_wcs_direction)

    def transform_thickness(self, thickness: float) -> float:
        """Transform the thickness attribute of an OCS entity from the old OCS
        into the new OCS.

        Thickness is always applied in the z-axis direction of the OCS
        a.k.a. extrusion vector.

        """
        # Only the z-component of the thickness vector transformed into the
        # new OCS is relevant for the extrusion in the direction of the new
        # OCS z-axis.
        # Input and output thickness can be negative!
        new_ocs_thickness = self.transform_ocs_direction(Vec3(0, 0, thickness))
        return new_ocs_thickness.z

    def transform_vertex(self, vertex: "Vertex") -> Vec3:
        """Returns vertex transformed from old OCS into new OCS."""
        return self.new_ocs.from_wcs(
            self.m.transform(self.old_ocs.to_wcs(vertex))
        )

    def transform_2d_vertex(self, vertex: "Vertex", elevation: float) -> Vec2:
        """Returns 2D vertex transformed from old OCS into new OCS."""
        v = Vec3(vertex).replace(z=elevation)
        return Vec2(
            self.new_ocs.from_wcs(self.m.transform(self.old_ocs.to_wcs(v)))
        )

    def transform_direction(self, direction: "Vertex") -> Vec3:
        """Returns direction transformed from old OCS into new OCS."""
        return self.new_ocs.from_wcs(
            self.m.transform_direction(self.old_ocs.to_wcs(direction))
        )

    def transform_angle(self, angle: float) -> float:
        """Returns angle (in radians) from old OCS transformed into new OCS."""
        return self.transform_direction(Vec3.from_angle(angle)).angle

    def transform_deg_angle(self, angle: float) -> float:
        """Returns angle (in degrees) from old OCS transformed into new OCS."""
        return math.degrees(self.transform_angle(math.radians(angle)))

    def transform_ccw_arc_angles(
        self, start: float, end: float
    ) -> Tuple[float, float]:
        """Returns arc start- and end angle (in radians) from old OCS
        transformed into new OCS in counter-clockwise orientation.
        """
        old_angle_span = ellipse_param_span(start, end)  # always >= 0
        new_start = self.transform_angle(start)
        new_end = self.transform_angle(end)
        if math.isclose(old_angle_span, math.pi):  # semicircle
            old_angle_span = 1.0  # arbitrary angle span
            check = self.transform_angle(start + old_angle_span)
            new_angle_span = ellipse_param_span(new_start, check)
        elif math.isclose(old_angle_span, math.tau):
            # preserve full circle span
            return new_start, new_start + math.tau
        else:
            new_angle_span = ellipse_param_span(new_start, new_end)

        if math.isclose(old_angle_span, new_angle_span):
            return new_start, new_end
        else:  # reversed angle orientation
            return new_end, new_start

    def transform_ccw_arc_angles_deg(
        self, start: float, end: float
    ) -> Tuple[float, float]:
        """Returns start- and end angle (in degrees) from old OCS transformed
        into new OCS in counter-clockwise orientation.
        """
        start, end = self.transform_ccw_arc_angles(
            math.radians(start), math.radians(end)
        )
        return math.degrees(start), math.degrees(end)
