# Created: 06.2020
# Copyright (c) 2020, Matthew Broadway
# License: MIT License
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, TYPE_CHECKING, Iterable

from ezdxf.addons.drawing.colors import ColorContext
from ezdxf.addons.drawing.type_hints import Color, Radians
from ezdxf.entities import DXFGraphic
from ezdxf.math import Vector, Matrix44, BSpline

if TYPE_CHECKING:
    from ezdxf.addons.drawing.text import FontMeasurements
    from ezdxf.eztypes import Hatch, Spline, LWPolyline


class DrawingBackend(ABC):
    def __init__(self):
        self._current_entity = None
        self._current_entity_stack = ()
        self._polyline_nesting_depth = 0

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
    def is_drawing_polyline(self) -> bool:
        return self._polyline_nesting_depth > 0

    @abstractmethod
    def set_background(self, color: Color) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw_line(self, start: Vector, end: Vector, color: Color) -> None:
        raise NotImplementedError

    def start_polyline(self):
        """ Called when a polyline is encountered. Any draw calls up until the next time _polyline_nesting_depth drops
        to 0 can be buffered into a single un-broken path if the backend supports this.
        """
        # using an integer rather than a boolean to allow nested polylines (e.g. spline as part of a polyline)
        self._polyline_nesting_depth += 1

    def end_polyline(self):
        self._polyline_nesting_depth -= 1
        assert self._polyline_nesting_depth >= 0

    @property
    def has_spline_support(self):
        return False

    def draw_spline(self, spline: BSpline, color: Color) -> None:
        raise NotImplementedError

    @property
    def has_hatch_support(self):
        return False

    def draw_hatch(self, hatch: 'Hatch', color: Color) -> None:
        raise NotImplementedError

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
        """ clear the canvas. Does not reset the internal state of the backend. Make sure that the previous drawing
        is finished before clearing.
        """
        raise NotImplementedError

    def finalize(self) -> None:
        assert self._polyline_nesting_depth == 0

    def ignored_entity(self, entity: DXFGraphic, colors: ColorContext):
        print(f'ignoring {entity.dxftype()} entity')
