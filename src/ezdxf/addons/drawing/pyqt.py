# Copyright (c) 2020-2021, Matthew Broadway
# License: MIT License
import math
from abc import ABCMeta
from typing import Optional, Iterable, Dict, Union, Tuple, no_type_check
from collections import defaultdict
from functools import lru_cache
from PyQt5 import QtCore as qc, QtGui as qg, QtWidgets as qw

from ezdxf.addons.drawing.backend import Backend, prepare_string_for_rendering
from ezdxf.addons.drawing.config import Configuration, LinePolicy, HatchPolicy
from ezdxf.tools.fonts import FontMeasurements
from ezdxf.addons.drawing.type_hints import Color
from ezdxf.addons.drawing.properties import Properties
from ezdxf.addons.drawing.line_renderer import AbstractLineRenderer
from ezdxf.tools import fonts
from ezdxf.math import Vec3, Matrix44
from ezdxf.path import Path, Command
from ezdxf.render.linetypes import LineTypeRenderer as EzdxfLineTypeRenderer
from ezdxf.tools.pattern import PatternAnalyser

PatternKey = Tuple[str, float]


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
CorrespondingDXFEntity = qc.Qt.UserRole + 0
CorrespondingDXFParentStack = qc.Qt.UserRole + 1


class PyQtBackend(Backend):
    def __init__(
        self,
        scene: Optional[qw.QGraphicsScene] = None,
        *,
        use_text_cache: bool = True,
        debug_draw_rect: bool = False,
        extra_lineweight_scaling: float = 2.0,
    ):
        """
        Args:
            extra_lineweight_scaling: compared to other backends,
                PyQt draws lines which appear thinner
        """
        super().__init__()
        self._scene = scene or qw.QGraphicsScene()  # avoids many type errors
        self._color_cache: Dict[Color, qg.QColor] = {}
        self._pattern_cache: Dict[PatternKey, int] = {}
        self._no_line = qg.QPen(qc.Qt.NoPen)
        self._no_fill = qg.QBrush(qc.Qt.NoBrush)

        self._text_renderer = TextRenderer(qg.QFont(), use_text_cache)
        self._line_renderer: PyQtLineRenderer
        self._extra_lineweight_scaling = extra_lineweight_scaling
        self._debug_draw_rect = debug_draw_rect

    def configure(self, config: Configuration) -> None:
        if config.min_lineweight is None:
            config = config.with_changes(min_lineweight=0.24)
        super().configure(config)
        if config.line_policy == LinePolicy.SOLID:
            self._line_renderer = InternalLineRenderer(
                self, config, solid_only=True
            )
        elif config.line_policy == LinePolicy.APPROXIMATE:
            self._line_renderer = InternalLineRenderer(
                self, config, solid_only=False
            )
        elif config.line_policy == LinePolicy.ACCURATE:
            self._line_renderer = EzdxfLineRenderer(self, config)
        else:
            raise ValueError(config.line_policy)

    def set_scene(self, scene: qw.QGraphicsScene):
        self._scene = scene

    def clear_text_cache(self):
        self._text_renderer.clear_cache()

    def _get_color(self, color: Color) -> qg.QColor:
        qt_color = self._color_cache.get(color, None)
        if qt_color is None:
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

    def _get_pen(self, properties: Properties) -> qg.QPen:
        """Returns a cosmetic pen with applied lineweight but without line type
        support.
        """
        px = (
            properties.lineweight
            / 0.3527
            * self.config.lineweight_scaling
            * self._extra_lineweight_scaling
        )
        pen = qg.QPen(self._get_color(properties.color), px)
        # Use constant width in pixel:
        pen.setCosmetic(True)
        pen.setJoinStyle(qc.Qt.RoundJoin)
        return pen

    def _get_brush(self, properties: Properties) -> qg.QBrush:
        filling = properties.filling
        if filling:
            if filling.type == filling.PATTERN:
                if (
                    self.config.hatch_policy
                    == HatchPolicy.SHOW_APPROXIMATE_PATTERN
                ):
                    # Default pattern scaling is not supported by PyQt:
                    key: PatternKey = (filling.name, filling.angle)
                    qt_pattern = self._pattern_cache.get(key)  # type: ignore
                    if qt_pattern is None:
                        qt_pattern = self._get_qt_pattern(filling.pattern)
                        self._pattern_cache[key] = qt_pattern
                elif self.config.hatch_policy == HatchPolicy.SHOW_SOLID:
                    qt_pattern = qc.Qt.SolidPattern
                elif self.config.hatch_policy == HatchPolicy.SHOW_OUTLINE:
                    return self._no_fill
                else:
                    raise ValueError(self.config.hatch_policy)
            else:
                qt_pattern = qc.Qt.SolidPattern

            return qg.QBrush(self._get_color(properties.color), qt_pattern)  # type: ignore
        else:
            return self._no_fill

    @staticmethod
    def _get_qt_pattern(pattern) -> int:
        pattern = PatternAnalyser(pattern)
        # knowledge of dark or light background would by handy:
        qt_pattern = qc.Qt.Dense4Pattern
        if pattern.all_angles(0):
            qt_pattern = qc.Qt.HorPattern
        elif pattern.all_angles(90):
            qt_pattern = qc.Qt.VerPattern
        elif pattern.has_angle(0) and pattern.has_angle(90):
            qt_pattern = qc.Qt.CrossPattern
        if pattern.all_angles(45):
            qt_pattern = qc.Qt.BDiagPattern
        elif pattern.all_angles(135):
            qt_pattern = qc.Qt.FDiagPattern
        elif pattern.has_angle(45) and pattern.has_angle(135):
            qt_pattern = qc.Qt.DiagCrossPattern
        return qt_pattern

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

    def draw_point(self, pos: Vec3, properties: Properties) -> None:
        """Draw a real dimensionless point."""
        brush = qg.QBrush(self._get_color(properties.color), qc.Qt.SolidPattern)
        item = _Point(pos.x, pos.y, brush)
        self._set_item_data(item)
        self._scene.addItem(item)

    def draw_line(self, start: Vec3, end: Vec3, properties: Properties) -> None:
        # PyQt draws a long line for a zero-length line:
        if start.isclose(end):
            self.draw_point(start, properties)
        else:
            item = self._line_renderer.draw_line(start, end, properties)  # type: ignore
            self._set_item_data(item)

    def draw_path(self, path: Path, properties: Properties) -> None:
        item = self._line_renderer.draw_path(path, properties)  # type: ignore
        self._set_item_data(item)

    def draw_filled_paths(
        self,
        paths: Iterable[Path],
        holes: Iterable[Path],
        properties: Properties,
    ) -> None:
        qt_path = qg.QPainterPath()
        for path in paths:
            try:
                path = path.counter_clockwise()
            except ValueError:  # cannot detect path orientation
                continue
            _extend_qt_path(qt_path, path)
        for path in holes:
            try:
                path = path.clockwise()
            except ValueError:  # cannot detect path orientation
                continue
            _extend_qt_path(qt_path, path)
        item = _CosmeticPath(qt_path)
        item.setPen(self._get_pen(properties))
        item.setBrush(self._get_brush(properties))
        self._scene.addItem(item)
        self._set_item_data(item)

    def draw_filled_polygon(
        self, points: Iterable[Vec3], properties: Properties
    ) -> None:
        brush = self._get_brush(properties)
        polygon = qg.QPolygonF()
        for p in points:
            polygon.append(qc.QPointF(p.x, p.y))
        item = _CosmeticPolygon(polygon)
        item.setPen(self._no_line)
        item.setBrush(brush)
        self._scene.addItem(item)
        self._set_item_data(item)

    def draw_text(
        self,
        text: str,
        transform: Matrix44,
        properties: Properties,
        cap_height: float,
    ) -> None:
        if not text.strip():
            return  # no point rendering empty strings
        text = prepare_string_for_rendering(text, self.current_entity.dxftype())  # type: ignore
        qfont = self.get_qfont(properties.font)
        scale = self._text_renderer.get_scale(cap_height, qfont)
        transform = Matrix44.scale(scale, -scale, 0) @ transform

        path = self._text_renderer.get_text_path(text, qfont)
        path = _matrix_to_qtransform(transform).map(path)
        item = self._scene.addPath(
            path, self._no_line, self._get_color(properties.color)
        )
        self._set_item_data(item)

    @lru_cache(maxsize=256)  # fonts.Font is a named tuple
    def get_qfont(self, font: fonts.FontFace) -> qg.QFont:
        qfont = self._text_renderer.default_font
        if font:
            family = font.family
            italic = "italic" in font.style.lower()
            weight = _map_weight(font.weight)
            qfont = qg.QFont(family, weight=weight, italic=italic)
            # INFO: setting the stretch value makes results worse!
            # qfont.setStretch(_map_stretch(font.stretch))
        return qfont

    def get_font_measurements(
        self, cap_height: float, font: fonts.FontFace = None
    ) -> FontMeasurements:
        qfont = self.get_qfont(font)
        return self._text_renderer.get_font_measurements(
            qfont
        ).scale_from_baseline(desired_cap_height=cap_height)

    def get_text_line_width(
        self, text: str, cap_height: float, font: fonts.FontFace = None
    ) -> float:
        if not text.strip():
            return 0

        dxftype = (
            self.current_entity.dxftype() if self.current_entity else "TEXT"
        )
        text = prepare_string_for_rendering(text, dxftype)
        qfont = self.get_qfont(font)
        scale = self._text_renderer.get_scale(cap_height, qfont)
        return self._text_renderer.get_text_rect(text, qfont).right() * scale

    def clear(self) -> None:
        self._scene.clear()

    def finalize(self) -> None:
        super().finalize()
        self._scene.setSceneRect(self._scene.itemsBoundingRect())
        if self._debug_draw_rect:
            properties = Properties()
            properties.color = "#000000"
            self._scene.addRect(
                self._scene.sceneRect(),
                self._get_pen(properties),
                self._no_fill,
            )


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
    brush.setTransform(painter.transform().inverted()[0].scale(1, -1))
    item.setBrush(brush)


