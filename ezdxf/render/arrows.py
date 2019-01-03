# created: 2019-01-03
# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING
from ezdxf.algebra.vector import Vector
from .forms import open_arrow, arrow2, translate, rotate

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex, GenericLayoutType

DEFAULT_ARROW_ANGLE = 18.924644
DEFAULT_BETA = 45.


class _Arrows:
    closed_filled = ""  # dimasz = length
    dot = "DOT"  # dimasz = diameter
    dot_small = "DOTSMALL"
    dot_blank = "DOTBLANK"
    origin_indicator = "ORIGIN"
    origin_indicator_2 = "ORIGIN2"
    open = "OPEN"
    right_angle = "OPEN90"
    open_30 = "OPEN30"
    closed = "CLOSED"
    dot_smallblank = "SMALL"
    none = "NONE"
    oblique = "OBLIQUE"
    box_filled = "BOXFILLED"
    box = "BOXBLANK"
    closed_blank = "CLOSEDBLANK"
    datum_triangle_filled = "DATUMFILLED"
    datum_triangle = "DATUMBLANK"
    integral = "INTEGRAL"
    architectural_tick = "ARCHTICK"
    # ezdxf special arrows
    ez_arrow = "EZ_ARROW"
    ez_arrow_blank = "EZ_ARROW_BLANK"
    ez_arrow_filled = "EZ_ARROW_FILLED"

    __acad__ = {
        closed_filled, dot, dot_small, dot_blank, origin_indicator, origin_indicator_2, open, right_angle, open_30,
        closed, dot_smallblank, none, oblique, box_filled, box, closed_blank, datum_triangle, datum_triangle_filled,
        integral, architectural_tick
    }
    __ezdxf__ = {
        ez_arrow,
        ez_arrow_blank,
        ez_arrow_filled,
    }
    __all_arrows__ = __acad__ | __ezdxf__

    def is_acad_arrow(self, item: str) -> bool:
        return item.upper() in self.__acad__

    def is_ezdxf_arrow(self, item: str) -> bool:
        return item.upper() in self.__ezdxf__

    def __contains__(self, item: str) -> bool:
        return item.upper() in self.__all_arrows__

    def create_block(self, blocks, name):
        block_name = self.block_name(name)
        if block_name not in blocks:
            block = blocks.new(block_name)
            self.render_arrow(block, name, insert=(0, 0), dxfattribs={'color': 0, 'linetype': 'BYBLOCK'})
        return block_name

    def block_name(self, name):
        if name == "":
            return "_CLOSED_FILLED"
        else:
            return '_' + name.upper()

    def insert_arrow(self, layout: 'GenericLayoutType',
                     name: str,
                     insert: 'Vertex',
                     size: float = 1.,
                     rotation: float = 0,
                     reverse: bool = False,
                     dxfattribs: dict = None) -> Vector:

        def _insert(angle):
            dxfattribs['rotation'] = angle
            dxfattribs['xscale'] = size
            dxfattribs['yscale'] = size
            layout.add_blockref(block_name, insert=insert, dxfattribs=dxfattribs)

        blocks = layout.drawing.blocks
        block_name = self.create_block(blocks, name)
        dxfattribs = dxfattribs or {}
        if name in _INSERT_ROTATED:
            _insert(rotation + 180 if reverse else rotation)
        else:
            _insert(rotation)
        return get_connection_point(name, insert, size, rotation, reverse)

    def render_arrow(self, layout: 'GenericLayoutType',
                     name: str,
                     insert: 'Vertex',
                     size: float = 1.,
                     rotation: float = 0,
                     reverse: bool = False,
                     dxfattribs: dict = None) -> Vector:

        def render_closed_filled_arrow(angle):
            layout.add_solid(
                points=translate(rotate(open_arrow(size, angle=DEFAULT_ARROW_ANGLE), angle), insert),
                dxfattribs=dxfattribs,
            )

        def render_closed_arrow(angle):
            polyline = layout.add_polyline2d(
                points=list(translate(rotate(open_arrow(size, angle=DEFAULT_ARROW_ANGLE), angle), insert)),
                dxfattribs=dxfattribs)
            polyline.close(True)

        def render_dot():
            s2 = size / 2
            if name == self.dot_small:
                s2 = s2 * .25
            d = Vector.from_deg_angle(rotation) * s2 / 2
            m = Vector(insert)
            dxfattribs['closed'] = True
            dxfattribs['default_start_width'] = s2
            dxfattribs['default_end_width'] = s2
            polyline = layout.add_polyline2d(points=[m - d, m + d], dxfattribs=dxfattribs)
            polyline[0].dxf.bulge = 1
            polyline[1].dxf.bulge = 1

        def render_circles():
            s2 = size / 2
            if name == self.dot_smallblank:
                s2 = s2 * .5
            layout.add_circle(center=insert, radius=s2, dxfattribs=dxfattribs)
            if name == self.origin_indicator_2:
                layout.add_circle(center=insert, radius=s2 / 2, dxfattribs=dxfattribs)

        def render_oblique_stroke():
            s2 = size / 2
            s, e = translate(rotate([(-s2, -s2), (s2, s2)], rotation), insert)
            if name == self.oblique:
                layout.add_line(start=s, end=e, dxfattribs=dxfattribs)
            else:
                dxfattribs['default_start_width'] = size * .15
                dxfattribs['default_end_width'] = size * .15
                layout.add_polyline2d([s, e], dxfattribs=dxfattribs)

        def render_open_arrow(angle):
            if name == self.open:
                arrow_angle = DEFAULT_ARROW_ANGLE
            elif name == self.open_30:
                arrow_angle = 30
            else:
                arrow_angle = 90

            points = list(translate(rotate(open_arrow(size, angle=arrow_angle), angle), insert))
            layout.add_polyline2d(points, dxfattribs=dxfattribs)

        def render_box():
            polyline = layout.add_polyline2d(points=list(translate(rotate(square(size), rotation), insert)),
                                             dxfattribs=dxfattribs)
            polyline.close(True)

        def render_filled_box():
            layout.add_solid(points=translate(rotate(solid_square(size), rotation), insert), dxfattribs=dxfattribs)

        def render_integral():
            s2 = size * .3535534
            d = Vector.from_deg_angle(rotation) * s2
            m = Vector(insert)
            layout.add_arc(center=m - d, radius=s2, start_angle=-90 + rotation, end_angle=rotation,
                           dxfattribs=dxfattribs)
            layout.add_arc(center=m + d, radius=s2, start_angle=90 + rotation, end_angle=180 + rotation,
                           dxfattribs=dxfattribs)

        def render_datum_triangle(angle):
            p = Vector(insert)
            direction = Vector.from_deg_angle(angle)
            d = direction.orthogonal() * (.577350269 * size)  # tan(30)
            points = (p + d, p - d, p + (direction * size))
            if name == self.datum_triangle:
                polyline = layout.add_polyline2d(points=points, dxfattribs=dxfattribs)
                polyline.close(True)
            else:
                layout.add_solid(points=points, dxfattribs=dxfattribs)

        def render_ezdxf_arrows(angle):
            p = Vector(insert)
            points = list(translate(rotate(arrow2(size, angle=DEFAULT_ARROW_ANGLE, beta=DEFAULT_BETA), angle), p))
            if name in (self.ez_arrow, self.ez_arrow_blank):
                polyline = layout.add_polyline2d(points, dxfattribs=dxfattribs)
                polyline.close(True)
            else:
                layout.add_solid([points[0], points[1], points[3], points[2]], dxfattribs=dxfattribs)

        dxfattribs = dxfattribs or {}
        if name == self.closed_filled:
            render_closed_filled_arrow(rotation + 180 if reverse else rotation)
        elif name in (self.closed, self.closed_blank):
            render_closed_arrow(rotation + 180 if reverse else rotation)
        elif name in (self.dot, self.dot_small):
            render_dot()
        elif name in _CIRCLES:
            render_circles()
        elif name in (self.oblique, self.architectural_tick):
            render_oblique_stroke()
        elif name in _OPEN_ARROWS:
            render_open_arrow(rotation + 180 if reverse else rotation)
        elif name == self.box_filled:
            render_filled_box()
        elif name == self.box:
            render_box()
        elif name == self.integral:
            render_integral()
        elif name in (self.datum_triangle, self.datum_triangle_filled):
            render_datum_triangle(rotation + 180 if reverse else rotation)
        elif name in _EZDXF_ARROWS:
            render_ezdxf_arrows(rotation + 180 if reverse else rotation)
        return get_connection_point(name, insert, size, rotation, reverse)


