# Created: 02.05.2020
# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Tuple
import math
from .matrix44 import Matrix44
from .vector import Vector
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
    ocs = OCS(extrusion)
    ocs_x_axis_in_wcs = ocs.to_wcs((1, 0, 0))
    ocs_y_axis_in_wcs = ocs.to_wcs((0, 1, 0))
    x_axis, y_axis = m.transform_directions((ocs_x_axis_in_wcs, ocs_y_axis_in_wcs))

    is_uniform = math.isclose(x_axis.magnitude_square, y_axis.magnitude_square, abs_tol=1e-9)
    new_extrusion = x_axis.cross(y_axis).normalize()
    return new_extrusion, is_uniform


def transform_length(v: 'Vertex', ocs: OCS, m: Matrix44) -> float:
    direction_in_wcs = m.transform_direction(ocs.to_wcs(v))
    return direction_in_wcs.magnitude
