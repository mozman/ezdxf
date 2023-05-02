# Copyright (c) 2020-2022, Manfred Moitzi
# License: MIT License

import pytest
import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.properties import BackendProperties

from ezdxf.addons.drawing.backend import Backend
from ezdxf.addons.drawing.debug_backend import BasicBackend, PathBackend
from ezdxf.entities import DXFGraphic
from ezdxf.render.forms import cube
from ezdxf.path import from_vertices


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
    return Frontend(ctx, BasicBackend())


@pytest.fixture
def path_backend(doc, ctx):
    return Frontend(ctx, PathBackend())


def unique_types(result):
    return {e[0] for e in result}


def get_result(frontend):
    return frontend.out.collector


def test_basic_frontend_init(basic):
    assert isinstance(basic.out, BasicBackend)


def test_backend_default_draw_path():
    backend = BasicBackend()
    path = from_vertices([(0, 0), (1, 0), (2, 0)])
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
    assert len(result) > 10
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
    assert len(result) > 10
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
    assert len(result) == 12
    assert result[0][0] == "filled_polygon"


def test_hatch(msp, path_backend):
    hatch = msp.add_hatch()
    hatch.paths.add_polyline_path([(0, 0), (1, 0), (1, 1), (0, 1)])
    path_backend.draw_entities(msp)
    result = get_result(path_backend)
    assert len(result) == 1
    assert result[0][0] == "filled_polygon"  # default implementation


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


def test_override_filter(msp, ctx):
    class FrontendWithOverride(Frontend):
        def __init__(self, ctx: RenderContext, out: Backend):
            super().__init__(ctx, out)
            self.override_enabled = True

        def override_properties(
            self, entity: DXFGraphic, properties: BackendProperties
        ) -> None:
            if not self.override_enabled:
                return
            if properties.layer == "T1":
                properties.layer = "Tx"
            properties.color = "#000000"
            if entity.dxf.text == "T2":
                properties.is_visible = False

    backend = BasicBackend()
    frontend = FrontendWithOverride(ctx, backend)

    msp.delete_all_entities()
    msp.add_text("T0", dxfattribs={"layer": "T0", "color": 7, "style": "DEJAVU"})
    msp.add_text("T1", dxfattribs={"layer": "T1", "color": 6, "style": "DEJAVU"})
    msp.add_text("T2", dxfattribs={"layer": "T2", "color": 5, "style": "DEJAVU"})
    frontend.draw_entities(msp)
    frontend.override_enabled = False
    frontend.draw_entities(msp)

    # since v1.0.4 the frontend does the text rendering and passes only filled
    # polygons to the backend
    assert len(backend.collector) == 10

    # can modify color property
    result = backend.collector[0]
    assert result[0] == "filled_polygon"
    assert result[2].color == "#000000"

    # can modify layer property
    result = backend.collector[2]
    assert result[0] == "filled_polygon"
    assert result[2].layer == "Tx"

    # with override disabled

    result = backend.collector[4]
    assert result[0] == "filled_polygon"
    assert result[2].color == "#ffffff"

    result = backend.collector[6]
    assert result[0] == "filled_polygon"
    assert result[2].layer == "T1"

    result = backend.collector[8]
    assert result[0] == "filled_polygon"
    assert result[2].layer == "T2"


if __name__ == "__main__":
    pytest.main([__file__])
