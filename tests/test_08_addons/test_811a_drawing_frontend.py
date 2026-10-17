# Copyright (c) 2020-2024, Manfred Moitzi
# License: MIT License

import pytest
import ezdxf
from ezdxf.math import Vec2
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.frontend import UniversalFrontend
from ezdxf.addons.drawing.properties import BackendProperties, Properties

from ezdxf.addons.drawing.backend import Backend, BkPath2d
from ezdxf.addons.drawing.debug_backend import BasicBackend, PathBackend
from ezdxf.addons.drawing.pipeline import RenderPipeline2d
from ezdxf.entities import DXFGraphic
from ezdxf.layouts import Modelspace
from ezdxf.render.forms import cube
from ezdxf import xclip


class ClippingTrackingPipeline(RenderPipeline2d):
    """Subclass of RenderPipeline2d that tracks push/pop clipping calls."""

    def __init__(self, backend):
        super().__init__(backend)
        self.push_count = 0
        self.pop_count = 0

    def push_clipping_shape(self, shape, transform):
        self.push_count += 1
        super().push_clipping_shape(shape, transform)

    def pop_clipping_shape(self):
        self.pop_count += 1
        super().pop_clipping_shape()


class ClippingTestFrontend(Frontend):
    """Frontend using ClippingTrackingPipeline for testing push/pop balance."""

    def __init__(self, ctx, backend):
        pipeline = ClippingTrackingPipeline(backend)
        # Call UniversalFrontend.__init__ directly to bypass Frontend.__init__
        # which would create a plain RenderPipeline2d, overwriting our tracking one.
        UniversalFrontend.__init__(self, ctx, pipeline)
        self.out = backend

    @property
    def stack_depth(self) -> int:
        return self.pipeline.clipping_portal.stack_depth


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
def basic(doc, ctx):
    return MyTestFrontend(ctx, BasicBackend())


@pytest.fixture
def path_backend(doc, ctx):
    return MyTestFrontend(ctx, PathBackend())


def unique_types(result):
    return {e[0] for e in result}


def get_result(frontend):
    return frontend.out.collector


def test_basic_frontend_init(basic):
    assert isinstance(basic.out, BasicBackend)


def test_backend_default_draw_path():
    backend = BasicBackend()
    path = BkPath2d.from_vertices(Vec2.list([(0, 0), (1, 0), (2, 0)]))
    backend.draw_path(path, BackendProperties())
    result = backend.collector
    assert len(result) == 2
    assert result[0][0] == "line"


def test_draw_layout(msp, basic):
    msp.add_point((0, 0))
    msp.add_point((0, 0))
    basic.draw_layout(msp)
    result = get_result(basic)
    assert len(result) == 3
    assert result[0][0] == "bgcolor"
    assert result[1][0] == "point"
    assert result[2][0] == "point"


def test_draw_entities(msp, basic):
    msp.add_point((0, 0))
    msp.add_point((0, 0))

    basic.draw_entities(msp)
    result = get_result(basic)
    assert len(result) == 2
    assert result[0][0] == "point"
    assert result[1][0] == "point"


def test_filter_draw_entities(msp, basic):
    def filter_layer_l1(e: DXFGraphic) -> bool:
        return e.dxf.layer == "L1"

    msp.add_point((0, 0), dxfattribs={"layer": "L1"})
    msp.add_point((0, 0), dxfattribs={"layer": "L2"})

    basic.draw_entities(msp, filter_func=filter_layer_l1)
    result = get_result(basic)
    assert len(result) == 1
    assert result[0][2].layer == "L1"


def test_point_and_layers(msp, basic):
    msp.add_point((0, 0), dxfattribs={"layer": "Test1"})
    # a non-existing layer shouldn't be a problem
    msp.add_point((0, 0), dxfattribs={"layer": "fail"})
    basic.draw_entities(msp)
    result = get_result(basic)
    assert len(result) == 2
    assert result[0][0] == "point"
    assert result[0][-1].layer == "Test1"
    assert result[1][0] == "point"
    assert result[1][-1].layer == "fail"


