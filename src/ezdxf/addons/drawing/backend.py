# Created: 06.2020
# Copyright (c) 2020, Matthew Broadway
# License: MIT License
from abc import ABC, abstractmethod
from typing import Optional, Tuple, TYPE_CHECKING, Iterable, List, Sequence

from ezdxf.addons.drawing.properties import Properties
from ezdxf.addons.drawing.type_hints import Color, THole
from ezdxf.entities import DXFGraphic
from ezdxf.entities.mtext import replace_non_printable_characters
from ezdxf.math import Vector, Matrix44
from ezdxf.render.path import Path

if TYPE_CHECKING:
    from ezdxf.addons.drawing.text import FontMeasurements


class Backend(ABC):
    def __init__(self):
        self.entity_stack: List[Tuple[DXFGraphic, Properties]] = []
        # Approximate cubic Bèzier-curves by `n` segments, only used for basic
        # back-ends without draw_path() support.
        self.bezier_approximation_count = 32
        # Max flattening distance in drawing units: the backend implementation
        # should calculate an appropriate value, like 1 screen- or paper pixel
        # on the output medium, but converted this value into drawing units.
        self.max_flattening_distance = 0.01

    def enter_entity(self, entity: DXFGraphic, properties: Properties) -> None:
        self.entity_stack.append((entity, properties))

    def exit_entity(self, entity: DXFGraphic) -> None:
        e, p = self.entity_stack.pop()
        assert e is entity, 'entity stack mismatch'

    @property
    def current_entity(self) -> Optional[DXFGraphic]:
        """ Obtain the current entity being drawn """
        return self.entity_stack[-1][0] if self.entity_stack else None

    @abstractmethod
    def set_background(self, color: Color) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw_point(self, pos: Vector, properties: Properties) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw_line(self, start: Vector, end: Vector,
                  properties: Properties) -> None:
        raise NotImplementedError

    def draw_path(self, path: Path, properties: Properties) -> None:
        """ Draw an outline path (connected string of line segments and Bezier
        curves).

        The :meth:`draw_path` implementation is a fall-back implementation
        which approximates Bezier curves by flattening as line segments.
        Backends can override this method if better path drawing functionality
        is available for that backend.

        """
        if len(path):
            vertices = iter(
                path.flattening(distance=self.max_flattening_distance)
            )
            prev = next(vertices)
            for vertex in vertices:
                self.draw_line(prev, vertex, properties)
                prev = vertex

    def draw_filled_path(self, path: Path, holes: Sequence[THole],
                         properties: Properties) -> None:
        """ Draw a filled path (connected string of line segments and Bezier
        curves) with holes.

        The default implementation draws a filled polygon without holes by the
        :meth:`draw_filled_polygon` method. Backends can override this method if
        filled polygon with hole support is available.

        The HATCH fill strategies ("ignore", "outermost", "ignore") are resolved
        by the frontend e.g. the holes sequence is empty for the "ignore"
        strategy and for the "outermost" strategy, holes do not contain nested
        holes.

        Args:
            path: the exterior (outline) boundary path
            holes: holes as sequence THole objects, each hole can contain
                nested holes.
            properties: HATCH properties

        """
        self.draw_filled_polygon(
            path.flattening(distance=self.max_flattening_distance),
            properties
        )

    @abstractmethod
    def draw_filled_polygon(self, points: Iterable[Vector],
                            properties: Properties) -> None:
        """ Fill a polygon whose outline is defined by the given points.
        Used to draw entities with simple outlines where :meth:`draw_path` may
        be an inefficient way to draw such a polygon.
        """
        raise NotImplementedError

    @abstractmethod
    def draw_text(self, text: str, transform: Matrix44, properties: Properties,
                  cap_height: float) -> None:
        """ Draw a single line of text with the anchor point at the baseline
        left point.
        """
        raise NotImplementedError

    @abstractmethod
    def get_font_measurements(self, cap_height: float,
                              font: str = None) -> 'FontMeasurements':
        """ Note: backends might want to cache the results of these calls """
        raise NotImplementedError

    @abstractmethod
    def get_text_line_width(self, text: str, cap_height: float,
                            font: str = None) -> float:
        """ Get the width of a single line of text. """
        # https://stackoverflow.com/questions/32555015/how-to-get-the-visual-length-of-a-text-string-in-python
        # https://stackoverflow.com/questions/4190667/how-to-get-width-of-a-truetype-font-character-in-1200ths-of-an-inch-with-python
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """ Clear the canvas. Does not reset the internal state of the backend.
        Make sure that the previous drawing is finished before clearing.

        """
        raise NotImplementedError

    def finalize(self) -> None:
        pass


def prepare_string_for_rendering(text: str, dxftype: str) -> str:
    assert '\n' not in text, 'not a single line of text'
    if dxftype in {'TEXT', 'ATTRIB'}:
        text = replace_non_printable_characters(text, replacement='?')
        text = text.replace('\t', '?')
    elif dxftype == 'MTEXT':
        text = replace_non_printable_characters(text, replacement='▯')
        text = text.replace('\t', '        ')
    else:
        raise TypeError(dxftype)
    return text