@no_type_check
def _extend_qt_path(qt_path: qg.QPainterPath, path: Path) -> None:
    start = path.start
    qt_path.moveTo(start.x, start.y)
    for cmd in path:
        if cmd.type == Command.LINE_TO:
            end = cmd.end
            qt_path.lineTo(end.x, end.y)
        elif cmd.type == Command.CURVE4_TO:
            end = cmd.end
            ctrl1 = cmd.ctrl1
            ctrl2 = cmd.ctrl2
            qt_path.cubicTo(ctrl1.x, ctrl1.y, ctrl2.x, ctrl2.y, end.x, end.y)
        else:
            raise ValueError(f"Unknown path command: {cmd.type}")


# https://doc.qt.io/qt-5/qfont.html#Weight-enum
# QFont::Thin	0	0
# QFont::ExtraLight	12	12
# QFont::Light	25	25
# QFont::Normal	50	50
# QFont::Medium	57	57
# QFont::DemiBold	63	63
# QFont::Bold	75	75
# QFont::ExtraBold	81	81
# QFont::Black	87	87
def _map_weight(weight: Union[str, int]) -> int:
    if isinstance(weight, str):
        weight = fonts.weight_name_to_value(weight)
    value = int((weight / 10) + 10)  # normal: 400 -> 50
    return min(max(0, value), 99)


