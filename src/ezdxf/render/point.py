#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
from typing import TYPE_CHECKING, List
import math
from ezdxf.entities import factory
from ezdxf.math import Vector, UCS, NULLVEC

if TYPE_CHECKING:
    from ezdxf.entities import Point, DXFEntity


def render(point: 'Point', pdsize: float = 1,
           pdmode: int = 0) -> List['DXFEntity']:
    """ Yields point graphic as DXF primitives LINE and CIRCLE entities.
    The dimensionless point is rendered a line with start == end vertex!
    Check for condition :code:`(line.dxf.start.isclose(line.dxf.end)` if
    the rendering engine can't handle zero-length lines.
    """

    def add_line_symmetrical(delta: Vector):
        dxfattribs['start'] = ucs.to_wcs(-delta)
        dxfattribs['end'] = ucs.to_wcs(delta)
        entities.append(factory.new('LINE', dxfattribs))

    def add_line(s: Vector, e: Vector):
        dxfattribs['start'] = ucs.to_wcs(s)
        dxfattribs['end'] = ucs.to_wcs(e)
        entities.append(factory.new('LINE', dxfattribs))

    center = point.dxf.location
    # This is not a real OCS! Defines just the point orientation,
    # location is in WCS!
    ocs = point.ocs()
    ucs = UCS(origin=center, ux=ocs.ux, uz=ocs.uz)
    ucs = ucs.rotate_local_z(math.radians(-point.dxf.angle))

    entities = []
    gfx = point.graphic_properties()

    size2 = pdsize * 0.5
    size3 = pdsize
    circle = bool(pdmode & 32)
    square = bool(pdmode & 64)
    style = pdmode & 7

    dxfattribs = dict(gfx)
    if style == 0:
        add_line_symmetrical(NULLVEC)
    elif style == 2:
        add_line_symmetrical(Vector(size3, 0))
        add_line_symmetrical(Vector(0, size3))
    elif style == 3:
        add_line_symmetrical(Vector(size3, size3))
        add_line_symmetrical(Vector(size3, -size3))
    elif style == 4:
        add_line(NULLVEC, Vector(0, size2))
    if square:
        x1 = -size2
        x2 = size2
        y1 = -size2
        y2 = size2
        add_line(Vector(x1, y1), Vector(x2, y1))
        add_line(Vector(x2, y1), Vector(x2, y2))
        add_line(Vector(x2, y2), Vector(x1, y2))
        add_line(Vector(x1, y2), Vector(x1, y1))
    if circle:
        dxfattribs = dict(gfx)
        if point.dxf.hasattr('extrusion'):
            dxfattribs['extrusion'] = point.dxf.extrusion
        dxfattribs['center'] = point.dxf.location
        dxfattribs['radius'] = size2
        entities.append(factory.new('CIRCLE', dxfattribs))

    return entities
