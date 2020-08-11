# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import Optional, List, Set
import pytest
import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext, Properties
from ezdxf.addons.drawing.backend import Backend
from ezdxf.addons.drawing.text import FontMeasurements
from ezdxf.addons.drawing.type_hints import Radians
from ezdxf.document import Drawing
from ezdxf.entities import DXFGraphic
from ezdxf.render.forms import cube
from ezdxf.render import Path
from ezdxf.math import Vector, Matrix44


class BasicBackend(Backend):
    """ The basic backend has no draw_path() support and approximates all curves
    by lines.
    """

    def __init__(self):
        super().__init__()
        self.collector = []

    def draw_point(self, pos: Vector, properties: Properties) -> None:
        self.collector.append(('point', pos, properties))

    def draw_line(self, start: Vector, end: Vector,
                  properties: Properties) -> None:
        self.collector.append(('line', start, end, properties))

    def draw_filled_polygon(self, points: List[Vector],
                            properties: Properties) -> None:
        self.collector.append(('filled_polygon', points, properties))

    def draw_text(self, text: str, transform: Matrix44, properties: Properties,
                  cap_height: float) -> None:
        self.collector.append(('text', text, transform, properties))

    def get_font_measurements(self, cap_height: float,
                              font=None) -> FontMeasurements:
        return FontMeasurements(baseline=0.0, cap_top=1.0, x_top=0.5,
                                bottom=-0.2)

    def set_background(self, color: str) -> None:
        self.collector.append(('bgcolor', color))

    def get_text_line_width(self, text: str, cap_height: float,
                            font: str = None) -> float:
        return len(text)

    def clear(self) -> None:
        self.collector = []


class PathBackend(BasicBackend):
    def draw_path(self, path: Path, properties: Properties) -> None:
        self.collector.append(('path', path, properties))


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
def path_backend(doc, ctx):
    return Frontend(ctx, PathBackend())


def unique_types(result):
    return {e[0] for e in result}


def test_basic_frontend_init(basic):
    assert isinstance(basic.out, BasicBackend)


def test_backend_default_draw_path():
    backend = BasicBackend()
    path = Path.from_vertices([(0, 0), (1, 0), (2, 0)])
    backend.draw_path(path, Properties())
    result = backend.collector
    assert len(result) == 2
    assert result[0][0] == 'line'


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


def test_lwpolyline_basic(msp, basic):
    msp.add_lwpolyline([(0, 0), (1, 0), (2, 0)])
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 2
    assert unique_types(result) == {'line'}


def test_lwpolyline_path(msp, path_backend):
    msp.add_lwpolyline([(0, 0), (1, 0), (2, 0)])
    path_backend.draw_entities(msp)
    result = path_backend.out.collector
    assert len(result) == 1
    assert unique_types(result) == {'path'}


def test_banded_lwpolyline(msp, basic):
    msp.add_lwpolyline([(0, 0), (1, 0), (2, 0)],
                       dxfattribs={'const_width': 0.1})
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 1
    assert unique_types(result) == {'filled_polygon'}


def test_polyline_2d(msp, basic):
    msp.add_polyline2d([(0, 0), (1, 0), (2, 0)])
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 2
    assert result[0][0] == 'line'
    assert result[1][0] == 'line'


def test_banded_polyline_2d(msp, basic):
    msp.add_polyline2d([(0, 0, 0.1, 0.2), (1, 0, 0.2, 0.1), (2, 0, 0.1, 0.5)],
                       format='xyse')
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 1
    assert result[0][0] == 'filled_polygon'


def test_polyline_3d_basic(msp, basic):
    msp.add_polyline3d([(0, 0, 0), (1, 0, 1), (2, 0, 5)])
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 2
    assert unique_types(result) == {'line'}


def test_polyline_3d_path(msp, path_backend):
    msp.add_polyline3d([(0, 0, 0), (1, 0, 1), (2, 0, 5)])
    path_backend.draw_entities(msp)
    result = path_backend.out.collector
    assert len(result) == 1
    assert unique_types(result) == {'path'}


def test_2d_arc_basic(msp, basic):
    msp.add_circle((0, 0), radius=2)
    msp.add_arc((0, 0), radius=2, start_angle=30, end_angle=60,
                dxfattribs={'layer': 'Test1'})
    msp.add_ellipse((0, 0), major_axis=(1, 0, 0), ratio=0.5, start_param=1,
                    end_param=2, dxfattribs={'layer': 'Test1'})
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) > 3
    assert unique_types(result) == {'line'}


