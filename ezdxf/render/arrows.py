# created: 2019-01-03
# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable
from ezdxf.algebra.vector import Vector
from .forms import open_arrow, arrow2
from .shape import Shape

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex, GenericLayoutType

DEFAULT_ARROW_ANGLE = 18.924644
DEFAULT_BETA = 45.


class BaseArrow:
    REVERSE_ANGLE = 0

    def __init__(self, vertices: Iterable['Vertex']):
        self.shape = Shape(vertices)

    def connection_point(self) -> Vector:
        return self.shape[0]

    def render(self, layout: 'GenericLayoutType', dxfattribs: dict = None):
        pass

    def place(self, insert: 'Vertex', angle: float):
        self.shape.rotate(angle)
        self.shape.translate(insert)

    def get_angle(self, rotation: float, reverse: bool):
        return rotation + self.REVERSE_ANGLE if reverse else rotation


class NoneStroke(BaseArrow):
    def __init__(self, insert: 'Vertex', size: float = 1.0, angle: float = 0, reverse: bool = False):
        super().__init__([Vector(insert)])


class ObliqueStroke(BaseArrow):
    def __init__(self, insert: 'Vertex', size: float = 1.0, angle: float = 0, reverse: bool = False):
        self.size = size
        s2 = size / 2
        # shape = [center, lower left, upper right]
        super().__init__([Vector(), Vector(-s2, -s2), Vector(s2, s2)])
        self.place(insert, angle)

    def render(self, layout: 'GenericLayoutType', dxfattribs: dict = None):
        layout.add_line(start=self.shape[1], end=self.shape[2], dxfattribs=dxfattribs)


class ArchTick(ObliqueStroke):
    def render(self, layout: 'GenericLayoutType', dxfattribs: dict = None):
        dxfattribs['default_start_width'] = self.size * .15
        dxfattribs['default_end_width'] = self.size * .15
        layout.add_polyline2d(self.shape[1:], dxfattribs=dxfattribs)


class ClosedArrow(BaseArrow):
    REVERSE_ANGLE = 180

    def __init__(self, insert: 'Vertex', size: float = 1.0, angle: float = 0, reverse: bool = False):
        super().__init__(open_arrow(size, angle=DEFAULT_ARROW_ANGLE))
        self.place(insert, self.get_angle(angle, reverse))

    def connection_point(self) -> Vector:
        return self.shape[1]

    def render(self, layout: 'GenericLayoutType', dxfattribs: dict = None):
        polyline = layout.add_polyline2d(
            points=self.shape,
            dxfattribs=dxfattribs)
        polyline.close(True)


class ClosedArrowBlank(ClosedArrow):
    def connection_point(self):
        return self.shape[0].lerp(self.shape[2])


class ClosedArrowFilled(ClosedArrow):
    def render(self, layout: 'GenericLayoutType', dxfattribs: dict = None):
        layout.add_solid(
            points=self.shape,
            dxfattribs=dxfattribs,
        )


class _OpenArrow(BaseArrow):
    REVERSE_ANGLE = 180

    def __init__(self, arrow_angle: float, insert: 'Vertex', size: float = 1.0, angle: float = 0,
                 reverse: bool = False):
        super().__init__(open_arrow(size, angle=arrow_angle))
        self.place(insert, self.get_angle(angle, reverse))

    def connection_point(self) -> Vector:
        return self.shape[1]

    def render(self, layout: 'GenericLayoutType', dxfattribs: dict = None):
        layout.add_polyline2d(points=self.shape, dxfattribs=dxfattribs)


class OpenArrow(_OpenArrow):
    def __init__(self, insert: 'Vertex', size: float = 1.0, angle: float = 0, reverse: bool = False):
        super().__init__(DEFAULT_ARROW_ANGLE, insert, size, angle, reverse)


class OpenArrow30(_OpenArrow):
    def __init__(self, insert: 'Vertex', size: float = 1.0, angle: float = 0, reverse: bool = False):
        super().__init__(30, insert, size, angle, reverse)


class OpenArrow90(_OpenArrow):
    def __init__(self, insert: 'Vertex', size: float = 1.0, angle: float = 0, reverse: bool = False):
        super().__init__(90, insert, size, angle, reverse)


