# Copyright (c) 2023, Manfred Moitzi
# License: MIT License

import pytest
import ezdxf
import ezdxf.path
from ezdxf.math import Vec2
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.recorder import Recorder, BackendProperties, Override
from ezdxf.addons.drawing.debug_backend import PathBackend


class MyTestFrontend(Frontend):
    def __init__(self, ctx, backend):
        super().__init__(ctx, backend)
        self.out = backend


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
    return MyTestFrontend(ctx, Recorder())


def replay(frontend, backend):
    player = frontend.out.player().copy()
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
    def override(_: BackendProperties) -> Override:
        return Override(properties=BackendProperties("#00ff00", 0.5, "1", 2, "FEFE"))

    msp.add_lwpolyline(
        [(0, 0), (1, 0), (2, 0)], dxfattribs={"color": 1, "lineweight": 70}
    )
    # recording:
    backend_recorder = Recorder()
    MyTestFrontend(ctx, backend_recorder).draw_entities(msp)

    # replay:
    player = backend_recorder.player().copy()
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
    player = recorder.player().copy()
    player.replay(PathBackend())
    bbox = player.bbox()
    assert bbox.extmin.isclose((0, 0))
    assert bbox.extmax.isclose((200, 100))


class TestCroppingRecords:
    """Clipping is tested in 822 and 618!"""

    def test_null_sized_crop_box_removes_everything(self):
        """A cropping box of size zero in any dimension should remove all records."""
        props = BackendProperties()
        recorder = Recorder()
        recorder.draw_point(Vec2(0, 0), props)

        # 0 x 0
        player = recorder.player().copy()
        assert len(player.records) == 1
        player.crop_rect((0, 0), (0, 0), 1)
        assert len(player.records) == 0

        # 0 x 1
        player = recorder.player().copy()
        player.crop_rect((0, 0), (0, 1), 1)
        assert len(player.records) == 0

        # 1 x 0
        player = recorder.player().copy()
        player.crop_rect((0, 0), (1, 0), 1)
        assert len(player.records) == 0

    def test_remove_entities_outside(self):
        """Records complete outside the crop box should be removed."""
        props = BackendProperties()
        recorder = Recorder()

        # point outside:
        recorder.draw_point(Vec2(1000, 1000), props)

        # line coincident with crop box side is outside!
        recorder.draw_line(Vec2(100, 0), Vec2(100, 100), props)

        # path coincident with crop box side is outside!
        path = ezdxf.path.from_2d_vertices([(0, 100), (50, 100), (100, 100)])
        recorder.draw_path(path, props)

        player = recorder.player()
        assert len(player.records) == 3

        # crop recordings:
        player.crop_rect((0, 0), (100, 100), 1)

        assert len(player.records) == 0

    def test_entities_inside_crop_box_do_not_change(self):
        """Records complete inside the crop box should not be processed in any kind."""
        props = BackendProperties()
        recorder = Recorder()
        recorder.draw_point(Vec2(50, 50), props)

        player = recorder.player()
        rec0 = player.records[0]
        player.crop_rect((0, 0), (100, 100), 1)

        assert player.records[0] is rec0, "should be identical to original record"

    def test_crop_filled_paths(self):
        props = BackendProperties()
        recorder = Recorder()
        square = ezdxf.path.rect(100, 100).to_2d_path()  # center = (0, 0)
        hole = ezdxf.path.rect(50, 50).to_2d_path()  # center = (0, 0)
        recorder.draw_filled_paths([square], [hole], props)

        player = recorder.player()
        data0 = player.records[0].data
        player.crop_rect((0, 0), (100, 100), 1)

        assert player.records[0].data is not data0, "should be new record data"

        exterior, holes = player.records[0].data
        assert exterior[0].extents() == ((0, 0), (50, 50)), "should be cropped"
        assert holes[0].extents() == ((0, 0), (25, 25)), "should be cropped"

    def test_does_not_crop_holes_inside_crop_box(self):
        props = BackendProperties()
        recorder = Recorder()
        square = ezdxf.path.rect(100, 100).to_2d_path()  # center = (0, 0)
        hole = ezdxf.path.from_2d_vertices(
            [(10, 10), (20, 10), (20, 20), (10, 20)], close=True
        )
        recorder.draw_filled_paths([square], [hole], props)

        player = recorder.player()
        _, holes = player.records[0].data
        hole0 = holes[0]
        player.crop_rect((0, 0), (100, 100), 1)

        _, holes = player.records[0].data
        assert holes[0] is hole0, "should be identical to original hole"

    def test_does_remove_holes_outside_crop_box(self):
        props = BackendProperties()
        recorder = Recorder()

        square = ezdxf.path.rect(100, 100).to_2d_path()  # center = (0, 0)
        hole = ezdxf.path.from_2d_vertices(
            [(-10, -10), (-20, -10), (-20, -20), (-10, -20)], close=True
        )
        recorder.draw_filled_paths([square], [hole], props)

        player = recorder.player()
        player.crop_rect((0, 0), (100, 100), 1)

        _, holes = player.records[0].data
        assert len(holes) == 0, "hole should be removed"