def test_line(msp, basic):
    msp.add_line((0, 0), (1, 0))
    basic.draw_entities(msp)
    result = get_result(basic)
    assert len(result) == 1
    assert result[0][0] == "line"


def test_lwpolyline_basic(msp, basic):
    msp.add_lwpolyline([(0, 0), (1, 0), (2, 0)])
    basic.draw_entities(msp)
    result = get_result(basic)
    assert len(result) == 2
    assert unique_types(result) == {"line"}


def test_lwpolyline_path(msp, path_backend):
    msp.add_lwpolyline([(0, 0), (1, 0), (2, 0)])
    path_backend.draw_entities(msp)
    result = get_result(path_backend)
    assert len(result) == 1
    assert unique_types(result) == {"path"}


def test_banded_lwpolyline(msp, basic):
    msp.add_lwpolyline([(0, 0), (1, 0), (2, 0)], dxfattribs={"const_width": 0.1})
    basic.draw_entities(msp)
    result = get_result(basic)
    assert len(result) == 1
    assert unique_types(result) == {"filled_polygon"}


def test_polyline_2d(msp, basic):
    msp.add_polyline2d([(0, 0), (1, 0), (2, 0)])
    basic.draw_entities(msp)
    result = get_result(basic)
    assert len(result) == 2
    assert result[0][0] == "line"
    assert result[1][0] == "line"


def test_banded_polyline_2d(msp, basic):
    msp.add_polyline2d(
        [(0, 0, 0.1, 0.2), (1, 0, 0.2, 0.1), (2, 0, 0.1, 0.5)], format="xyse"
    )
    basic.draw_entities(msp)
    result = get_result(basic)
    assert len(result) == 1
    assert result[0][0] == "filled_polygon"


def test_polyline_3d_basic(msp, basic):
    msp.add_polyline3d([(0, 0, 0), (1, 0, 1), (2, 0, 5)])
    basic.draw_entities(msp)
    result = get_result(basic)
    assert len(result) == 2
    assert unique_types(result) == {"line"}


def test_polyline_3d_path(msp, path_backend):
    msp.add_polyline3d([(0, 0, 0), (1, 0, 1), (2, 0, 5)])
    path_backend.draw_entities(msp)
    result = get_result(path_backend)
    assert len(result) == 1
    assert unique_types(result) == {"path"}


def test_2d_arc_basic(msp, basic):
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
    result = get_result(basic)
    assert len(result) > 3
    assert unique_types(result) == {"line"}


def test_3d_circle_basic(msp, basic):
    msp.add_circle((0, 0), radius=2, dxfattribs={"extrusion": (0, 1, 1)})
    basic.draw_entities(msp)
    result = get_result(basic)
    assert len(result) > 30
    assert unique_types(result) == {"line"}


def test_3d_circle_path(msp, path_backend):
    msp.add_circle((0, 0), radius=2, dxfattribs={"extrusion": (0, 1, 1)})
    path_backend.draw_entities(msp)
    result = get_result(path_backend)
    assert len(result) == 1
    assert unique_types(result) == {"path"}


def test_3d_arc_basic(msp, basic):
    msp.add_arc(
        (0, 0),
        radius=2,
        start_angle=30,
        end_angle=60,
        dxfattribs={"extrusion": (0, 1, 1)},
    )
    basic.draw_entities(msp)
    result = get_result(basic)
    assert len(result) >= 4
    assert unique_types(result) == {"line"}


def test_3d_arc_path(msp, path_backend):
    msp.add_arc(
        (0, 0),
        radius=2,
        start_angle=30,
        end_angle=60,
        dxfattribs={"extrusion": (0, 1, 1)},
    )
    path_backend.draw_entities(msp)
    result = get_result(path_backend)
    assert len(result) == 1
    assert unique_types(result) == {"path"}