# https://doc.qt.io/qt-5/qfont.html#Stretch-enum
StretchMapping = {
    "ultracondensed": 50,
    "extracondensed": 62,
    "condensed": 75,
    "semicondensed": 87,
    "unstretched": 100,
    "semiexpanded": 112,
    "expanded": 125,
    "extraexpanded": 150,
    "ultraexpanded": 200,
}


def _map_stretch(stretch: str) -> int:
    return StretchMapping.get(stretch.lower(), 100)


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


class TextRenderer:
    def __init__(self, font: qg.QFont, use_cache: bool):
        self._default_font = font
        self._use_cache = use_cache

        # Each font has its own text path cache
        # key is QFont.key()
        self._text_path_cache: Dict[
            str, Dict[str, qg.QPainterPath]
        ] = defaultdict(dict)

        # Each font has its own font measurements cache
        # key is QFont.key()
        self._font_measurement_cache: Dict[str, FontMeasurements] = {}

    @property
    def default_font(self) -> qg.QFont:
        return self._default_font

    def clear_cache(self):
        self._text_path_cache.clear()

    def get_scale(self, desired_cap_height: float, font: qg.QFont) -> float:
        measurements = self.get_font_measurements(font)
        return desired_cap_height / measurements.cap_height

    def get_font_measurements(self, font: qg.QFont) -> FontMeasurements:
        # None is the default font.
        key = font.key() if font is not None else None
        measurements = self._font_measurement_cache.get(key)
        if measurements is None:
            upper_x = self.get_text_rect("X", font)
            lower_x = self.get_text_rect("x", font)
            lower_p = self.get_text_rect("p", font)
            baseline = lower_x.bottom()
            measurements = FontMeasurements(
                baseline=baseline,
                cap_height=baseline - upper_x.top(),
                x_height=baseline - lower_x.top(),
                descender_height=lower_p.bottom() - baseline,
            )
            self._font_measurement_cache[key] = measurements
        return measurements

    def get_text_path(self, text: str, font: qg.QFont) -> qg.QPainterPath:
        # None is the default font
        key = font.key() if font is not None else None
        cache = self._text_path_cache[key]  # defaultdict(dict)
        path = cache.get(text, None)
        if path is None:
            if font is None:
                font = self._default_font
            path = qg.QPainterPath()
            path.addText(0, 0, font, text)
            if self._use_cache:
                cache[text] = path
        return path

    def get_text_rect(self, text: str, font: qg.QFont) -> qc.QRectF:
        # no point caching the bounding rect calculation, it is very cheap
        return self.get_text_path(text, font).boundingRect()