def get_connection_point(name, insert, size, rotation, reverse):
    pos = Vector(insert)
    angle = rotation + 180 if reverse else rotation
    direction = Vector.from_deg_angle(angle)
    connection_point = pos
    s2 = size / 2

    if name not in _BLANKS:
        return pos
    if name == _Arrows.closed_blank:
        points = list(translate(rotate(open_arrow(size, angle=DEFAULT_ARROW_ANGLE), angle), insert))
        connection_point = points[0].lerp(points[2])
    elif name in (_Arrows.box, _Arrows.dot_blank, _Arrows.origin_indicator_2, _Arrows.dot_smallblank):
        if name == _Arrows.dot_smallblank:
            s2 = s2 * .5
        connection_point = pos + (direction * s2)
    elif name == _Arrows.datum_triangle:
        connection_point = pos + (direction * size)
    elif name == _Arrows.ez_arrow_blank:
        points = list(translate(rotate(arrow2(size, angle=DEFAULT_ARROW_ANGLE, beta=DEFAULT_BETA), angle), pos))
        connection_point = points[-1]
    return connection_point


def square(size):
    s2 = size / 2
    return Vector(-s2, -s2), Vector(s2, -s2), Vector(s2, s2), Vector(-s2, s2)


def solid_square(size):
    s2 = size / 2
    return Vector(-s2, -s2), Vector(s2, -s2), Vector(-s2, s2), Vector(s2, s2)


_CIRCLES = {
    _Arrows.dot_blank,
    _Arrows.dot_smallblank,
    _Arrows.origin_indicator,
    _Arrows.origin_indicator_2,
}
_OPEN_ARROWS = {
    _Arrows.open,
    _Arrows.open_30,
    _Arrows.right_angle
}
_EZDXF_ARROWS = {
    _Arrows.ez_arrow,
    _Arrows.ez_arrow_blank,
    _Arrows.ez_arrow_filled
}
_INSERT_ROTATED = {
                      _Arrows.closed_filled,
                      _Arrows.closed,
                      _Arrows.closed_blank,
                      _Arrows.datum_triangle,
                      _Arrows.datum_triangle_filled,
                  } | _OPEN_ARROWS | _EZDXF_ARROWS

_BLANKS = {
    _Arrows.closed_blank,
    _Arrows.datum_triangle,
    _Arrows.box,
    _Arrows.dot_smallblank,
    _Arrows.dot_blank,
    _Arrows.origin_indicator_2,
    _Arrows.ez_arrow_blank,
}

ARROWS = _Arrows()
