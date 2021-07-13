# Copyright (c) 2021, Manfred Moitzi
# License: MIT License
from typing import Iterable
from ezdxf.math import Z_AXIS, Vec3, OCS, Vertex
from ezdxf.entities import DXFGraphic, DXFNamespace

__all__ = ["upright", "upright_all"]


def upright(entity: DXFGraphic) -> None:
    """Flips an inverted :ref:`OCS` defined by extrusion vector (0, 0, -1) into
    a :ref:`WCS` aligned :ref:`OCS` defined by extrusion vector (0, 0, 1).
    DXF entities with other extrusion vectors and unsupported DXF entities will
    be silently ignored.

    .. warning::

        The WCS representation as :class:`~ezdxf.path.Path` objects is the same
        overall but not always 100% identical, the orientation or the starting
        points of curves can be different.

        E.g. arc angles are always counter-clockwise oriented around the
        extrusion vector, therefore flipping the extrusion vector creates a
        similar but not a 100% identical arc.

    Supported DXF entities:

    - CIRCLE
    - ARC

    """
    # A mirrored text represented by an extrusion vector (0, 0, -1) cannot
    # represented by an extrusion vector (0, 0, 1), therefore this CANNOT work
    # for text entities or entities including text:
    # TEXT, ATTRIB, ATTDEF, MTEXT, DIMENSION, LEADER, MLEADER
    if not (
        isinstance(entity, DXFGraphic)
        and entity.is_alive
        and entity.dxf.hasattr("extrusion")
    ):
        return
    extrusion = Vec3(entity.dxf.extrusion).normalize()
    if not extrusion.isclose(FLIPPED_Z_AXIS):
        return
    simple_tool = SIMPLE_UPRIGHT_TOOLS.get(entity.dxftype())
    if simple_tool:
        simple_tool(entity.dxf)
    else:
        complex_tool = COMPLEX_UPRIGHT_TOOLS.get(entity.dxftype())
        if complex_tool:
            complex_tool(entity)


def upright_all(entities: Iterable[DXFGraphic]) -> None:
    """Call function :func:`upright` for all DXF entities in iterable
    `entities`::

        upright_all(doc.modelspace())

    """
    for e in entities:
        upright(e)


FLIPPED_Z_AXIS = -Z_AXIS
FLIPPED_OCS = OCS(FLIPPED_Z_AXIS)


def _flip_deg_angle(angle: float) -> float:
    return 180.0 - angle if angle >= 0.0 else -180.0 - angle


def _flip_vertex(vertex: Vertex) -> Vertex:
    return FLIPPED_OCS.to_wcs(vertex)


def _flip_thickness(dxf: DXFNamespace) -> None:
    if dxf.hasattr("thickness"):
        dxf.thickness = -dxf.thickness


def _flip_circle(dxf: DXFNamespace) -> None:
    dxf.center = _flip_vertex(dxf.center)
    _flip_thickness(dxf)
    dxf.discard("extrusion")


def _flip_arc(dxf: DXFNamespace) -> None:
    _flip_circle(dxf)
    end_angle = dxf.end_angle
    dxf.end_angle = _flip_deg_angle(dxf.start_angle)
    dxf.start_angle = _flip_deg_angle(end_angle)


# All properties stored as DXF attributes
SIMPLE_UPRIGHT_TOOLS = {
    "CIRCLE": _flip_circle,
    "ARC": _flip_arc,
    "SOLID": None,
    "TRACE": None,
    "ELLIPSE": None,  # WCS entity!
}


def _flip_complex_entity(entity: DXFGraphic) -> None:
    pass


# Additional vertices or paths to transform
COMPLEX_UPRIGHT_TOOLS = {
    "LWPOLYLINE": _flip_complex_entity,
    "POLYLINE": None,  # only 2D POLYLINE
    "POLYGON": None,  # HATCH, MPOLYGON
    "INSERT": None,
}
