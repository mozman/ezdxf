# Copyright (c) 2023, Manfred Moitzi
# License: MIT License

import pytest
import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.recorder import Recorder, BackendProperties
from ezdxf.addons.drawing.debug_backend import PathBackend


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
    player = frontend.out.copy_player()
    player.replay(backend)
    return backend.collector


def test_replay_layout(msp, frontend):
    msp.add_point((0, 0))
    msp.add_point((0, 0))
    frontend.draw_layout(msp)
    bg, pt0, pt1 = replay(frontend, PathBackend())
    assert bg[0] == "bgcolor"
    assert pt0[0] == "point"
    assert pt1[0] == "point"


def test_points(msp, frontend):
    msp.add_point((0, 0), dxfattribs={"layer": "Test1"})
    msp.add_point((0, 0), dxfattribs={"layer": "fail"})
    frontend.draw_entities(msp)
    bg, pt0, pt1 = replay(frontend, PathBackend())
    assert bg[0] == "bgcolor"
    assert pt0[0] == "point"
    assert pt0[-1].layer == "Test1"
    assert pt1[0] == "point"
    assert pt1[-1].layer == "fail"


def test_line(msp, frontend):
    msp.add_line((0, 0), (1, 0))
    frontend.draw_entities(msp)
    _, line = replay(frontend, PathBackend())
    assert line[0] == "line"


def test_lwpolyline_as_path(msp, frontend):
    msp.add_lwpolyline([(0, 0), (1, 0), (2, 0)])
    frontend.draw_entities(msp)
    _, path = replay(frontend, PathBackend())
    assert path[0] == "path"


def test_replay_properties(msp, frontend):
    pline = msp.add_lwpolyline(
        [(0, 0), (1, 0), (2, 0)], dxfattribs={"color": 1, "lineweight": 70}
    )
    frontend.draw_entities(msp)
    _, path = replay(frontend, PathBackend())
    properties = path[2]
    assert properties.color == "#ff0000"
    assert properties.lineweight == pytest.approx(0.7)
    assert properties.layer == "0"
    assert properties.pen == 1
    assert properties.handle == pline.dxf.handle


def test_override_properties_at_replay(msp, ctx):
    def override(_: BackendProperties) -> BackendProperties:
        return BackendProperties("#00ff00", 0.5, "1", 2, "FEFE")

    msp.add_lwpolyline(
        [(0, 0), (1, 0), (2, 0)], dxfattribs={"color": 1, "lineweight": 70}
    )
    # recording:
    backend_recorder = Recorder()
    Frontend(ctx, backend_recorder).draw_entities(msp)

    # replay:
    player = backend_recorder.copy_player()
    replay_backend = PathBackend()
    player.replay(replay_backend, override)

    properties = replay_backend.collector[1][2]
    assert properties.color == "#00ff00"
    assert properties.lineweight == pytest.approx(0.5)
    assert properties.layer == "1"
    assert properties.pen == 2
    assert properties.handle == "FEFE"


def test_banded_lwpolyline_as_filled_polygon(msp, frontend):
    msp.add_lwpolyline([(0, 0), (1, 0), (2, 0)], dxfattribs={"const_width": 0.1})
    frontend.draw_entities(msp)
    _, filled_polygon = replay(frontend, PathBackend())
    assert filled_polygon[0] == "filled_polygon"


def test_2d_text_as_filled_paths(msp, frontend):
    # since v1.0.4 the frontend does the text rendering and passes only filled
    # polygons to the backend
    msp.add_text(
        "test\ntest", dxfattribs={"style": "DEJAVU"}
    )  # \n shouldn't be  problem. Will be ignored
    frontend.draw_entities(msp)
    _, *filled_paths = replay(frontend, PathBackend())
    assert filled_paths[0][0] == "filled_path"
    assert len(filled_paths[0][1]) == 2


def test_bounding_box(msp, frontend):
    recorder = frontend.out
    assert isinstance(recorder, Recorder)

    msp.add_lwpolyline([(0, 0), (200, 0), (200, 100), (0, 100)])
    frontend.draw_layout(msp)
    player = recorder.copy_player()
    player.replay(PathBackend())
    bbox = player.bbox()
    assert bbox.extmin.isclose((0, 0))
    assert bbox.extmax.isclose((200, 100))
