# Created: 02.05.2020
# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Tuple
import math
from .matrix44 import Matrix44
from .construct2d import sign
from .vector import Vector, X_AXIS, Y_AXIS, Vec2
from .ucs import OCS

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFGraphic, Vertex


class TransformError(Exception):
    pass


class NonUniformScalingError(TransformError):
    pass


class InsertTransformationError(TransformError):
    pass


def transform_thickness_and_extrusion_without_ocs(entity: 'DXFGraphic', m: Matrix44) -> None:
    if entity.dxf.hasattr('thickness'):
        thickness = entity.dxf.thickness
        reflection = sign(thickness)
        thickness = m.transform_direction(entity.dxf.extrusion * thickness)
        entity.dxf.thickness = thickness.magnitude * reflection
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
    def __init__(self, extrusion: Vector = None, m: Matrix44 = None):
        self.m = m
        if extrusion is None:
            self.old_ocs = None
            self.scale_uniform = False
            self.new_ocs = None
        else:
            self.old_ocs = OCS(extrusion)
            new_extrusion, self.scale_uniform = transform_extrusion(extrusion, m)
            self.new_ocs = OCS(new_extrusion)

    @property
    def old_extrusion(self) -> Vector:
        return self.old_ocs.uz

    @property
    def new_extrusion(self) -> Vector:
        return self.new_ocs.uz

    @classmethod
    def from_ocs(cls, old: OCS, new: OCS, m: Matrix44) -> 'OCSTransform':
        ocs = cls()
        ocs.m = m
        ocs.old_ocs = old
        ocs.new_ocs = new
        return ocs

    def transform_length(self, length: 'Vertex', reflection=1.0) -> float:
        """ Returns magnitude of `length` direction vector transformed from
        old OCS into new OCS including `reflection` correction applied.
        """
        return self.m.transform_direction(self.old_ocs.to_wcs(length)).magnitude * sign(reflection)

    transform_scale_factor = transform_length

    def transform_vertex(self, vertex: 'Vertex') -> Vector:
        """ Returns vertex transformed from old OCS into new OCS. """
        return self.new_ocs.from_wcs(self.m.transform(self.old_ocs.to_wcs(vertex)))

    def transform_2d_vertex(self, vertex: 'Vertex', elevation: float) -> Vec2:
        """ Returns 2D vertex transformed from old OCS into new OCS. """
        v = Vector(vertex).replace(z=elevation)
        return self.new_ocs.from_wcs(self.m.transform(self.old_ocs.to_wcs(v))).vec2

    def transform_direction(self, direction: 'Vertex') -> Vector:
        """ Returns direction transformed from old OCS into new OCS. """
        return self.new_ocs.from_wcs(self.m.transform_direction(self.old_ocs.to_wcs(direction)))

    def transform_angle(self, angle: float) -> float:
        """ Returns angle (in radians) from old OCS transformed into new OCS.
        """
        return self.transform_direction(Vector.from_angle(angle)).angle % math.tau

    def transform_deg_angle(self, angle: float) -> float:
        """ Returns angle (in degrees) from old OCS transformed into new OCS.
        """
        return math.degrees(self.transform_angle(math.radians(angle))) % 360.0
