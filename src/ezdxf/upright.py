# Copyright (c) 2021, Manfred Moitzi
# License: MIT License

from ezdxf.math import Z_AXIS, Vec3, OCS, OCSTransform, Matrix44
from ezdxf.entities import DXFGraphic, DXFNamespace

__all__ = ["upright"]

FLIPPED_Z_AXIS = -Z_AXIS
TRANSFORMER = OCSTransform.from_ocs(
    OCS(FLIPPED_Z_AXIS),
    OCS(Z_AXIS),
    Matrix44(),
)


def _flip_thickness(dxf: DXFNamespace) -> None:
    if dxf.hasattr("thickness"):
        dxf.thickness = TRANSFORMER.transform_thickness(dxf.thickness)


def _flip_circle(dxf: DXFNamespace) -> None:
    dxf.center = TRANSFORMER.transform_vertex(dxf.center)
    _flip_thickness(dxf)
    dxf.discard("extrusion")


def _flip_arc(dxf: DXFNamespace) -> None:
    _flip_circle(dxf)
    s, e = TRANSFORMER.transform_ccw_arc_angles_deg(
        dxf.start_angle, dxf.end_angle
    )
    dxf.start_angle = s
    dxf.end_angle = e


UPRIGHT_TOOLS = {
    "CIRCLE": _flip_circle,
    "ARC": _flip_arc,
}


def upright(entity: DXFGraphic) -> None:
    """Flips an inverted :ref:`OCS` defined by extrusion vector (0, 0, -1) into
    a :ref:`WCS` aligned :ref:`OCS` defined by extrusion vector (0, 0, 1).
    DXF entities with other extrusion vectors and unsupported DXF entities will
    be silently ignored.

    Supported DXF entities:

    - CIRCLE
    - ARC

    """
    if not entity.dxf.hasattr("extrusion"):
        return
    extrusion = Vec3(entity.dxf.extrusion).normalize()
    if not extrusion.isclose(FLIPPED_Z_AXIS):
        return
    tool = UPRIGHT_TOOLS.get(entity.dxftype())
    if tool:
        tool(entity.dxf)