# noinspection PyProtectedMember
class PyQtLineRenderer(AbstractLineRenderer, metaclass=ABCMeta):
    def __init__(self, backend: PyQtBackend, config: Configuration):
        super().__init__(config)
        self._backend = backend

    @property
    def scene(self) -> qw.QGraphicsScene:
        return self._backend._scene

    @property
    def no_fill(self) -> qg.QBrush:
        return self._backend._no_fill

    def get_color(self, color: Color) -> qg.QColor:
        return self._backend._get_color(color)

    def get_pen(self, properties: Properties) -> qg.QPen:
        return self._backend._get_pen(properties)


# Just guessing here: this values assume a cosmetic pen!
ISO_LIN_PATTERN_FACTOR = 15
ANSI_LIN_PATTERN_FACTOR = ISO_LIN_PATTERN_FACTOR * 2.54


class InternalLineRenderer(PyQtLineRenderer):
    """PyQt internal linetype rendering"""

    def __init__(
        self, backend: PyQtBackend, config: Configuration, solid_only: bool
    ):
        super().__init__(backend, config)
        self._solid_only = solid_only

    @property
    def measurement_scale(self) -> float:
        return (
            ISO_LIN_PATTERN_FACTOR
            if self._config.measurement
            else ISO_LIN_PATTERN_FACTOR
        )

    def get_pen(self, properties: Properties) -> qg.QPen:
        pen = super().get_pen(properties)
        if not self._solid_only and len(properties.linetype_pattern) > 1:
            # The dash pattern is specified in units of the pens width; e.g. a
            # dash of length 5 in width 10 is 50 pixels long.
            pattern = self.pattern(properties)
            if len(pattern):
                pen.setDashPattern(pattern)
        return pen

    def draw_line(self, start: Vec3, end: Vec3, properties: Properties, z=0):
        return self.scene.addLine(
            start.x, start.y, end.x, end.y, self.get_pen(properties)
        )

    def draw_path(self, path: Path, properties: Properties, z=0):
        qt_path = qg.QPainterPath()
        _extend_qt_path(qt_path, path)
        return self.scene.addPath(
            qt_path,
            self.get_pen(properties),
            self.no_fill,
        )


class EzdxfLineRenderer(PyQtLineRenderer):
    """Replicate AutoCAD linetype rendering oriented on drawing units and
    various ltscale factors. This rendering method break lines into small
    segments which causes a longer rendering time!
    """

    def draw_line(self, start: Vec3, end: Vec3, properties: Properties, z=0):
        pattern = self.pattern(properties)
        pen = self.get_pen(properties)
        if len(pattern) < 2:
            return self.scene.addLine(start.x, start.y, end.x, end.y, pen)
        else:
            add_line = self.scene.addLine
            renderer = EzdxfLineTypeRenderer(pattern)
            return [
                add_line(s.x, s.y, e.x, e.y, pen)
                for s, e in renderer.line_segment(start, end)
                # PyQt has problems with very short lines:
                if not s.isclose(e)
            ]

    def draw_path(self, path, properties: Properties, z=0):
        pattern = self.pattern(properties)
        pen = self.get_pen(properties)
        if len(pattern) < 2:
            qt_path = qg.QPainterPath()
            _extend_qt_path(qt_path, path)
            return self.scene.addPath(qt_path, pen, self.no_fill)
        else:
            add_line = self.scene.addLine
            renderer = EzdxfLineTypeRenderer(pattern)
            segments = renderer.line_segments(
                path.flattening(
                    self._config.max_flattening_distance, segments=16
                )
            )
            return [
                add_line(s.x, s.y, e.x, e.y, pen)
                for s, e in segments
                # PyQt has problems with very short lines:
                if not s.isclose(e)
            ]
