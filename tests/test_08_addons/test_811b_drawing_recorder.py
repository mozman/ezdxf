# Copyright (c) 2023, Manfred Moitzi
# License: MIT License

import pytest
import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.recorder import Recorder
from ezdxf.addons.drawing.debug_backend import PathBackend
from ezdxf.render.forms import cube


@pytest.fixture
def doc():
    d = ezdxf.new()
    d.layers.new("Test1")
    d.styles.add("DEJAVU", font="DejaVuSans.ttf")
    return d


@pytest.fixture
def msp(doc):
    return doc.modelspace()


@pytest.fixture
def ctx(doc):
    return RenderContext(doc)


@pytest.fixture
def frontend(doc, ctx):
    return Frontend(ctx, Recorder())


def replay(frontend, backend):
    recorder = frontend.out
    recorder.replay(backend)
    return backend.collector


def unique_types(result):
    return {e[0] for e in result}


def test_replay_layout(msp, frontend):
    msp.add_point((0, 0))
    msp.add_point((0, 0))
    frontend.draw_layout(msp)
    bg, pt0, pt1 = replay(frontend, PathBackend())
    assert bg[0] == "bgcolor"
    assert pt0[0] == "point"
    assert pt1[0] == "point"


def test_point_and_layers(msp, frontend):
    msp.add_point((0, 0), dxfattribs={"layer": "Test1"})
    # a non-existing layer shouldn't be a problem
    msp.add_point((0, 0), dxfattribs={"layer": "fail"})
    frontend.draw_entities(msp)
    bg, pt0, pt1 = replay(frontend, PathBackend())
    assert bg[0] == "bgcolor"
    assert pt0[0] == "point"
    assert pt0[-1].layer == "Test1"
    assert pt1[0] == "point"
    assert pt1[-1].layer == "fail"


def _test_line(msp, basic):
    msp.add_line((0, 0), (1, 0))
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 1
    assert result[0][0] == "line"


def _test_lwpolyline_basic(msp, basic):
    msp.add_lwpolyline([(0, 0), (1, 0), (2, 0)])
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 2
    assert unique_types(result) == {"line"}


def _test_lwpolyline_path(msp, path_backend):
    msp.add_lwpolyline([(0, 0), (1, 0), (2, 0)])
    path_backend.draw_entities(msp)
    result = path_backend.out.collector
    assert len(result) == 1
    assert unique_types(result) == {"path"}


def _test_banded_lwpolyline(msp, basic):
    msp.add_lwpolyline([(0, 0), (1, 0), (2, 0)], dxfattribs={"const_width": 0.1})
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 1
    assert unique_types(result) == {"filled_polygon"}


def _test_polyline_2d(msp, basic):
    msp.add_polyline2d([(0, 0), (1, 0), (2, 0)])
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 2
    assert result[0][0] == "line"
    assert result[1][0] == "line"


def _test_banded_polyline_2d(msp, basic):
    msp.add_polyline2d(
        [(0, 0, 0.1, 0.2), (1, 0, 0.2, 0.1), (2, 0, 0.1, 0.5)], format="xyse"
    )
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 1
    assert result[0][0] == "filled_polygon"


def _test_polyline_3d_basic(msp, basic):
    msp.add_polyline3d([(0, 0, 0), (1, 0, 1), (2, 0, 5)])
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 2
    assert unique_types(result) == {"line"}


def _test_polyline_3d_path(msp, path_backend):
    msp.add_polyline3d([(0, 0, 0), (1, 0, 1), (2, 0, 5)])
    path_backend.draw_entities(msp)
    result = path_backend.out.collector
    assert len(result) == 1
    assert unique_types(result) == {"path"}


def _test_2d_arc_basic(msp, basic):
    msp.add_circle((0, 0), radius=2)
    msp.add_arc(
        (0, 0),
        radius=2,
        start_angle=30,
        end_angle=60,
        dxfattribs={"layer": "Test1"},
    )
    msp.add_ellipse(
        (0, 0),
        major_axis=(1, 0, 0),
        ratio=0.5,
        start_param=1,
        end_param=2,
        dxfattribs={"layer": "Test1"},
    )
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) > 3
    assert unique_types(result) == {"line"}


