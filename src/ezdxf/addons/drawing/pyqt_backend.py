# Created: 06.2020
# Copyright (c) 2020, Matthew Broadway
# License: MIT License
import math
from typing import Optional, Tuple, List, Union

from PyQt5 import QtCore as qc, QtGui as qg, QtWidgets as qw

from ezdxf.addons.drawing.backend_interface import DrawingBackend
from ezdxf.addons.drawing.text import FontMeasurements
from ezdxf.addons.drawing.type_hints import Radians, Color
from ezdxf.addons.drawing.properties import Properties
from ezdxf.entities import DXFGraphic
from ezdxf.math import Vector, Matrix44


class _Ellipse(qw.QGraphicsEllipseItem):
    """ an ellipse item which does not draw radii to the ends of the arc """

    # noinspection PyMethodOverriding
    def paint(self, painter: qg.QPainter, option: qw.QStyleOptionGraphicsItem, widget: Optional[qw.QWidget]) -> None:
        painter.setPen(self.pen())
        painter.drawArc(self.rect(), self.startAngle(), self.spanAngle())


class _Point(qw.QAbstractGraphicsShapeItem):
    """ a point which is drawn 'cosmetically' (scale depends on view) """

    def __init__(self, x: float, y: float, radius: float, brush: qg.QBrush):
        super().__init__()
        self.pos = qc.QPointF(x, y)
        self.radius = radius
        self.setPen(qg.QPen(qc.Qt.NoPen))
        self.setBrush(brush)

    # noinspection PyMethodOverriding
    def paint(self, painter: qg.QPainter, option: qw.QStyleOptionGraphicsItem, widget: Optional[qw.QWidget]) -> None:
        view_scale = _get_x_scale(painter.transform())
        radius = self.radius / view_scale

        painter.setBrush(self.brush())
        painter.setPen(qc.Qt.NoPen)
        painter.drawEllipse(self.pos, radius, radius)

    def boundingRect(self) -> qc.QRectF:
        return qc.QRectF(self.pos, qc.QSizeF(1, 1))


CorrespondingDXFEntity = 0  # the key used to store the dxf entity corresponding to each graphics element
CorrespondingDXFEntityStack = 1


class _PolylinePath:
    def __init__(self, current_entity: DXFGraphic):
        self.path = qg.QPainterPath()
        self.color = None
        self.first_component = True
        self.current_entity = current_entity

    def draw(self, component: Union["_BufferedLineSegment", "_BufferedArc"]):
        pos = self.path.currentPosition()
        pos = Vector(pos.x(), pos.y(), 0)
        start = component.start_point()
        jump_distance = pos.distance(start)
        if jump_distance > 1e-5:
            if not self.first_component:
                print(f'warning: non-contiguous polyline: {self.current_entity}. '
                      f'Jump from {pos} to {start} (distance of {jump_distance})')
            self.path.moveTo(start.x, start.y)
        component.draw(self.path)
        if self.color is None:
            self.color = component.color
        elif component.color != self.color:
            print(f'warning: component has different color to the polyline {component.color} != {self.color}')
        self.first_component = False


class _BufferedLineSegment:
    def __init__(self, start: Vector, end: Vector, color: Color):
        self.start = start
        self.end = end
        self.color = color

    def start_point(self) -> Vector:
        return self.start

    def draw(self, path: qg.QPainterPath):
        path.lineTo(self.end.x, self.end.y)


class _BufferedArc:
    def __init__(self, rect: qc.QRectF, start_angle: float, span_angle: float, color: Color):
        self.rect = rect
        self.start_angle = start_angle
        self.span_angle = span_angle
        self.color = color

    def start_point(self) -> Vector:
        c = self.rect.center()
        return Vector(c.x(), c.y(), 0) + Vector(self.rect.width() / 2, 0, 0).rotate_deg(self.start_angle)

    def draw(self, path: qg.QPainterPath):
        path.arcTo(self.rect, self.start_angle, self.span_angle)


