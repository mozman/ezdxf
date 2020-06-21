# Created: 06.2020
# Copyright (c) 2020, Matthew Broadway
# License: MIT License
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, TYPE_CHECKING

from ezdxf.addons.drawing.type_hints import Color, Radians
from ezdxf.entities import DXFGraphic
from ezdxf.math import Vector, Matrix44

if TYPE_CHECKING:
    from ezdxf.addons.drawing.text import FontMeasurements


class DrawingBackend(ABC):
    def __init__(self):
        self._current_entity = None

    def set_current_entity(self, entity: Optional[DXFGraphic]) -> None:
        self._current_entity = entity

    @property
    def current_entity(self) -> Optional[DXFGraphic]:
        """ obtain the current entity being drawn """
        return self._current_entity

    @abstractmethod
    def set_background(self, color: Color) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw_line(self, start: Vector, end: Vector, color: Color) -> None:
        raise NotImplementedError

    def draw_line_string(self, points: List[Vector], color: Color) -> None:
        for a, b in zip(points, points[1:]):
            self.draw_line(a, b, color)

    @abstractmethod
    def draw_point(self, pos: Vector, color: Color) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw_filled_polygon(self, points: List[Vector], color: Color) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw_text(self, text: str, transform: Matrix44, color: Color, cap_height: float) -> None:
        """ draw a single line of text with the anchor point at the baseline left point """
        raise NotImplementedError

    @abstractmethod
    def get_font_measurements(self, cap_height: float) -> "FontMeasurements":
        """ note: backends might want to cache the results of these calls """
        raise NotImplementedError

    @abstractmethod
    def get_text_line_width(self, text: str, cap_height: float) -> float:
        """ get the width of a single line of text """
        raise NotImplementedError

    @abstractmethod
    def draw_arc(self, center: Vector, width: float, height: float, angle: Radians,
                 draw_angles: Optional[Tuple[Radians, Radians]], color: Color) -> None:
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        raise NotImplementedError

    def finalize(self) -> None:
        pass