class Circle(BaseArrow):
    def __init__(self, insert: 'Vertex', size: float = 1.0, angle: float = 0, reverse: bool = False):
        self.radius = size / 2
        # shape = [center point, connection point]
        super().__init__([
            Vector(),
            Vector(self.radius, 0) if not reverse else Vector(-self.radius, 0)
        ])
        self.place(insert, angle)

    def render(self, layout: 'GenericLayoutType', dxfattribs: dict = None):
        layout.add_circle(center=self.shape[0], radius=self.radius, dxfattribs=dxfattribs)


class Dot(Circle):
    def render(self, layout: 'GenericLayoutType', dxfattribs: dict = None):
        dxfattribs['closed'] = True
        dxfattribs['default_start_width'] = self.radius
        dxfattribs['default_end_width'] = self.radius
        center = self.shape[0]
        d = Vector(self.radius / 2, 0)
        polyline = layout.add_polyline2d(points=[center - d, center + d], dxfattribs=dxfattribs)
        polyline[0].dxf.bulge = 1
        polyline[1].dxf.bulge = 1


class CircleBlank(Circle):
    def connection_point(self) -> Vector:
        return self.shape[1]  # blank circle


class OriginIndicator2(CircleBlank):
    def render(self, layout: 'GenericLayoutType', dxfattribs: dict = None):
        layout.add_circle(center=self.shape[0], radius=self.radius, dxfattribs=dxfattribs)
        layout.add_circle(center=self.shape[0], radius=self.radius / 2, dxfattribs=dxfattribs)


class Box(BaseArrow):
    def __init__(self, insert: 'Vertex', size: float = 1.0, angle: float = 0, reverse: bool = False):
        # shape = [lower_left, lower_right, upper_right, upper_left, connection point]
        s2 = size / 2
        super().__init__([
            Vector(-s2, -s2),
            Vector(+s2, -s2),
            Vector(+s2, +s2),
            Vector(-s2, +s2),
            Vector(+s2, 0) if not reverse else Vector(-s2, 0)
        ])
        self.place(insert, angle)

    def render(self, layout: 'GenericLayoutType', dxfattribs: dict = None):
        polyline = layout.add_polyline2d(points=self.shape[0:4], dxfattribs=dxfattribs)
        polyline.close(True)

    def connection_point(self):
        return self.shape[4]


class BoxFilled(Box):
    def render(self, layout: 'GenericLayoutType', dxfattribs: dict = None):
        def solid_order():
            v = self.shape.vertices
            return [v[0], v[1], v[3], v[2]]

        layout.add_solid(points=solid_order(), dxfattribs=dxfattribs)


class Integral(BaseArrow):
    def __init__(self, insert: 'Vertex', size: float = 1.0, angle: float = 0, reverse: bool = False):
        self.radius = size * .3535534
        self.angle = angle
        # shape = [center, left_center, right_center]
        super().__init__([
            Vector(),
            Vector(-self.radius, 0),
            Vector(self.radius, 0),
        ])
        self.place(insert, angle)

    def render(self, layout: 'GenericLayoutType', dxfattribs: dict = None):
        angle = self.angle
        layout.add_arc(center=self.shape[1], radius=self.radius, start_angle=-90 + angle, end_angle=angle,
                       dxfattribs=dxfattribs)
        layout.add_arc(center=self.shape[2], radius=self.radius, start_angle=90 + angle, end_angle=180 + angle,
                       dxfattribs=dxfattribs)


class DatumTriangle(BaseArrow):
    REVERSE_ANGLE = 180

    def __init__(self, insert: 'Vertex', size: float = 1.0, angle: float = 0, reverse: bool = False):
        d = .577350269 * size  # tan(30)
        # shape = [upper_corner, lower_corner, connection_point]
        super().__init__([
            Vector(0, d),
            Vector(0, -d),
            Vector(size, 0),
        ])
        self.place(insert, self.get_angle(angle, reverse))

    def render(self, layout: 'GenericLayoutType', dxfattribs: dict = None):
        polyline = layout.add_polyline2d(points=self.shape, dxfattribs=dxfattribs)
        polyline.close(True)

    def connection_point(self):
        return self.shape[2]


class DatumTriangleFilled(DatumTriangle):
    def render(self, layout: 'GenericLayoutType', dxfattribs: dict = None):
        layout.add_solid(points=self.shape, dxfattribs=dxfattribs)