def test_3d_circle_basic(msp, basic):
    msp.add_circle((0, 0), radius=2,
                   dxfattribs={'extrusion': (0, 1, 1)})
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) > 30
    assert unique_types(result) == {'line'}


def test_3d_circle_path(msp, path_backend):
    msp.add_circle((0, 0), radius=2,
                   dxfattribs={'extrusion': (0, 1, 1)})
    path_backend.draw_entities(msp)
    result = path_backend.out.collector
    assert len(result) == 1
    assert unique_types(result) == {'path'}


def test_3d_arc_basic(msp, basic):
    msp.add_arc((0, 0), radius=2, start_angle=30, end_angle=60,
                dxfattribs={'extrusion': (0, 1, 1)})
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) > 10
    assert unique_types(result) == {'line'}


def test_3d_arc_path(msp, path_backend):
    msp.add_arc((0, 0), radius=2, start_angle=30, end_angle=60,
                dxfattribs={'extrusion': (0, 1, 1)})
    path_backend.draw_entities(msp)
    result = path_backend.out.collector
    assert len(result) == 1
    assert unique_types(result) == {'path'}


def test_3d_ellipse_basic(msp, basic):
    msp.add_ellipse((0, 0), major_axis=(1, 0, 0), ratio=0.5, start_param=1,
                    end_param=2, dxfattribs={'extrusion': (0, 1, 1)})
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) > 10
    assert unique_types(result) == {'line'}


def test_3d_ellipse_path(msp, path_backend):
    msp.add_ellipse((0, 0), major_axis=(1, 0, 0), ratio=0.5, start_param=1,
                    end_param=2,
                    dxfattribs={'extrusion': (0, 1, 1)})
    path_backend.draw_entities(msp)
    result = path_backend.out.collector
    assert len(result) == 1
    assert unique_types(result) == {'path'}


def test_2d_text(msp, basic):
    msp.add_text('test\ntest')  # \n shouldn't be  problem. Will be ignored
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 1
    assert result[0][0] == 'text'
    assert result[0][1] == 'testtest'


def test_ignore_3d_text(msp, basic):
    msp.add_text('test', dxfattribs={'extrusion': (0, 1, 1)})
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 0


def test_mtext(msp, basic):
    msp.add_mtext('line1\nline2')
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 2
    assert result[0][0] == 'text'
    assert result[0][1] == 'line1'
    assert result[1][0] == 'text'
    assert result[1][1] == 'line2'


def test_hatch(msp, path_backend):
    hatch = msp.add_hatch()
    hatch.paths.add_polyline_path([(0, 0), (1, 0), (1, 1), (0, 1)])
    path_backend.draw_entities(msp)
    result = path_backend.out.collector
    assert len(result) == 1
    assert result[0][0] == 'path'


def test_basic_spline(msp, basic):
    msp.add_spline(fit_points=[(0, 0), (3, 2), (4, 5), (6, 4), (12, 0)])
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) > 1
    entities = {e[0] for e in result}
    assert entities == {'line'}


def test_mesh(msp, basic):
    # draw mesh as wire frame
    c = cube()
    c.render(msp)
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 24
    assert unique_types(result) == {'line'}


def test_polyface(msp, basic):
    # draw mesh as wire frame
    c = cube()
    c.render_polyface(msp)
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 24
    entities = {e[0] for e in result}
    assert entities == {'line'}


def _add_text_block(doc: Drawing):
    doc.layers.new(name='Layer1')
    doc.layers.new(name='Layer2')

    text_block = doc.blocks.new(name='text-block')
    text_block.add_text(
        text="L0",
        dxfattribs={
            'layer': "0",
            'insert': (0, 0, 0),
            'height': 5.0,
        },
    )
    text_block.add_text(
        text="L1",
        dxfattribs={
            'layer': "Layer1",
            'insert': (0, 0, 0),
            'height': 5.0,
        },
    )


