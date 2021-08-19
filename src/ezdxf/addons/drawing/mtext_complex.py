#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Iterable, List
from ezdxf.entities import MText
from ezdxf.tools import text_layout as tl
from ezdxf.math import Matrix44, Vec3
from .backend import Backend
from .properties import Properties

__all__ = ["complex_mtext_renderer"]


def corner_vertices(
    left: float,
    bottom: float,
    right: float,
    top: float,
    m: Matrix44 = None,
) -> Iterable[Vec3]:
    corners = [  # closed polygon: fist vertex  == last vertex
        (left, top),
        (right, top),
        (right, bottom),
        (left, bottom),
        (left, top),
    ]
    if m is None:
        return Vec3.generate(corners)
    else:
        return m.transform_vertices(corners)


class FrameRenderer(tl.ContentRenderer):
    def __init__(self, properties: Properties, backend: Backend):
        self.line_properties = properties
        self.backend = backend

    def render(
        self,
        left: float,
        bottom: float,
        right: float,
        top: float,
        m: Matrix44 = None,
    ) -> None:
        self._render_outline(list(corner_vertices(left, bottom, right, top, m)))

    def _render_outline(self, vertices: List[Vec3]) -> None:
        backend = self.backend
        properties = self.line_properties
        prev = vertices.pop(0)
        for vertex in vertices:
            backend.draw_line(prev, vertex, properties)
            prev = vertex

    def line(
        self, x1: float, y1: float, x2: float, y2: float, m: Matrix44 = None
    ) -> None:
        points = [(x1, y1), (x2, y2)]
        if m is not None:
            p1, p2 = m.transform_vertices(points)
        else:
            p1, p2 = Vec3.generate(points)
        self.backend.draw_line(p1, p2, self.line_properties)


class ColumnBackgroundRenderer(FrameRenderer):
    def __init__(
        self,
        properties: Properties,
        backend: Backend,
        bg_properties: Properties = None,
        offset: float = 0,
        text_frame: bool = False,
    ):
        super().__init__(properties, backend)
        self.bg_properties = bg_properties
        self.offset = offset  # background border offset
        self.has_text_frame = text_frame

    def render(
        self,
        left: float,
        bottom: float,
        right: float,
        top: float,
        m: Matrix44 = None,
    ) -> None:
        # Important: this is not a clipping box, it is possible to
        # render anything outside of the given borders!
        offset = self.offset
        vertices = list(
            corner_vertices(
                left - offset, bottom - offset, right + offset, top + offset, m
            )
        )
        if self.bg_properties is not None:
            self.backend.draw_filled_polygon(vertices, self.bg_properties)
        if self.has_text_frame:
            self._render_outline(vertices)


class TextRenderer(FrameRenderer):
    """Text content renderer."""

    def __init__(
        self,
        text: str,
        cap_height: float,
        text_properties: Properties,
        line_properties: Properties,
        backend: Backend,
    ):
        super().__init__(line_properties, backend)
        self.text = text
        self.cap_height = cap_height
        self.text_properties = text_properties

    def render(
        self,
        left: float,
        bottom: float,
        right: float,
        top: float,
        m: Matrix44 = None,
    ):
        """Create/render the text content"""
        t = Matrix44.translate(left, bottom, 0)
        if m is None:
            m = t
        else:
            m = t * m
        self.backend.draw_text(
            self.text, m, self.text_properties, self.cap_height
        )


def complex_mtext_renderer(
    backend: Backend, mtext: MText, properties: Properties
) -> None:
    pass
