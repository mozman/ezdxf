# Created: 02.05.2020
# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Tuple
import math
from .matrix44 import Matrix44, sign
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
        thickness = entity.dxf.thickness
        reflexion = sign(thickness)
        thickness = m.transform_direction(entity.dxf.extrusion * thickness)
        entity.dxf.thickness = thickness.magnitude * reflexion
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

    def set_new_ocs(self, extrusion: 'Vertex'):
        self.new_extrusion = Vector(extrusion)
        self.new_ocs = OCS(self.new_extrusion)

    def transform_length(self, length: 'Vertex', reflexion=1.0) -> float:
        """ Returns magnitude of `length` direction vector transformed from
        old OCS into new OCS including `reflexion` correction applied.
        """
        return self.m.transform_direction(self.old_ocs.to_wcs(length)).magnitude * sign(reflexion)

    transform_scale_factor = transform_length

    def transform_vertex(self, vertex: 'Vertex'):
        """ Returns vertex transformed from old OCS into new OCS.
        """
        return self.new_ocs.from_wcs(self.m.transform(self.old_ocs.to_wcs(vertex)))

    def transform_2d_vertex(self, vertex: 'Vertex', elevation: float):
        """ Returns 2d vertex transformed from old OCS into new OCS.
        """
        v = Vector(vertex).replace(z=elevation)
        return self.new_ocs.from_wcs(self.m.transform(self.old_ocs.to_wcs(v))).vec2

    def transform_direction(self, direction: 'Vertex'):
        """ Returns direction transformed from old OCS into new OCS.
        """
        return self.new_ocs.from_wcs(self.m.transform_direction(self.old_ocs.to_wcs(direction)))

    def transform_angle(self, angle: float) -> float:
        """ Returns angle (in radians) from old OCS transformed into new OCS.
        """
        return self.transform_direction(Vector.from_angle(angle)).angle % math.tau

    def transform_deg_angle(self, angle: float) -> float:
        """ Returns angle (in degrees) from old OCS transformed into new OCS.
        """
        return math.degrees(self.transform_angle(math.radians(angle)))
