# Copyright (c) 2020-2023, Matthew Broadway
# License: MIT License
# mypy: ignore_errors=True
from __future__ import annotations
from typing import Optional, Iterable
import math

from ezdxf.addons.xqt import QtCore as qc, QtGui as qg, QtWidgets as qw
from ezdxf.addons.drawing.backend import Backend
from ezdxf.addons.drawing.config import Configuration
from ezdxf.addons.drawing.type_hints import Color
from ezdxf.addons.drawing.properties import BackendProperties
from ezdxf.math import Vec3, Matrix44
from ezdxf.path import Path, to_qpainter_path


class _Point(qw.QAbstractGraphicsShapeItem):
    """A dimensionless point which is drawn 'cosmetically' (scale depends on
    view)
    """

    def __init__(self, x: float, y: float, brush: qg.QBrush):
        super().__init__()
        self.location = qc.QPointF(x, y)
        self.radius = 1.0
        self.setPen(qg.QPen(qc.Qt.NoPen))
        self.setBrush(brush)

    def paint(
        self,
        painter: qg.QPainter,
        option: qw.QStyleOptionGraphicsItem,
        widget: Optional[qw.QWidget] = None,
    ) -> None:
        view_scale = _get_x_scale(painter.transform())
        radius = self.radius / view_scale
        painter.setBrush(self.brush())
        painter.setPen(qc.Qt.NoPen)
        painter.drawEllipse(self.location, radius, radius)

    def boundingRect(self) -> qc.QRectF:
        return qc.QRectF(self.location, qc.QSizeF(1, 1))


# The key used to store the dxf entity corresponding to each graphics element
CorrespondingDXFEntity = qc.Qt.UserRole + 0  # type: ignore
CorrespondingDXFParentStack = qc.Qt.UserRole + 1  # type: ignore


class PyQtBackend(Backend):
    """
    Backend which uses the :mod:`PySide6` package to implement an interactive
    viewer. The :mod:`PyQt5` package can be used as fallback if the :mod:`PySide6`
    package is not available.

    Args:
        scene: drawing canvas of type :class:`QtWidgets.QGraphicsScene`,
            if ``None`` a new canvas will be created
    """

    def __init__(
        self,
        scene: Optional[qw.QGraphicsScene] = None,
    ):
        super().__init__()
        self._scene = scene or qw.QGraphicsScene()  # avoids many type errors
        self._color_cache: dict[Color, qg.QColor] = {}
        self._no_line = qg.QPen(qc.Qt.NoPen)
        self._no_fill = qg.QBrush(qc.Qt.NoBrush)

    def configure(self, config: Configuration) -> None:
        if config.min_lineweight is None:
            config = config.with_changes(min_lineweight=0.24)
        super().configure(config)

    def set_scene(self, scene: qw.QGraphicsScene):
        self._scene = scene

    def _add_item(self, item):
        self._set_item_data(item)
        self._scene.addItem(item)

    def _get_color(self, color: Color) -> qg.QColor:
        try:
            return self._color_cache[color]
        except KeyError:
            pass
        if len(color) == 7:
            qt_color = qg.QColor(color)  # '#RRGGBB'
        elif len(color) == 9:
            rgb = color[1:7]
            alpha = color[7:9]
            qt_color = qg.QColor(f"#{alpha}{rgb}")  # '#AARRGGBB'
        else:
            raise TypeError(color)

        self._color_cache[color] = qt_color
        return qt_color

    def _get_pen(self, properties: BackendProperties) -> qg.QPen:
        """Returns a cosmetic pen with applied lineweight but without line type
        support.
        """
        px = properties.lineweight / 0.3527 * self.config.lineweight_scaling
        pen = qg.QPen(self._get_color(properties.color), px)
        # Use constant width in pixel:
        pen.setCosmetic(True)
        pen.setJoinStyle(qc.Qt.RoundJoin)
        return pen

    def _get_fill_brush(self, color: Color) -> qg.QBrush:
        return qg.QBrush(self._get_color(color), qc.Qt.SolidPattern)  # type: ignore

    def _set_item_data(self, item: qw.QGraphicsItem) -> None:
        parent_stack = tuple(e for e, props in self.entity_stack[:-1])
        current_entity = self.current_entity
        if isinstance(item, list):
            for item_ in item:
                item_.setData(CorrespondingDXFEntity, current_entity)
                item_.setData(CorrespondingDXFParentStack, parent_stack)
        else:
            item.setData(CorrespondingDXFEntity, current_entity)
            item.setData(CorrespondingDXFParentStack, parent_stack)

    def set_background(self, color: Color):
        self._scene.setBackgroundBrush(qg.QBrush(self._get_color(color)))

    def draw_point(self, pos: Vec3, properties: BackendProperties) -> None:
        """Draw a real dimensionless point."""
        brush = self._get_fill_brush(properties.color)
        item = _Point(pos.x, pos.y, brush)
        self._set_item_data(item)
        self._add_item(item)

    def draw_line(self, start: Vec3, end: Vec3, properties: BackendProperties) -> None:
        # PyQt draws a long line for a zero-length line:
        if start.isclose(end):
            self.draw_point(start, properties)
        else:
            item = qw.QGraphicsLineItem(start.x, start.y, end.x, end.y)
            item.setPen(self._get_pen(properties))
            self._add_item(item)

    def draw_solid_lines(
        self,
        lines: Iterable[tuple[Vec3, Vec3]],
        properties: BackendProperties,
    ):
        """Fast method to draw a bunch of solid lines with the same properties."""
        pen = self._get_pen(properties)
        add_line = self._add_item
        for s, e in lines:
            if s.isclose(e):
                self.draw_point(s, properties)
            else:
                item = qw.QGraphicsLineItem(s.x, s.y, e.x, e.y)
                item.setPen(pen)
                add_line(item)

    def draw_path(self, path: Path, properties: BackendProperties) -> None:
        item = qw.QGraphicsPathItem(to_qpainter_path([path]))
        item.setPen(self._get_pen(properties))
        item.setBrush(self._no_fill)
        self._add_item(item)

    def draw_filled_paths(
        self,
        paths: Iterable[Path],
        holes: Iterable[Path],
        properties: BackendProperties,
    ) -> None:
        oriented_paths: list[Path] = []
        for path in paths:
            try:
                path = path.counter_clockwise()
            except ValueError:  # cannot detect path orientation
                continue
            oriented_paths.append(path)
        for path in holes:
            try:
                path = path.clockwise()
            except ValueError:  # cannot detect path orientation
                continue
            oriented_paths.append(path)
        if len(oriented_paths) == 0:
            return
        item = _CosmeticPath(to_qpainter_path(oriented_paths))
        item.setPen(self._get_pen(properties))
        item.setBrush(self._get_fill_brush(properties.color))
        self._add_item(item)

    def draw_filled_polygon(
        self, points: Iterable[Vec3], properties: BackendProperties
    ) -> None:
        brush = self._get_fill_brush(properties.color)
        polygon = qg.QPolygonF()
        for p in points:
            polygon.append(qc.QPointF(p.x, p.y))
        item = _CosmeticPolygon(polygon)
        item.setPen(self._no_line)
        item.setBrush(brush)
        self._add_item(item)

    def clear(self) -> None:
        self._scene.clear()

    def finalize(self) -> None:
        super().finalize()
        self._scene.setSceneRect(self._scene.itemsBoundingRect())


