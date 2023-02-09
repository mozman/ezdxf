# Copyright (c) 2020-2022, Matthew Broadway
# License: MIT License
from __future__ import annotations
from abc import ABC, abstractmethod, ABCMeta
from typing import (
    Optional,
    TYPE_CHECKING,
    Iterable,
)

from ezdxf.addons.drawing.config import Configuration
from ezdxf.addons.drawing.properties import Properties
from ezdxf.addons.drawing.type_hints import Color
from ezdxf.entities import DXFGraphic
from ezdxf.tools.text import replace_non_printable_characters
from ezdxf.math import Vec3, Matrix44
from ezdxf.path import Path

if TYPE_CHECKING:
    from ezdxf.tools.fonts import FontFace, FontMeasurements


class BackendInterface(ABC):
    """the public interface for the rendering backend."""

    @abstractmethod
    def configure(self, config: Configuration) -> None:
        raise NotImplementedError

    @abstractmethod
    def enter_entity(self, entity: DXFGraphic, properties: Properties) -> None:
        raise NotImplementedError

    @abstractmethod
    def exit_entity(self, entity: DXFGraphic) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_background(self, color: Color) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw_point(self, pos: Vec3, properties: Properties) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw_line(self, start: Vec3, end: Vec3, properties: Properties) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw_solid_lines(
        self, lines: Iterable[tuple[Vec3, Vec3]], properties: Properties
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw_path(self, path: Path, properties: Properties) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw_filled_paths(
        self,
        paths: Iterable[Path],
        holes: Iterable[Path],
        properties: Properties,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw_filled_polygon(
        self, points: Iterable[Vec3], properties: Properties
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw_text(
        self,
        text: str,
        transform: Matrix44,
        properties: Properties,
        cap_height: float,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_font_measurements(
        self, cap_height: float, font: Optional[FontFace] = None
    ) -> FontMeasurements:
        raise NotImplementedError

    @abstractmethod
    def get_text_line_width(
        self, text: str, cap_height: float, font: Optional[FontFace] = None
    ) -> float:
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def finalize(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_clipping_path(
        self, path: Optional[Path] = None, scale: float = 1.0
    ) -> bool:
        """Set the current clipping path.
        Returns True if a clipping path is supported.
        An empty path or None removes the clipping path.
        The `scale` is the scaling factor from modelspace to viewport.
        """
        raise NotImplementedError


class Backend(BackendInterface, metaclass=ABCMeta):
    def __init__(self) -> None:
        self.entity_stack: list[tuple[DXFGraphic, Properties]] = []
        self.config: Configuration

    def configure(self, config: Configuration) -> None:
        self.config = config

    def enter_entity(self, entity: DXFGraphic, properties: Properties) -> None:
        self.entity_stack.append((entity, properties))

    def exit_entity(self, entity: DXFGraphic) -> None:
        e, p = self.entity_stack.pop()
        assert e is entity, "entity stack mismatch"

    @property
    def current_entity(self) -> Optional[DXFGraphic]:
        """Obtain the current entity being drawn"""
        return self.entity_stack[-1][0] if self.entity_stack else None

    @abstractmethod
    def set_background(self, color: Color) -> None:
        raise NotImplementedError

    def set_clipping_path(
        self, path: Optional[Path] = None, scale: float = 1.0
    ) -> bool:
        """Clipping path is not supported by default."""
        return False

    @abstractmethod
    def draw_point(self, pos: Vec3, properties: Properties) -> None:
        """Draw a real dimensionless point, because not all backends support
        zero-length lines!
        """
        raise NotImplementedError

    @abstractmethod
    def draw_line(self, start: Vec3, end: Vec3, properties: Properties) -> None:
        raise NotImplementedError

    def draw_solid_lines(
        self, lines: Iterable[tuple[Vec3, Vec3]], properties: Properties
    ) -> None:
        """Fast method to draw a bunch of solid lines with the same properties."""
        # Must be overridden by the backend to gain a performance benefit.
        # This is the default implementation to ensure compatibility with
        # existing backends.
        for s, e in lines:
            if e.isclose(s):
                self.draw_point(s, properties)
            else:
                self.draw_line(s, e, properties)

    def draw_path(self, path: Path, properties: Properties) -> None:
        """Draw an outline path (connected string of line segments and Bezier
        curves).

        The :meth:`draw_path` implementation is a fall-back implementation
        which approximates Bezier curves by flattening as line segments.
        Backends can override this method if better path drawing functionality
        is available for that backend.

        """
        if len(path):
            vertices = iter(
                path.flattening(distance=self.config.max_flattening_distance)
            )
            prev = next(vertices)
            for vertex in vertices:
                self.draw_line(prev, vertex, properties)
                prev = vertex

    def draw_filled_paths(
        self,
        paths: Iterable[Path],
        holes: Iterable[Path],
        properties: Properties,
    ) -> None:
        """Draw multiple filled paths (connected string of line segments and
        Bezier curves) with holes.

        The strategy to draw multiple paths at once was chosen, because a HATCH
        entity can contain multiple unconnected areas and the holes are not easy
        to assign to an external path.

        The idea is to put all filled areas into `paths` (counter-clockwise
        winding) and all holes into `holes` (clockwise winding) and look what
        the backend does with this information.

        The HATCH fill strategies ("ignore", "outermost", "ignore") are resolved
        by the frontend e.g. the holes sequence is empty for the "ignore"
        strategy and for the "outermost" strategy, holes do not contain nested
        holes.

        The default implementation draws all paths as filled polygon without
        holes by the :meth:`draw_filled_polygon` method. Backends can override
        this method if filled polygon with hole support is available.

        Args:
            paths: sequence of exterior paths (counter-clockwise winding)
            holes: sequence of holes (clockwise winding)
            properties: HATCH properties

        """
        for path in paths:
            self.draw_filled_polygon(
                path.flattening(distance=self.config.max_flattening_distance),
                properties,
            )

    @abstractmethod
    def draw_filled_polygon(
        self, points: Iterable[Vec3], properties: Properties
    ) -> None:
        """Fill a polygon whose outline is defined by the given points.
        Used to draw entities with simple outlines where :meth:`draw_path` may
        be an inefficient way to draw such a polygon.
        """
        raise NotImplementedError

    @abstractmethod
    def draw_text(
        self,
        text: str,
        transform: Matrix44,
        properties: Properties,
        cap_height: float,
    ) -> None:
        """Draw a single line of text with the anchor point at the baseline
        left point.
        """
        raise NotImplementedError

    @abstractmethod
    def get_font_measurements(
        self, cap_height: float, font: Optional[FontFace] = None
    ) -> "FontMeasurements":
        """Note: backends might want to cache the results of these calls"""
        raise NotImplementedError

    @abstractmethod
    def get_text_line_width(
        self, text: str, cap_height: float, font: Optional[FontFace] = None
    ) -> float:
        """Get the width of a single line of text."""
        # https://stackoverflow.com/questions/32555015/how-to-get-the-visual-length-of-a-text-string-in-python
        # https://stackoverflow.com/questions/4190667/how-to-get-width-of-a-truetype-font-character-in-1200ths-of-an-inch-with-python
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """Clear the canvas. Does not reset the internal state of the backend.
        Make sure that the previous drawing is finished before clearing.

        """
        raise NotImplementedError

    def finalize(self) -> None:
        pass


def prepare_string_for_rendering(text: str, dxftype: str) -> str:
    assert "\n" not in text, "not a single line of text"
    if dxftype in {"TEXT", "ATTRIB", "ATTDEF"}:
        text = replace_non_printable_characters(text, replacement="?")
        text = text.replace("\t", "?")
    elif dxftype == "MTEXT":
        text = replace_non_printable_characters(text, replacement="▯")
        text = text.replace("\t", "        ")
    else:
        raise TypeError(dxftype)
    return text