def _get_text_visible_when(doc: Drawing, active_layers: Set[str]) -> List[str]:
    ctx = RenderContext(doc)
    # set given layer to ON, others to OFF
    ctx.set_layers_state(active_layers, state=True)

    backend = BasicBackend()
    Frontend(ctx, backend).draw_layout(doc.modelspace())
    visible_text = [x[1] for x in backend.collector if x[0] == 'text']
    return visible_text


def test_visibility_insert_0():
    """ see notes/drawing.md 'Layers and Draw Order' """
    doc = ezdxf.new()
    _add_text_block(doc)
    layout = doc.modelspace()
    layout.add_blockref(
        name="text-block",
        insert=(0, 0, 0),
        dxfattribs={'layer': "0"},
    )
    # INSERT on '0'
    # 'L0' on '0'
    # 'L1' on 'Layer1'
    assert _get_text_visible_when(doc, {'0', 'Layer1', 'Layer2'}) == ['L0',
                                                                      'L1']
    assert _get_text_visible_when(doc, {'0', 'Layer2'}) == ['L0']
    assert _get_text_visible_when(doc, {'0', 'Layer1'}) == ['L0', 'L1']
    assert _get_text_visible_when(doc, {'Layer1', 'Layer2'}) == ['L1']
    assert _get_text_visible_when(doc, {'Layer2'}) == []
    assert _get_text_visible_when(doc, {'Layer1'}) == ['L1']
    assert _get_text_visible_when(doc, set()) == []


def test_visibility_insert_2():
    """ see notes/drawing.md 'Layers and Draw Order' """
    doc = ezdxf.new()
    _add_text_block(doc)
    layout = doc.modelspace()
    layout.add_blockref(
        name="text-block",
        insert=(0, 0, 0),
        dxfattribs={'layer': "Layer2"},
    )
    # 'L0' on '0'
    # 'L1' on 'Layer1'
    # text-block on 'Layer2' -> 'L0' on '0' acts like on 'Layer2'
    assert _get_text_visible_when(doc, {'0', 'Layer1', 'Layer2'}) == ['L0',
                                                                      'L1']
    assert _get_text_visible_when(doc, {'0', 'Layer2'}) == ['L0']
    assert _get_text_visible_when(doc, {'0', 'Layer1'}) == ['L1']
    assert _get_text_visible_when(doc, {'Layer1', 'Layer2'}) == ['L0', 'L1']
    assert _get_text_visible_when(doc, {'Layer2'}) == ['L0']
    assert _get_text_visible_when(doc, {'Layer1'}) == ['L1']
    assert _get_text_visible_when(doc, set()) == []


def test_override_filter(msp, ctx):
    class FrontendWithOverride(Frontend):
        def __init__(self, ctx: RenderContext, out: Backend):
            super().__init__(ctx, out)
            self.override_enabled = True

        def override_properties(self, entity: DXFGraphic,
                                properties: Properties) -> None:
            if not self.override_enabled:
                return
            if properties.layer == 'T1':
                properties.layer = 'Tx'
            properties.color = '#000000'
            if entity.dxf.text == 'T2':
                properties.is_visible = False

    backend = BasicBackend()
    frontend = FrontendWithOverride(ctx, backend)

    msp.delete_all_entities()
    msp.add_text('T0', dxfattribs={'layer': 'T0', 'color': 7})
    msp.add_text('T1', dxfattribs={'layer': 'T1', 'color': 6})
    msp.add_text('T2', dxfattribs={'layer': 'T2', 'color': 5})
    frontend.draw_entities(msp)
    frontend.override_enabled = False
    frontend.draw_entities(msp)

    assert len(backend.collector) == 5

    # can modify color property
    result = backend.collector[0]
    assert result[0] == 'text'
    assert result[1] == 'T0'
    assert result[3].color == '#000000'

    # can modify layer property
    result = backend.collector[1]
    assert result[0] == 'text'
    assert result[1] == 'T1'
    assert result[3].layer == 'Tx'

    # with override disabled

    result = backend.collector[2]
    assert result[0] == 'text'
    assert result[1] == 'T0'
    assert result[3].color == '#ffffff'

    result = backend.collector[3]
    assert result[0] == 'text'
    assert result[1] == 'T1'
    assert result[3].layer == 'T1'

    result = backend.collector[4]
    assert result[0] == 'text'
    assert result[1] == 'T2'
    assert result[3].layer == 'T2'


if __name__ == '__main__':
    pytest.main([__file__])
