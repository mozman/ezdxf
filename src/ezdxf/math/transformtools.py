# Created: 02.05.2020
# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Tuple
import math
from .matrix44 import Matrix44
from .vector import Vector, X_AXIS, Y_AXIS
from .ucs import OCS

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFGraphic, Vertex


class TransformError(Exception):
    pass


class NonUniformScalingError(TransformError):
    pass


def transform_thickness_and_extrusion_without_ocs(entity: 'DXFGraphic', m: Matrix44) -> None:
    if entity.dxf.hasattr('thickness'):
        thickness = m.transform_direction(entity.dxf.extrusion * entity.dxf.thickness)
        entity.dxf.thickness = thickness.magnitude
        entity.dxf.extrusion = thickness.normalize()
    elif entity.dxf.hasattr('extrusion'):  # without thickness?
        extrusion = m.transform_direction(entity.dxf.extrusion)
        entity.dxf.extrusion = extrusion.normalize()


def transform_extrusion(extrusion: 'Vertex', m: Matrix44) -> Tuple[Vector, bool]:
    """
    Transforms the old `extrusion` vector into a new extrusion vector. Returns the new extrusion vector and a
    boolean value: ``True`` if the new OCS established by the new extrusion vector has a uniform scaled xy-plane,
    else ``False``.

    The new extrusion vector is perpendicular to plane defined by the transformed x- and y-axis.

    Args:
        extrusion: extrusion vector of the old OCS
        m: transformation matrix

    Returns:

    """
    ocs = OCS(extrusion)
    ocs_x_axis_in_wcs = ocs.to_wcs(X_AXIS)
    ocs_y_axis_in_wcs = ocs.to_wcs(Y_AXIS)
    x_axis, y_axis = m.transform_directions((ocs_x_axis_in_wcs, ocs_y_axis_in_wcs))

    # Not sure if this is the correct test for a uniform scaled xy-plane
    is_uniform = math.isclose(x_axis.magnitude_square, y_axis.magnitude_square, abs_tol=1e-9)
    new_extrusion = x_axis.cross(y_axis).normalize()
    return new_extrusion, is_uniform


class OCSTransform:
    def __init__(self, extrusion: Vector, m: Matrix44):
        self.m = m
        self.old_extrusion = extrusion
        self.old_ocs = OCS(extrusion)
        self.new_extrusion, self.scale_uniform = transform_extrusion(extrusion, m)
        self.new_ocs = OCS(self.new_extrusion)

    def transform_length(self, length: 'Vertex') -> float:
        """ Returns length of transformed `length` vector.

        Args:
            length: length vector in old OCS

        """
        return self.m.transform_direction(self.old_ocs.to_wcs(length)).magnitude

    transform_scale_factor = transform_length

    def transform_vertex(self, vertex: 'Vertex'):
        """ Returns vertex transformed from old OCS into new OCS by transformation matrix `m`.
        """
        return self.new_ocs.from_wcs(self.m.transform(self.old_ocs.to_wcs(vertex)))

    def transform_direction(self, direction: 'Vertex'):
        """ Returns direction transformed from old OCS into new OCS by transformation matrix `m`.
        """
        return self.new_ocs.from_wcs(self.m.transform_direction(self.old_ocs.to_wcs(direction)))

    def transform_angle(self, angle: float) -> float:
        """ Returns new angle in radians.

        Transform old `angle` from old OCS to a WCS vector, transforms this WCS vector by transformation matrix `m` and
        calculates the angle in the OCS established by the new `extrusion` vector between to the new OCS x-axis and the
        transformed angle vector.

        Args:
            angle: old angle in radians

        """
        new_angle_vec = self.m.transform_direction(self.old_ocs.to_wcs(Vector.from_angle(angle)))
        return self.new_extrusion.angle_about(X_AXIS, new_angle_vec)

    def transform_deg_angle(self, angle: float) -> float:
        return math.degrees(self.transform_angle(math.radians(angle)))
