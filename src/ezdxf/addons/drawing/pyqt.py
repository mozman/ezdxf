# Created: 06.2020
# Copyright (c) 2020, Matthew Broadway
# License: MIT License
import math
from typing import Optional, Iterable

from PyQt5 import QtCore as qc, QtGui as qg, QtWidgets as qw

from ezdxf.addons.drawing.backend import Backend, prepare_string_for_rendering
from ezdxf.addons.drawing.text import FontMeasurements
from ezdxf.addons.drawing.type_hints import Color
from ezdxf.addons.drawing.properties import Properties
from ezdxf.math import Vector, Matrix44
from ezdxf.render import Path, Command


class _Point(qw.QAbstractGraphicsShapeItem):
    """ a point which is drawn 'cosmetically' (scale depends on view) """

    def __init__(self, x: float, y: float, radius: float, brush: qg.QBrush):
        super().__init__()
        self.pos = qc.QPointF(x, y)
        self.radius = radius
        self.setPen(qg.QPen(qc.Qt.NoPen))
        self.setBrush(brush)

    def paint(self, painter: qg.QPainter, option: qw.QStyleOptionGraphicsItem,
              widget: Optional[qw.QWidget] = None) -> None:
        view_scale = _get_x_scale(painter.transform())
        radius = self.radius / view_scale

        painter.setBrush(self.brush())
        painter.setPen(qc.Qt.NoPen)
        painter.drawEllipse(self.pos, radius, radius)

    def boundingRect(self) -> qc.QRectF:
        return qc.QRectF(self.pos, qc.QSizeF(1, 1))


# The key used to store the dxf entity corresponding to each graphics element
CorrespondingDXFEntity = 0
CorrespondingDXFParentStack = 1


class PyQtBackend(Backend):
    def __init__(self,
                 scene: qw.QGraphicsScene,
                 point_radius: float = 0.5,
                 *,
                 debug_draw_rect: bool = False):
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
        pen.setJoinStyle(qc.Qt.RoundJoin)
        return pen

    def _get_brush(self, properties: Properties) -> qg.QBrush:
        if properties.filling:
            return qg.QBrush(
                self._get_color(properties.color),
                qc.Qt.SolidPattern
            )
        else:
            return self._no_fill

    def _set_item_data(self, item: qw.QGraphicsItem) -> None:
        item.setData(CorrespondingDXFEntity, self.current_entity)
        parent_stack = tuple(e for e, props in self.entity_stack[:-1])
        item.setData(CorrespondingDXFParentStack, parent_stack)

    def set_background(self, color: Color):
        self.scene.setBackgroundBrush(qg.QBrush(self._get_color(color)))

    def draw_line(self, start: Vector, end: Vector,
                  properties: Properties) -> None:
        color = properties.color
        item = self.scene.addLine(
            start.x, start.y, end.x, end.y,
            self._get_pen(color)
        )
        self._set_item_data(item)

    def draw_path(self, path: Path, properties) -> None:
        qt_path = qg.QPainterPath()
        start = path.start
        qt_path.moveTo(start.x, start.y)
        for cmd in path:
            if cmd.type == Command.LINE_TO:
                end = cmd.end
                qt_path.lineTo(end.x, end.y)
            elif cmd.type == Command.CURVE_TO:
                end = cmd.end
                ctrl1 = cmd.ctrl1
                ctrl2 = cmd.ctrl2
                qt_path.cubicTo(
                    ctrl1.x, ctrl1.y, ctrl2.x, ctrl2.y, end.x, end.y
                )
            else:
                raise ValueError(f'Unknown path command: {cmd.type}')
        item = self.scene.addPath(
            qt_path,
            self._get_pen(properties.color),
            self._get_brush(properties),
        )
        self._set_item_data(item)

    def draw_point(self, pos: Vector, properties: Properties) -> None:
        brush = qg.QBrush(self._get_color(properties.color), qc.Qt.SolidPattern)
        item = _Point(pos.x, pos.y, self.point_radius, brush)
        self._set_item_data(item)
        self.scene.addItem(item)

    def draw_filled_polygon(self, points: Iterable[Vector],
                            properties: Properties) -> None:
        brush = self._get_brush(properties)
        polygon = qg.QPolygonF()
        for p in points:
            polygon.append(qc.QPointF(p.x, p.y))
        item = self.scene.addPolygon(polygon, self._no_line, brush)
        self._set_item_data(item)

    def draw_text(self, text: str, transform: Matrix44, properties: Properties,
                  cap_height: float) -> None:
        if not text.strip():
            return  # no point rendering empty strings
        text = prepare_string_for_rendering(text, self.current_entity.dxftype())

        scale = cap_height / self._font_measurements.cap_height
        transform = Matrix44.scale(scale, -scale, 0) @ transform

        path = qg.QPainterPath()
        path.addText(0, 0, self._font, text)
        path = _matrix_to_qtransform(transform).map(path)
        item = self.scene.addPath(path, self._no_line,
                                  self._get_color(properties.color))
        self._set_item_data(item)

    def get_font_measurements(self, cap_height: float,
                              font: str = None) -> FontMeasurements:
        return self._font_measurements.scale_from_baseline(
            desired_cap_height=cap_height)

    def get_text_line_width(self, text: str, cap_height: float,
                            font: str = None) -> float:
        if not text.strip():
            return 0

        dxftype = self.current_entity.dxftype() if self.current_entity else 'TEXT'
        text = prepare_string_for_rendering(text, dxftype)
        scale = cap_height / self._font_measurements.cap_height
        return _get_text_rect(self._font, text).right() * scale

    def clear(self) -> None:
        self.scene.clear()

    def finalize(self) -> None:
        super().finalize()
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        if self._debug_draw_rect:
            self.scene.addRect(self.scene.sceneRect(), self._get_pen('#000000'),
                               self._no_fill)


def _get_x_scale(t: qg.QTransform) -> float:
    return math.sqrt(t.m11() * t.m11() + t.m21() * t.m21())


def _matrix_to_qtransform(matrix: Matrix44) -> qg.QTransform:
    """ Qt also uses row-vectors so the translation elements are placed in the
    bottom row.

    This is only a simple conversion which assumes that although the
    transformation is 4x4,it does not involve the z axis.

    A more correct transformation could be implemented like so:
    https://stackoverflow.com/questions/10629737/convert-3d-4x4-rotation-matrix-into-2d
    """
    return qg.QTransform(*matrix.get_2d_transformation())


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