def test_3d_ellipse_basic(msp, basic):
    msp.add_ellipse(
        (0, 0),
        major_axis=(1, 0, 0),
        ratio=0.5,
        start_param=1,
        end_param=2,
        dxfattribs={"extrusion": (0, 1, 1)},
    )
    basic.draw_entities(msp)
    result = get_result(basic)
    assert len(result) >= 4
    assert unique_types(result) == {"line"}


def test_3d_ellipse_path(msp, path_backend):
    msp.add_ellipse(
        (0, 0),
        major_axis=(1, 0, 0),
        ratio=0.5,
        start_param=1,
        end_param=2,
        dxfattribs={"extrusion": (0, 1, 1)},
    )
    path_backend.draw_entities(msp)
    result = get_result(path_backend)
    assert len(result) == 1
    assert unique_types(result) == {"path"}


def test_2d_text(msp, basic):
    # since v1.0.4 the frontend does the text rendering and passes only filled
    # polygons to the backend
    msp.add_text(
        "test\ntest", dxfattribs={"style": "DEJAVU"}
    )  # \n shouldn't be  problem. Will be ignored
    basic.draw_entities(msp)
    result = get_result(basic)
    assert len(result) == 8
    assert result[0][0] == "filled_polygon"


def test_ignore_3d_text(msp, basic):
    msp.add_text("test", dxfattribs={"extrusion": (0, 1, 1)})
    basic.draw_entities(msp)
    result = get_result(basic)
    assert len(result) == 0


def test_mtext(msp, basic):
    # since v1.0.4 the frontend does the text rendering and passes only filled
    # polygons to the backend
    msp.add_mtext("line1\nline2", dxfattribs={"style": "DEJAVU"})
    basic.draw_entities(msp)
    result = get_result(basic)
    assert (
        len(result) == 10
    )  # each character is now one multi-path: changed in v1.1.0b4
    assert result[0][0] == "filled_polygon"


def test_hatch(msp, path_backend):
    hatch = msp.add_hatch()
    hatch.paths.add_polyline_path([(0, 0), (1, 0), (1, 1), (0, 1)])
    path_backend.draw_entities(msp)
    result = get_result(path_backend)
    assert len(result) == 1
    assert result[0][0] == "filled_path"


def test_basic_spline(msp, basic):
    msp.add_spline(fit_points=[(0, 0), (3, 2), (4, 5), (6, 4), (12, 0)])
    basic.draw_entities(msp)
    result = get_result(basic)
    assert len(result) > 1
    entities = {e[0] for e in result}
    assert entities == {"line"}


def test_mesh(msp, basic):
    # draw mesh as wire frame
    c = cube()
    c.render_mesh(msp)
    basic.draw_entities(msp)
    result = get_result(basic)
    assert len(result) == 24
    assert unique_types(result) == {"line"}


def test_polyface(msp, basic):
    # draw mesh as wire frame
    c = cube()
    c.render_polyface(msp)
    basic.draw_entities(msp)
    result = get_result(basic)
    assert len(result) == 24
    entities = {e[0] for e in result}
    assert entities == {"line"}


class FrontendWithOverride(MyTestFrontend):
    def __init__(self, ctx: RenderContext, out: Backend):
        super().__init__(ctx, out)
        self.override_enabled = True

    def override_properties(self, entity: DXFGraphic, properties: Properties) -> None:
        if not self.override_enabled:
            return
        if properties.layer == "T1":
            properties.layer = "Tx"
        properties.color = "#000000"
        if entity.dxf.text == "T2":
            properties.is_visible = False


def make_override_content(msp: Modelspace):
    msp.delete_all_entities()
    msp.add_text("T0", dxfattribs={"layer": "T0", "color": 7, "style": "DEJAVU"})
    msp.add_text("T1", dxfattribs={"layer": "T1", "color": 6, "style": "DEJAVU"})
    msp.add_text("T2", dxfattribs={"layer": "T2", "color": 5, "style": "DEJAVU"})