def _test_3d_circle_basic(msp, basic):
    msp.add_circle((0, 0), radius=2, dxfattribs={"extrusion": (0, 1, 1)})
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) > 30
    assert unique_types(result) == {"line"}


def _test_3d_circle_path(msp, path_backend):
    msp.add_circle((0, 0), radius=2, dxfattribs={"extrusion": (0, 1, 1)})
    path_backend.draw_entities(msp)
    result = path_backend.out.collector
    assert len(result) == 1
    assert unique_types(result) == {"path"}


def _test_3d_arc_basic(msp, basic):
    msp.add_arc(
        (0, 0),
        radius=2,
        start_angle=30,
        end_angle=60,
        dxfattribs={"extrusion": (0, 1, 1)},
    )
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) > 10
    assert unique_types(result) == {"line"}


def _test_3d_arc_path(msp, path_backend):
    msp.add_arc(
        (0, 0),
        radius=2,
        start_angle=30,
        end_angle=60,
        dxfattribs={"extrusion": (0, 1, 1)},
    )
    path_backend.draw_entities(msp)
    result = path_backend.out.collector
    assert len(result) == 1
    assert unique_types(result) == {"path"}


def _test_3d_ellipse_basic(msp, basic):
    msp.add_ellipse(
        (0, 0),
        major_axis=(1, 0, 0),
        ratio=0.5,
        start_param=1,
        end_param=2,
        dxfattribs={"extrusion": (0, 1, 1)},
    )
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) > 10
    assert unique_types(result) == {"line"}


def _test_3d_ellipse_path(msp, path_backend):
    msp.add_ellipse(
        (0, 0),
        major_axis=(1, 0, 0),
        ratio=0.5,
        start_param=1,
        end_param=2,
        dxfattribs={"extrusion": (0, 1, 1)},
    )
    path_backend.draw_entities(msp)
    result = path_backend.out.collector
    assert len(result) == 1
    assert unique_types(result) == {"path"}


def _test_2d_text(msp, basic):
    # since v1.0.4 the frontend does the text rendering and passes only filled
    # polygons to the backend
    msp.add_text(
        "test\ntest", dxfattribs={"style": "DEJAVU"}
    )  # \n shouldn't be  problem. Will be ignored
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 8
    assert result[0][0] == "filled_polygon"


def _test_ignore_3d_text(msp, basic):
    msp.add_text("test", dxfattribs={"extrusion": (0, 1, 1)})
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 0


def _test_mtext(msp, basic):
    # since v1.0.4 the frontend does the text rendering and passes only filled
    # polygons to the backend
    msp.add_mtext("line1\nline2", dxfattribs={"style": "DEJAVU"})
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 12
    assert result[0][0] == "filled_polygon"


def _test_hatch(msp, path_backend):
    hatch = msp.add_hatch()
    hatch.paths.add_polyline_path([(0, 0), (1, 0), (1, 1), (0, 1)])
    path_backend.draw_entities(msp)
    result = path_backend.out.collector
    assert len(result) == 1
    assert result[0][0] == "filled_polygon"  # default implementation


def _test_basic_spline(msp, basic):
    msp.add_spline(fit_points=[(0, 0), (3, 2), (4, 5), (6, 4), (12, 0)])
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) > 1
    entities = {e[0] for e in result}
    assert entities == {"line"}


def _test_mesh(msp, basic):
    # draw mesh as wire frame
    c = cube()
    c.render_mesh(msp)
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 24
    assert unique_types(result) == {"line"}


def _test_polyface(msp, basic):
    # draw mesh as wire frame
    c = cube()
    c.render_polyface(msp)
    basic.draw_entities(msp)
    result = basic.out.collector
    assert len(result) == 24
    entities = {e[0] for e in result}
    assert entities == {"line"}