class _CosmeticPath(qw.QGraphicsPathItem):
    def paint(
        self,
        painter: qg.QPainter,
        option: qw.QStyleOptionGraphicsItem,
        widget: Optional[qw.QWidget] = None,
    ) -> None:
        _set_cosmetic_brush(self, painter)
        super().paint(painter, option, widget)


class _CosmeticPolygon(qw.QGraphicsPolygonItem):
    def paint(
        self,
        painter: qg.QPainter,
        option: qw.QStyleOptionGraphicsItem,
        widget: Optional[qw.QWidget] = None,
    ) -> None:
        _set_cosmetic_brush(self, painter)
        super().paint(painter, option, widget)


def _set_cosmetic_brush(
    item: qw.QAbstractGraphicsShapeItem, painter: qg.QPainter
) -> None:
    """like a cosmetic pen, this sets the brush pattern to appear the same independent of the view"""
    brush = item.brush()
    # scale by -1 in y because the view is always mirrored in y and undoing the view transformation entirely would make
    # the hatch mirrored w.r.t the view
    brush.setTransform(painter.transform().inverted()[0].scale(1, -1))  # type: ignore
    item.setBrush(brush)


def _get_x_scale(t: qg.QTransform) -> float:
    return math.sqrt(t.m11() * t.m11() + t.m21() * t.m21())


def _matrix_to_qtransform(matrix: Matrix44) -> qg.QTransform:
    """Qt also uses row-vectors so the translation elements are placed in the
    bottom row.

    This is only a simple conversion which assumes that although the
    transformation is 4x4,it does not involve the z axis.

    A more correct transformation could be implemented like so:
    https://stackoverflow.com/questions/10629737/convert-3d-4x4-rotation-matrix-into-2d
    """
    return qg.QTransform(*matrix.get_2d_transformation())