class PyQtBackend(DrawingBackend):
    def __init__(self,
                 scene: qw.QGraphicsScene,
                 point_radius: float = 2.0,
                 *,
                 draw_individual_polyline_elements: bool = False,
                 debug_draw_rect: bool = False):
        super().__init__()
        self.scene = scene
        self._color_cache = {}
        self.point_radius = point_radius
        self.draw_individual_polyline_elements = draw_individual_polyline_elements
        self._no_line = qg.QPen(qc.Qt.NoPen)
        self._no_fill = qg.QBrush(qc.Qt.NoBrush)
        self._font = qg.QFont()
        self._font_measurements = _get_font_measurements(self._font)
        self._debug_draw_rect = debug_draw_rect
        self._polyline_components: List[Union[_BufferedLineSegment, _BufferedArc]] = []

    @property
    def is_drawing_polyline(self) -> bool:
        return not self.draw_individual_polyline_elements and self._polyline_nesting_depth > 0

    def _get_color(self, color: Color) -> qg.QColor:
        qt_color = self._color_cache.get(color, None)
        if qt_color is None:
            if len(color) == 7:
                qt_color = qg.QColor(color)  # '#RRGGBB'
            elif len(color) == 9:
                rgb = color[1:7]
                alpha = color[7:9]
                qt_color = qg.QColor(f'#{alpha}{rgb}')  # '#AARRGGBB'
            else:
                raise TypeError(color)

            self._color_cache[color] = qt_color
        return qt_color

    def _get_pen(self, color: Color) -> qg.QPen:
        pen = qg.QPen(self._get_color(color), 1)
        pen.setCosmetic(True)  # changes width depending on zoom
        pen.setJoinStyle(qc.Qt.RoundJoin)
        return pen

    def _set_item_data(self, item: qw.QGraphicsItem) -> None:
        item.setData(CorrespondingDXFEntity, self.current_entity)
        item.setData(CorrespondingDXFEntityStack, self.current_entity_stack)

    def set_background(self, color: Color):
        self.scene.setBackgroundBrush(qg.QBrush(self._get_color(color)))

    def draw_line(self, start: Vector, end: Vector, properties: Properties) -> None:
        color = properties.color
        if self.is_drawing_polyline:
            self._polyline_components.append(_BufferedLineSegment(start, end, color))
        else:
            item = self.scene.addLine(start.x, start.y, end.x, end.y, self._get_pen(color))
            self._set_item_data(item)

    def start_polyline(self):
        if not self.is_drawing_polyline:
            assert not self._polyline_components
        super().start_polyline()

    def end_polyline(self):
        super().end_polyline()
        if self.is_drawing_polyline or not self._polyline_components:
            return
        path = _PolylinePath(self.current_entity)
        for component in self._polyline_components:
            path.draw(component)
        item = self.scene.addPath(path.path, self._get_pen(path.color), self._no_fill)
        self._set_item_data(item)

        self._polyline_components = []

    def draw_point(self, pos: Vector, properties: Properties) -> None:
        brush = qg.QBrush(self._get_color(properties.color), qc.Qt.SolidPattern)
        item = _Point(pos.x, pos.y, self.point_radius, brush)
        self._set_item_data(item)
        self.scene.addItem(item)

    def draw_filled_polygon(self, points: List[Vector], properties: Properties) -> None:
        brush = qg.QBrush(self._get_color(properties.color), qc.Qt.SolidPattern)
        polygon = qg.QPolygonF()
        for p in points:
            polygon.append(qc.QPointF(p.x, p.y))
        item = self.scene.addPolygon(polygon, self._no_line, brush)
        self._set_item_data(item)

    def draw_text(self, text: str, transform: Matrix44, properties: Properties, cap_height: float) -> None:
        if not text:
            return  # no point rendering empty strings
        assert '\n' not in text, 'not a single line of text'

        scale = cap_height / self._font_measurements.cap_height
        transform = Matrix44.scale(scale, -scale, 0) @ transform

        path = qg.QPainterPath()
        path.addText(0, 0, self._font, text)
        path = _matrix_to_qtransform(transform).map(path)
        item = self.scene.addPath(path, self._no_line, self._get_color(properties.color))
        self._set_item_data(item)

    def get_font_measurements(self, cap_height: float) -> FontMeasurements:
        return self._font_measurements.scale_from_baseline(desired_cap_height=cap_height)

    def get_text_line_width(self, text: str, cap_height: float) -> float:
        if not text:
            return 0
        assert '\n' not in text
        scale = cap_height / self._font_measurements.cap_height
        return _get_text_rect(self._font, text).right() * scale

    def draw_arc(self, center: Vector, width: float, height: float, angle: Radians,
                 draw_angles: Optional[Tuple[Radians, Radians]], properties: Properties) -> None:
        top = center.x - width / 2
        left = center.y - height / 2
        color = properties.color

        # any angle other than 0 is not possible with arcTo and a complete circle/ellipse wouldn't make sense
        if self.is_drawing_polyline and angle == 0.0 and draw_angles is not None:
            start, span = _draw_angles_to_start_and_span(draw_angles)
            self._polyline_components.append(_BufferedArc(qc.QRectF(top, left, width, height), start, span, color))
            return

        ellipse = _Ellipse(top, left, width, height)
        ellipse.setBrush(self._no_fill)
        ellipse.setPen(self._get_pen(color))
        ellipse.setTransformOriginPoint(center.x, center.y)
        ellipse.setRotation(math.degrees(angle))
        if draw_angles is not None:
            start, span = _draw_angles_to_start_and_span(draw_angles)
            # angles stored as integers in 16ths of a degree units
            ellipse.setStartAngle(int(round(start * 16)))
            ellipse.setSpanAngle(int(round(span * 16)))
        self._set_item_data(ellipse)
        self.scene.addItem(ellipse)

    def clear(self) -> None:
        self.scene.clear()

    def finalize(self) -> None:
        super().finalize()
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        if self._debug_draw_rect:
            self.scene.addRect(self.scene.sceneRect(), self._get_pen('#000000'), self._no_fill)