def use_override_method(msp: Modelspace, ctx: RenderContext) -> list:
    backend = BasicBackend()
    frontend = FrontendWithOverride(ctx, backend)
    make_override_content(msp)
    frontend.draw_entities(msp)
    frontend.override_enabled = False
    frontend.draw_entities(msp)
    return backend.collector


def override_property_function(entity: DXFGraphic, properties: Properties) -> None:
    if properties.layer == "T1":
        properties.layer = "Tx"
    properties.color = "#000000"
    if entity.dxf.text == "T2":
        properties.is_visible = False


def use_override_function(msp: Modelspace, ctx: RenderContext) -> list:
    backend = BasicBackend()
    frontend = Frontend(ctx, backend)
    make_override_content(msp)

    frontend.push_property_override_function(override_property_function)
    frontend.draw_entities(msp)
    frontend.pop_property_override_function()
    frontend.draw_entities(msp)
    return backend.collector


@pytest.mark.parametrize("override", [use_override_method, use_override_function])
def test_property_override_method(msp: Modelspace, ctx: RenderContext, override):
    collector = override(msp, ctx)

    # since v1.0.4 the frontend does the text rendering and passes only filled
    # polygons to the backend
    assert len(collector) == 10

    # can modify color property
    result = collector[0]
    assert result[0] == "filled_polygon"
    assert result[2].color == "#000000"

    # can modify layer property
    result = collector[2]
    assert result[0] == "filled_polygon"
    assert result[2].layer == "Tx"

    # with override disabled

    result = collector[4]
    assert result[0] == "filled_polygon"
    assert result[2].color == "#ffffff"

    result = collector[6]
    assert result[0] == "filled_polygon"
    assert result[2].layer == "T1"

    result = collector[8]
    assert result[0] == "filled_polygon"
    assert result[2].layer == "T2"


# =============================================================================
# INSERT clipping stack balance tests
# =============================================================================


def _make_block_with_line(doc, name: str, line_end: tuple) -> str:
    """Create a named block containing a single line."""
    blk = doc.blocks.new(name)
    blk.add_line((0, 0), line_end)
    return name


def test_insert_clipping_push_pop_balanced_when_frame_policy_true(doc, ctx):
    """push/pop must be balanced even when get_xclip_frame_policy() returns True."""
    blk_name = _make_block_with_line(doc, "CLIP_BLK", (10, 10))
    msp = doc.modelspace()
    insert = msp.add_blockref(blk_name, (0, 0))
    xclip.XClip(insert).set_block_clipping_path([(-1, -1), (2, 2)])

    # Ensure frame policy is True (XCLIPFRAME = 1 or 2 means frame shown)
    doc.header["$XCLIPFRAME"] = 2

    frontend = ClippingTestFrontend(ctx, BasicBackend())
    frontend.draw_entities(msp)

    assert frontend.pipeline.push_count == 1
    assert frontend.pipeline.pop_count == 1
    assert frontend.stack_depth == 0, (
        f"stack leak: depth={frontend.stack_depth}, "
        f"push={frontend.pipeline.push_count}, pop={frontend.pipeline.pop_count}"
    )


def test_insert_clipping_push_pop_balanced_when_frame_policy_false(doc, ctx):
    """push/pop must be balanced when get_xclip_frame_policy() returns False.

    This is the critical regression test: with $XCLIPFRAME = 0, draw_path() for
    the frame is skipped but pop_clipping_shape() must still be called.
    """
    blk_name = _make_block_with_line(doc, "CLIP_BLK2", (10, 10))
    msp = doc.modelspace()
    insert = msp.add_blockref(blk_name, (0, 0))
    xclip.XClip(insert).set_block_clipping_path([(-1, -1), (2, 2)])

    # XCLIPFRAME = 0 means the clipping boundary frame is hidden
    doc.header["$XCLIPFRAME"] = 0

    frontend = ClippingTestFrontend(ctx, BasicBackend())
    frontend.draw_entities(msp)

    assert frontend.pipeline.push_count == 1
    assert frontend.pipeline.pop_count == 1
    assert frontend.stack_depth == 0, (
        f"stack leak: depth={frontend.stack_depth}, "
        f"push={frontend.pipeline.push_count}, pop={frontend.pipeline.pop_count}"
    )


