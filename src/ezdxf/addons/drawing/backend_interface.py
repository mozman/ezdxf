# Created: 06.2020
# Copyright (c) 2020, Matthew Broadway
# License: MIT License
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, TYPE_CHECKING, Iterable

from ezdxf.addons.drawing.properties import Properties
from ezdxf.addons.drawing.type_hints import Color, Radians
from ezdxf.entities import DXFGraphic
from ezdxf.math import Vector, Matrix44, BSpline

if TYPE_CHECKING:
    from ezdxf.addons.drawing.text import FontMeasurements


class DrawingBackend(ABC):
    def __init__(self):
        self._current_entity = None
        self._current_entity_stack = ()
        self._path_mode = False

    def set_current_entity(self, entity: Optional[DXFGraphic], parent_stack: Tuple[DXFGraphic, ...] = ()) -> None:
        self._current_entity = entity
        self._current_entity_stack = parent_stack

    @property
    def current_entity(self) -> Optional[DXFGraphic]:
        """ obtain the current entity being drawn """
        return self._current_entity

    @property
    def current_entity_stack(self) -> Tuple[DXFGraphic, ...]:
        """ When the entity is virtual, the stack of entities which were exploded to obtain the entity.
        When the entity is 'real', an empty tuple.
        """
        return self._current_entity_stack

    @property
    def is_path_mode(self) -> bool:
        return self._path_mode

    @abstractmethod
    def set_background(self, color: Color) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw_line(self, start: Vector, end: Vector, properties: Properties) -> None:
        raise NotImplementedError

    def start_path(self):
        """ Called when a polyline path is encountered. Any draw calls up until end_path() is called,
        can be buffered into a single un-broken path if the backend supports this.
        """
        assert self._path_mode is False, 'Nested paths not supported.'
        self._path_mode = True

    def end_path(self):
        assert self._path_mode is True, 'Path mode not started.'
        self._path_mode = False

    def draw_line_string(self, vertices: Iterable[Vector], close: bool, properties: Properties) -> None:
        """ Draw efficient multiple lines as connected polyline.

        Override in backend for a more efficient implementation.

        """
        self.start_path()
        prev = None
        first = None
        for vertex in vertices:
            if prev is None:
                prev = vertex
                first = vertex
            else:
                self.draw_line(prev, vertex, properties)
                prev = vertex
        if close and prev is not None and not prev.isclose(first):
            self.draw_line(prev, first, properties)
        self.end_path()

    @property
    def has_spline_support(self):
        return False

    def draw_spline(self, spline: BSpline, properties: Properties) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw_point(self, pos: Vector, properties: Properties) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw_filled_polygon(self, points: Iterable[Vector], properties: Properties) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw_text(self, text: str, transform: Matrix44, properties: Properties, cap_height: float) -> None:
        """ draw a single line of text with the anchor point at the baseline left point """
        raise NotImplementedError

    @abstractmethod
    def get_font_measurements(self, cap_height: float) -> 'FontMeasurements':
        """ note: backends might want to cache the results of these calls """
        raise NotImplementedError

    @abstractmethod
    def get_text_line_width(self, text: str, cap_height: float) -> float:
        """ get the width of a single line of text """
        raise NotImplementedError

    @abstractmethod
    def draw_arc(self, center: Vector, width: float, height: float, angle: Radians,
                 draw_angles: Optional[Tuple[Radians, Radians]], properties: Properties) -> None:
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """ clear the canvas. Does not reset the internal state of the backend. Make sure that the previous drawing
        is finished before clearing.
        """
        raise NotImplementedError

    def finalize(self) -> None:
        assert self._path_mode is False, 'Missing end of path.'
