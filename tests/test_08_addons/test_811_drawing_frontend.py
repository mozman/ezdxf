# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import Optional, Tuple, List
import pytest
import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext, Properties
from ezdxf.addons.drawing.backend_interface import DrawingBackend, Radians
from ezdxf.addons.drawing.text import FontMeasurements
from ezdxf.render.forms import cube
from ezdxf.math import Vector, Matrix44, BSpline


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
        return FontMeasurements(baseline=0.0, cap_top=1.0, x_top=0.5, bottom=-0.2)

    def set_background(self, color: str) -> None:
        self.collector.append(('bgcolor', color))

    def get_text_line_width(self, text: str, cap_height: float) -> float:
        return len(text)

    def clear(self) -> None:
        self.collector = []


class ExtendedBackend(BasicBackend):
    @property
    def has_spline_support(self):
        return True

    def draw_spline(self, spline: BSpline, properties: Properties) -> None:
        self.collector.append(('spline', spline, properties))


@pytest.fixture
def doc():
    d = ezdxf.new()
    d.layers.new('Test1')
    return d


@pytest.fixture
def msp(doc):
    return doc.modelspace()


@pytest.fixture
def ctx(doc):
    return RenderContext(doc)


@pytest.fixture
def basic(doc, ctx):
    return Frontend(ctx, BasicBackend())


@pytest.fixture
def extended(doc, ctx):
    return Frontend(ctx, ExtendedBackend())


def test_basic_frontend_init(basic):
    assert isinstance(basic.out, BasicBackend)


def test_extended_frontend_init(extended):
    assert isinstance(extended.out, ExtendedBackend)


def test_draw_layout(msp, basic):
    msp.add_point((0, 0))
    msp.add_point((0, 0))
    basic.draw_layout(msp)
    result = basic.out.collector
    assert len(result) == 3
    assert result[0][0] == 'point'
    assert result[1][0] == 'point'
    assert result[2][0] == 'bgcolor'


def test_draw_entities(msp, basic):
    msp.add_point((0, 0))
    msp.add_point((0, 0))

    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 2
    assert result[0][0] == 'point'
    assert result[1][0] == 'point'


def test_point_and_layers(msp, basic):
    msp.add_point((0, 0), dxfattribs={'layer': 'Test1'})
    # a non-existing layer shouldn't be a problem
    msp.add_point((0, 0), dxfattribs={'layer': 'fail'})
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 2
    assert result[0][0] == 'point'
    assert result[0][-1].layer == 'Test1'
    assert result[1][0] == 'point'
    assert result[1][-1].layer == 'fail'


def test_line(msp, basic):
    msp.add_line((0, 0), (1, 0))
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 1
    assert result[0][0] == 'line'


def test_lwpolyline(msp, basic):
    msp.add_lwpolyline([(0, 0), (1, 0), (2, 0)])
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 2
    assert result[0][0] == 'line'
    assert result[1][0] == 'line'


def test_polyline_2d(msp, basic):
    msp.add_polyline2d([(0, 0), (1, 0), (2, 0)])
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 2
    assert result[0][0] == 'line'
    assert result[1][0] == 'line'


def test_polyline_3d(msp, basic):
    msp.add_polyline3d([(0, 0, 0), (1, 0, 1), (2, 0, 5)])
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 2
    assert result[0][0] == 'line'
    assert result[1][0] == 'line'


def test_2d_arc(msp, basic):
    msp.add_circle((0, 0), radius=2)
    msp.add_arc((0, 0), radius=2, start_angle=30, end_angle=60, dxfattribs={'layer': 'Test1'})
    msp.add_ellipse((0, 0), major_axis=(1, 0, 0), ratio=0.5, start_param=1, end_param=2, dxfattribs={'layer': 'Test1'})
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 3
    assert result[0][0] == 'arc'
    assert result[1][0] == 'arc'
    assert result[2][0] == 'arc'


def test_3d_circle(msp, basic):
    basic.circle_approximation_count = 30
    msp.add_circle((0, 0), radius=2,
                   dxfattribs={'extrusion': (0, 1, 1)})
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 30


def test_3d_arc(msp, basic):
    basic.circle_approximation_count = 120
    msp.add_arc((0, 0), radius=2, start_angle=30, end_angle=60,
                dxfattribs={'extrusion': (0, 1, 1)})
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 10


def test_3d_ellipse(msp, basic):
    basic.circle_approximation_count = 120
    msp.add_ellipse((0, 0), major_axis=(1, 0, 0), ratio=0.5, start_param=1, end_param=2,
                    dxfattribs={'extrusion': (0, 1, 1)})
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 19


def test_2d_text(msp, basic):
    msp.add_text('test\ntest')  # \n shouldn't be  problem
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 1
    assert result[0][0] == 'text'


def test_ignore_3d_text(msp, basic):
    msp.add_text('test', dxfattribs={'extrusion': (0, 1, 1)})
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 0


def test_mtext(msp, basic):
    msp.add_mtext('test\ntest')
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 2
    assert result[0][0] == 'text'
    assert result[1][0] == 'text'


def test_hatch(msp, basic):
    hatch = msp.add_hatch()
    hatch.paths.add_polyline_path([(0, 0), (1, 0), (1, 1), (0, 1)])
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 1
    assert result[0][0] == 'filled_polygon'


def test_basic_spline(msp, basic):
    msp.add_spline(fit_points=[(0, 0), (3, 2), (4, 5), (6, 4), (12, 0)])
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) > 1
    entities = {e[0] for e in result}
    assert entities == {'line'}


def test_extended_spline(msp, extended):
    msp.add_spline(fit_points=[(0, 0), (3, 2), (4, 5), (6, 4), (12, 0)])
    extended.draw_entities(msp)
    result = extended.out.collector
    assert len(result) == 1
    assert result[0][0] == 'spline'


def test_mesh(msp, basic):
    # draw mesh as wire frame
    c = cube()
    c.render(msp)
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 24
    entities = {e[0] for e in result}
    assert entities == {'line'}


def test_polyface(msp, basic):
    # draw mesh as wire frame
    c = cube()
    c.render_polyface(msp)
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 24
    entities = {e[0] for e in result}
    assert entities == {'line'}


if __name__ == '__main__':
    pytest.main([__file__])
