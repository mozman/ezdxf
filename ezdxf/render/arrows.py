# created: 2019-01-03
# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING
from ezdxf.algebra.vector import Vector

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex, GenericLayoutType


class _Arrows:
    closed_filled = ""
    dot = "DOT"
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
    ez_arrow_head = "EZ_ARROW_HEAD"
    __acad__ = {
        closed_filled, dot, dot_small, dot_blank, origin_indicator, origin_indicator_2, open, right_angle, open_30,
        closed, dot_smallblank, none, oblique, box_filled, box, closed_blank, datum_triangle, datum_triangle_filled,
        integral, architectural_tick
    }
    __ezdxf__ = {
        ez_arrow_head,
    }
    __all_arrows__ = __acad__ | __ezdxf__

    def is_acad_arrow(self, item: str) -> bool:
        return item.upper() in self.__acad__

    def is_ezdxf_arrow(self, item: str) -> bool:
        return item.upper() in self.__ezdxf__

    def __contains__(self, item: str) -> bool:
        return item.upper() in self.__all_arrows__

    def render(self, layout: 'GenericLayoutType',
               name: str, insert: 'Vertex',
               size: float = 1.,
               rotation: float = 0,
               reverse: bool = False,
               dxfattribs: dict = None) -> None:

        p1 = Vector(insert)
        direction = Vector.from_deg_angle(rotation)
        if name == self.closed_filled:
            size = size * .25
            p2 = p1 + direction * size
            d = (p2 - p1).orthogonal().normalize(size / 4)
            layout.add_solid([p1, p2 + d, p2 - d], dxfattribs=dxfattribs)
        elif name == self.dot:
            layout.add_circle(center=insert, radius=size, dxfattribs=dxfattribs)
        elif name == self.oblique:
            d = Vector.from_deg_angle(rotation + 45).normalize(size * .707106781)  # sqrt(2)
            layout.add_line(start=p1 + d, end=p1 - d, dxfattribs=dxfattribs)


ARROWS = _Arrows()
