# Copyright (c) 2021, Manfred Moitzi
# License: MIT License
#
# Purpose:
# Flips an inverted OCS defined by extrusion vector (0, 0, -1) into a WCS
# aligned OCS defined by extrusion vector (0, 0, 1).
#
# This simplifies 2D entity processing for ezdxf users and creates DXF
# output for 3rd party DXF libraries which ignore the existence of the OCS.
#
# Warning:
# The WCS representation of OCS entities with flipped extrusion vector
# is not 100% identical to the source entity, curve orientation and vertex order
# may change. A mirrored text represented by an extrusion vector (0, 0, -1)
# cannot represented by an extrusion vector (0, 0, 1), therefore this CANNOT
# work for text entities or entities including text:
# TEXT, ATTRIB, ATTDEF, MTEXT, DIMENSION, LEADER, MLEADER

from typing import Iterable, cast, TYPE_CHECKING, List, Sequence
import math
from ezdxf.math import Z_AXIS, Vec3
from ezdxf.entities import DXFGraphic, DXFNamespace
from ezdxf.lldxf import const

if TYPE_CHECKING:
    from ezdxf.entities import LWPolyline, Polyline

__all__ = ["upright", "upright_all"]


def upright(entity: DXFGraphic) -> None:
    """Flips an inverted :ref:`OCS` defined by extrusion vector (0, 0, -1) into
    a :ref:`WCS` aligned :ref:`OCS` defined by extrusion vector (0, 0, 1).
    DXF entities with other extrusion vectors and unsupported DXF entities will
    be silently ignored.

    .. warning::

        The WCS representation of OCS entities with flipped extrusion vector
        is not 100% identical to the source entity, curve orientation and vertex
        order may change.

        E.g. arc angles are always counter-clockwise oriented around the
        extrusion vector, therefore flipping the extrusion vector creates a
        similar but not a 100% identical arc.

    Supported DXF entities:

    - CIRCLE
    - ARC
    - ELLIPSE (WCS entity, flips only the extrusion vector)
    - SOLID
    - TRACE
    - LWPOLYLINE

    """
    if not (
        isinstance(entity, DXFGraphic)
        and entity.is_alive
        and entity.dxf.hasattr("extrusion")
    ):
        return
    extrusion = Vec3(entity.dxf.extrusion).normalize()
    if not extrusion.isclose(FLIPPED_Z_AXIS):
        return
    dxftype: str = entity.dxftype()
    simple_tool = SIMPLE_UPRIGHT_TOOLS.get(dxftype)
    if simple_tool:
        simple_tool(entity.dxf)
    else:
        complex_tool = COMPLEX_UPRIGHT_TOOLS.get(dxftype)
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


def _flip_deg_angle(angle: float) -> float:
    return (180.0 if angle >= 0.0 else -180.0) - angle


def _flip_rad_angle(angle: float) -> float:
    return (math.pi if angle >= 0.0 else -math.pi) - angle


def _flip_vertex(vertex: Vec3) -> Vec3:
    return Vec3(-vertex.x, vertex.y, -vertex.z)


def _flip_existing_vertex(dxf: DXFNamespace, name: str) -> None:
    if dxf.hasattr(name):
        vertex = _flip_vertex(dxf.get(name))
        dxf.set(name, vertex)


def _flip_thickness(dxf: DXFNamespace) -> None:
    if dxf.hasattr("thickness"):
        dxf.thickness = -dxf.thickness


def _flip_elevation(dxf: DXFNamespace) -> None:
    if dxf.hasattr("elevation"):
        # works with float (LWPOLYLINE) and Vec3 (POLYLINE)
        dxf.elevation = -dxf.elevation


def _flip_circle(dxf: DXFNamespace) -> None:
    _flip_existing_vertex(dxf, "center")
    _flip_thickness(dxf)
    dxf.discard("extrusion")


def _flip_arc(dxf: DXFNamespace) -> None:
    _flip_circle(dxf)
    end_angle = dxf.end_angle
    dxf.end_angle = _flip_deg_angle(dxf.start_angle)
    dxf.start_angle = _flip_deg_angle(end_angle)


def _flip_solid(dxf: DXFNamespace) -> None:
    for name in const.VERTEXNAMES:
        _flip_existing_vertex(dxf, name)
    _flip_thickness(dxf)
    dxf.discard("extrusion")


def _flip_ellipse(dxf: DXFNamespace) -> None:
    # ELLIPSE is a WCS entity!
    # just process start- and end params
    end_param = -dxf.end_param
    dxf.end_param = -dxf.start_param
    dxf.start_param = end_param
    dxf.discard("extrusion")


# All properties stored as DXF attributes
SIMPLE_UPRIGHT_TOOLS = {
    "CIRCLE": _flip_circle,
    "ARC": _flip_arc,
    "SOLID": _flip_solid,
    "TRACE": _flip_solid,
    "ELLIPSE": _flip_ellipse,
}


def _flip_lwpolyline(entity: DXFGraphic) -> None:
    pline = cast("LWPolyline", entity)
    flipped_points: List[Sequence[float]] = []
    for x, y, start_width, end_width, bulge in pline.lwpoints:
        bulge = -bulge
        v = _flip_vertex(Vec3(x, y))
        flipped_points.append((v.x, v.y, start_width, end_width, bulge))
    pline.set_points(flipped_points, format="xyseb")
    dxf = pline.dxf
    _flip_thickness(dxf)
    _flip_elevation(dxf)
    dxf.discard("extrusion")


# Additional vertices or paths to transform
COMPLEX_UPRIGHT_TOOLS = {
    "LWPOLYLINE": _flip_lwpolyline,
    "POLYLINE": None,  # only 2D POLYLINE
    "HATCH": None,
    "MPOLYGON": None,
    "INSERT": None,
}