def test_insert_no_clipping_nothing_pushed(doc, ctx):
    """INSERT without XCLIP must not push or pop anything."""
    blk_name = _make_block_with_line(doc, "NO_CLIP_BLK", (10, 10))
    msp = doc.modelspace()
    msp.add_blockref(blk_name, (0, 0))

    frontend = ClippingTestFrontend(ctx, BasicBackend())
    frontend.draw_entities(msp)

    assert frontend.pipeline.push_count == 0
    assert frontend.pipeline.pop_count == 0
    assert frontend.stack_depth == 0


def test_insert_nested_clipping_stacks_balanced(doc, ctx):
    """Nested INSERTs with clipping must keep the stack balanced."""
    inner_blk = _make_block_with_line(doc, "INNER_BLK", (5, 5))
    doc.blocks.new("OUTER_BLK").add_blockref(inner_blk, (0, 0))

    msp = doc.modelspace()
    outer_insert = msp.add_blockref("OUTER_BLK", (0, 0))

    xclip.XClip(outer_insert).set_block_clipping_path([(-2, -2), (20, 20)])

    # The inner INSERT is inside the OUTER_BLK block definition, so we need
    # to add clipping to all nested INSERTs in that block
    for e in doc.blocks["OUTER_BLK"]:
        if e.dxftype() == "INSERT" and e.dxf.name == inner_blk:
            xclip.XClip(e).set_block_clipping_path([(-1, -1), (6, 6)])

    doc.header["$XCLIPFRAME"] = 0

    frontend = ClippingTestFrontend(ctx, BasicBackend())
    frontend.draw_entities(msp)

    assert frontend.pipeline.push_count == 2
    assert frontend.pipeline.pop_count == 2
    assert frontend.stack_depth == 0, f"stack leak: depth={frontend.stack_depth}"


if __name__ == "__main__":
    pytest.main([__file__])


@pytest.mark.parametrize(
    "batch_size,max_segments,expected_sizes",
    [
        (None, None, [2500]),
        (None, 2050, [2050]),
        (1024, None, [1024, 1024, 452]),
        (1024, 2050, [1024, 1024, 2]),
    ],
)
def test_hatch_pattern_output_is_batched(
    msp, basic, monkeypatch, batch_size, max_segments, expected_sizes
):
    from ezdxf.render import hatching

    baseline = hatching.HatchBaseLine(Vec2(), Vec2(1, 0), Vec2(0, 1), [1, -1])
    monkeypatch.setattr(
        hatching, "pattern_baselines", lambda *args, **kwargs: [baseline]
    )
    monkeypatch.setattr(
        hatching,
        "hatch_paths",
        lambda *args, **kwargs: [hatching.Line(Vec2(), Vec2(5000, 0), 0)],
    )
    hatch = msp.add_hatch()
    hatch.set_pattern_fill("ANSI31")
    basic.config = basic.config.with_changes(
        hatching_max_segments=max_segments, hatching_batch_size=batch_size
    )
    batches = []
    monkeypatch.setattr(
        basic.pipeline,
        "draw_solid_lines",
        lambda lines, properties: batches.append(list(lines)),
    )
    basic.draw_hatch_pattern(hatch, [], Properties())
    assert [len(batch) for batch in batches] == expected_sizes
    flattened = [segment for batch in batches for segment in batch]
    for index, (start, end) in enumerate(flattened):
        assert start == Vec2(index * 2, 0)
        assert end == Vec2(index * 2 + 1, 0)
