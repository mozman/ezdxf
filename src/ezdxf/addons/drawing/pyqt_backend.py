# Created: 06.2020
# Copyright (c) 2020, Matthew Broadway
# License: MIT License
import math
from typing import Optional, Tuple, List, Union

from PyQt5 import QtCore as qc, QtGui as qg, QtWidgets as qw

from ezdxf.addons.drawing.backend_interface import DrawingBackend
from ezdxf.addons.drawing.text import FontMeasurements
from ezdxf.addons.drawing.type_hints import Radians, Color
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


class PyQtBackend(DrawingBackend):
    def __init__(self, scene: qw.QGraphicsScene, point_radius: float = 2.0, *, debug_draw_rect: bool = False):
        super().__init__()
        self.scene = scene
        self._color_cache = {}
        self.point_radius = point_radius
        self._no_line = qg.QPen(qc.Qt.NoPen)
        self._no_fill = qg.QBrush(qc.Qt.NoBrush)
        self._font = qg.QFont()
        self._font_measurements = _get_font_measurements(self._font)
        self._debug_draw_rect = debug_draw_rect

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
        return pen

    def set_background(self, color: Color):
        self.scene.setBackgroundBrush(qg.QBrush(self._get_color(color)))

    def draw_line(self, start: Vector, end: Vector, color: Color) -> None:
        item = self.scene.addLine(start.x, start.y, end.x, end.y, self._get_pen(color))
        item.setData(CorrespondingDXFEntity, self.current_entity)

    def draw_line_string(self, points: List[Vector], color: Color) -> None:
        if not points:
            return
        path = qg.QPainterPath()
        path.moveTo(points[0].x, points[0].y)
        for p in points[1:]:
            path.lineTo(p.x, p.y)
        item = self.scene.addPath(path, self._get_pen(color), self._no_fill)
        item.setData(CorrespondingDXFEntity, self.current_entity)

    def draw_point(self, pos: Vector, color: Color) -> None:
        brush = qg.QBrush(self._get_color(color), qc.Qt.SolidPattern)
        item = _Point(pos.x, pos.y, self.point_radius, brush)
        item.setData(CorrespondingDXFEntity, self.current_entity)
        self.scene.addItem(item)

    def draw_filled_polygon(self, points: List[Vector], color: Color) -> None:
        brush = qg.QBrush(self._get_color(color), qc.Qt.SolidPattern)
        polygon = qg.QPolygonF()
        for p in points:
            polygon.append(qc.QPointF(p.x, p.y))
        item = self.scene.addPolygon(polygon, self._no_line, brush)
        item.setData(CorrespondingDXFEntity, self.current_entity)

    def draw_text(self, text: str, transform: Matrix44, color: Color, cap_height: float) -> None:
        if not text:
            return  # no point rendering empty strings
        assert '\n' not in text, 'not a single line of text'

        scale = cap_height / self._font_measurements.cap_height
        transform = Matrix44.scale(scale, -scale, 0) @ transform

        path = qg.QPainterPath()
        path.addText(0, 0, self._font, text)
        path = _matrix_to_qtransform(transform).map(path)
        item = self.scene.addPath(path, self._no_line, self._get_color(color))
        item.setData(CorrespondingDXFEntity, self.current_entity)

    def get_font_measurements(self, cap_height: float) -> FontMeasurements:
        return self._font_measurements.scale_from_baseline(desired_cap_height=cap_height)

    def get_text_line_width(self, text: str, cap_height: float) -> float:
        if not text:
            return 0
        assert '\n' not in text
        scale = cap_height / self._font_measurements.cap_height
        return _get_text_rect(self._font, text).right() * scale

    def draw_arc(self, center: Vector, width: float, height: float, angle: Radians,
                 draw_angles: Optional[Tuple[Radians, Radians]], color: Color) -> None:
        top = center.x - width / 2
        left = center.y - height / 2
        ellipse = _Ellipse(top, left, width, height)
        ellipse.setBrush(self._no_fill)
        ellipse.setPen(self._get_pen(color))
        ellipse.setTransformOriginPoint(center.x, center.y)
        ellipse.setRotation(math.degrees(angle))
        if draw_angles is not None:
            a, b = draw_angles
            start_angle = -math.degrees(a)
            if b < a:  # arc crosses the discontinuity at n*360
                b += math.tau
            span_angle = -math.degrees(b - a)
            ellipse.setStartAngle(int(start_angle * 16))  # angles stored as integers in 16ths of a degree units
            ellipse.setSpanAngle(int(span_angle * 16))
        ellipse.setData(CorrespondingDXFEntity, self.current_entity)
        self.scene.addItem(ellipse)

    def clear(self) -> None:
        self.scene.clear()

    def finalize(self) -> None:
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
    m11, m12, _, _ = matrix.get_row(0)
    m21, m22, _, _ = matrix.get_row(1)
    _, _, _, _ = matrix.get_row(2)
    tx, ty, _, _ = matrix.get_row(3)
    return qg.QTransform(m11, m12, 0,
                         m21, m22, 0,
                         tx, ty, 1)


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