def _buffer_rect(r: Union[qc.QRect, qc.QRectF], buffer_x: float,
                 buffer_y: Optional[float] = None) -> Union[qc.QRect, qc.QRectF]:
    if buffer_y is None:
        buffer_y = buffer_x
    bx = buffer_x / 2
    by = buffer_y / 2
    if isinstance(r, qc.QRect):
        bx, by = int(bx), int(by)
    # arguments are deltas to apply to the left, top, right, bottom of the rect
    # note: +y is down
    return r.adjusted(-bx, -by, bx, by)


def _get_x_scale(t: qg.QTransform) -> float:
    return math.sqrt(t.m11() * t.m11() + t.m21() * t.m21())


def _matrix_to_qtransform(matrix: Matrix44) -> qg.QTransform:
    """ Qt also uses row-vectors so the translation elements are placed in the bottom row

    This is only a simple conversion which assumes that although the transformation is 4x4,
    it does not involve the z axis.

    A more correct transformation could be implemented like so:
    https://stackoverflow.com/questions/10629737/convert-3d-4x4-rotation-matrix-into-2d
    """
    return qg.QTransform(*matrix.get_2d_transformation())


def _draw_angles_to_start_and_span(draw_angles: Tuple[float, float]) -> Tuple[float, float]:
    a, b = draw_angles
    if b < a:  # arc crosses the discontinuity at n*360
        b += math.tau
    start_angle = -math.degrees(a)
    span_angle = -math.degrees(b - a)
    return start_angle, span_angle


def _get_text_rect(font: qg.QFont, text: str) -> qc.QRectF:
    path = qg.QPainterPath()
    path.addText(0, 0, font, text)
    return path.boundingRect()


def _get_font_measurements(font: qg.QFont) -> FontMeasurements:
    upper_x = _get_text_rect(font, 'X')
    lower_x = _get_text_rect(font, 'x')
    lower_p = _get_text_rect(font, 'p')
    return FontMeasurements(
        baseline=lower_x.bottom(),
        cap_top=upper_x.top(),
        x_top=lower_x.top(),
        bottom=lower_p.bottom(),
    )