class EzArrow(BaseArrow):
    REVERSE_ANGLE = 180

    def __init__(self, insert: 'Vertex', size: float = 1.0, angle: float = 0, reverse: bool = False):
        super().__init__(arrow2(size, angle=DEFAULT_ARROW_ANGLE))
        self.place(insert, self.get_angle(angle, reverse))

    def connection_point(self) -> Vector:
        return self.shape[1]

    def render(self, layout: 'GenericLayoutType', dxfattribs: dict = None):
        polyline = layout.add_polyline2d(self.shape, dxfattribs=dxfattribs)
        polyline.close(True)


class EzArrowBlank(EzArrow):
    def connection_point(self) -> Vector:
        return self.shape[3]


class EzArrowFilled(EzArrow):
    def render(self, layout: 'GenericLayoutType', dxfattribs: dict = None):
        points = self.shape.vertices
        layout.add_solid([points[0], points[1], points[3], points[2]], dxfattribs=dxfattribs)


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
    ez_arrow = "EZ_ARROW"
    ez_arrow_blank = "EZ_ARROW_BLANK"
    ez_arrow_filled = "EZ_ARROW_FILLED"

    CLASSES = {
        closed_filled: ClosedArrowFilled,
        dot: Dot,
        dot_small: Dot,
        dot_blank: CircleBlank,
        origin_indicator: Circle,
        origin_indicator_2: OriginIndicator2,
        open: OpenArrow,
        right_angle: OpenArrow90,
        open_30: OpenArrow30,
        closed: ClosedArrow,
        dot_smallblank: CircleBlank,
        none: NoneStroke,
        oblique: ObliqueStroke,
        box_filled: BoxFilled,
        box: Box,
        closed_blank: ClosedArrowBlank,
        datum_triangle: DatumTriangle,
        datum_triangle_filled: DatumTriangleFilled,
        integral: Integral,
        architectural_tick: ArchTick,
        ez_arrow: EzArrow,
        ez_arrow_blank: EzArrowBlank,
        ez_arrow_filled: EzArrowFilled,
    }
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

    def create_block(self, blocks, name: str):
        block_name = self.block_name(name)
        if block_name not in blocks:
            block = blocks.new(block_name)
            arrow = self.arrow_shape(name, insert=(0, 0), size=1, rotation=0, reverse=False)
            arrow.render(block, dxfattribs={'color': 0, 'linetype': 'BYBLOCK'})
        return block_name

    def block_name(self, name):
        if not self.is_acad_arrow(name):  # common BLOCK definition
            return name.upper()  # e.g. Dimension.dxf.bkl = 'EZ_ARROW' == Insert.dxf.name
        elif name == "":  # special AutoCAD arrow symbols 'CLOSED_FILLED' has no name
            return "_CLOSED_FILLED"  # Dimension.dxf.bkl = '' != Insert.dxf.name = '_CLOSED_FILLED'
        else:  # special AutoCAD arrow symbols have leading '_' as common practice!
            return '_' + name.upper()  # Dimension.dxf.bkl = 'DOT' != Insert.dxf.name = '_DOT'

    def insert_arrow(self, layout: 'GenericLayoutType',
                     name: str,
                     insert: 'Vertex',
                     size: float = 1.,
                     rotation: float = 0,
                     reverse: bool = False,
                     dxfattribs: dict = None) -> Vector:

        block_name = self.create_block(layout.drawing.blocks, name)
        dxfattribs = dxfattribs or {}
        # real placed arrow shape required for correct connection point
        arrow = self.arrow_shape(name, insert=insert, size=size, rotation=rotation, reverse=reverse)

        dxfattribs['rotation'] = arrow.get_angle(rotation, reverse)
        dxfattribs['xscale'] = size
        dxfattribs['yscale'] = size
        layout.add_blockref(block_name, insert=insert, dxfattribs=dxfattribs)
        return arrow.connection_point()

    def render_arrow(self, layout: 'GenericLayoutType',
                     name: str,
                     insert: 'Vertex',
                     size: float = 1.,
                     rotation: float = 0,
                     reverse: bool = False,
                     dxfattribs: dict = None) -> Vector:

        dxfattribs = dxfattribs or {}
        arrow = self.arrow_shape(name, insert, size, rotation, reverse)
        arrow.render(layout, dxfattribs)
        return arrow.connection_point()

    def arrow_shape(self, name: str, insert: 'Vertex', size: float, rotation: float, reverse: bool) -> BaseArrow:
        # size depending shapes
        if name == self.dot_small:
            size *= .25
        elif name == self.dot_smallblank:
            size *= .5
        cls = self.CLASSES[name]
        return cls(insert, size, rotation, reverse)


ARROWS = _Arrows()
