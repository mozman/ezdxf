# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import Optional, Tuple, List
import pytest
import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext, Properties
from ezdxf.addons.drawing.backend_interface import DrawingBackend, Radians
from ezdxf.addons.drawing.text import FontMeasurements
from ezdxf.math import Vector, Matrix44


class BasicBackend(DrawingBackend):
    def __init__(self):
        super().__init__()
        self.collector = []

    def draw_point(self, pos: Vector, properties: Properties) -> None:
        self.collector.append(('point', pos, properties))

    def draw_line(self, start: Vector, end: Vector, properties: Properties) -> None:
        self.collector.append(('line', start, end, properties))

    def draw_arc(self, center: Vector, width: float, height: float, angle: Radians,
                 draw_angles: Optional[Tuple[Radians, Radians]], properties: Properties) -> None:
        self.collector.append(('arc', center, properties))

    def draw_filled_polygon(self, points: List[Vector], properties: Properties) -> None:
        self.collector.append(('filled_polygon', points, properties))

    def draw_text(self, text: str, transform: Matrix44, properties: Properties, cap_height: float) -> None:
        self.collector.append(('text', transform, properties))

    def get_font_measurements(self, cap_height: float) -> FontMeasurements:
        return FontMeasurements(baseline=0.0, cap_top=1.0, x_top=0.0, bottom=-0.2)

    def set_background(self, color: str) -> None:
        self.collector.append(('bgcolor', color))

    def get_text_line_width(self, text: str, cap_height: float) -> float:
        return len(text)

    def clear(self) -> None:
        self.collector = []


class ExtendedBackend(BasicBackend):
    pass


@pytest.fixture
def doc():
    d = ezdxf.new()
    d.layers.new('Test1')
    d.layers.new('Test2')
    d.layers.new('Test3')
    return d


@pytest.fixture
def ctx(doc):
    return RenderContext(doc)


def test_frontend_init(doc, ctx):
    backend = BasicBackend()
    frontend = Frontend(ctx, backend)
    assert frontend.ctx is ctx
    assert frontend.out is backend


if __name__ == '__main__':
    pytest.main([__file__])
