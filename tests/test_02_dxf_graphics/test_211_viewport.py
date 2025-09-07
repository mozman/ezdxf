# Copyright (c) 2019-2025 Manfred Moitzi
# License: MIT License
import pytest

import ezdxf
from ezdxf.entities.viewport import Viewport
from ezdxf.lldxf.extendedtags import ExtendedTags, DXFTag
from ezdxf.lldxf.const import DXF12, DXF2000
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text
from ezdxf.math import Z_AXIS

TEST_CLASS = Viewport
TEST_TYPE = "VIEWPORT"

ENTITY_R12 = """0
VIEWPORT
5
0
8
VIEWPORTS
10
0.0
20
0.0
30
0.0
40
1.0
41
1.0
68
1
1001
ACAD
1000
MVIEW
1002
{
1070
16
1010
0.0
1020
0.0
1030
0.0
1010
0.0
1020
0.0
1030
0.0
1040
0.0
1040
1.0
1040
0.0
1040
0.0
1040
50.0
1040
0.0
1040
0.0
1070
0
1070
100
1070
1
1070
3
1070
0
1070
0
1070
0
1070
0
1040
0.0
1040
0.0
1040
0.0
1040
0.1
1040
0.1
1040
0.1
1040
0.1
1070
0
1002
{
1002
}
1002
}
"""

ENTITY_R2000 = """0
VIEWPORT
5
0
330
0
100
AcDbEntity
67
1
8
VIEWPORTS
100
AcDbViewport
10
0.0
20
0.0
30
0.0
40
1.0
41
1.0
68
2
69
2
12
0.0
22
0.0
13
0.0
23
0.0
14
0.1
24
0.1
15
0.1
25
0.1
16
0.0
26
0.0
36
0.0
17
0.0
27
0.0
37
0.0
42
50.0
43
0.0
44
0.0
45
1.0
50
0.0
51
0.0
72
100
90
32864
1

281
0
71
0
74
0
110
0.0
120
0.0
130
0.0
111
1.0
121
0.0
131
0.0
112
0.0
122
1.0
132
0.0
79
0
146
0.0
"""


@pytest.fixture(params=[ENTITY_R12, ENTITY_R2000])
def entity(request):
    return TEST_CLASS.from_text(request.param)


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES

    assert TEST_TYPE in ENTITY_CLASSES


def test_default_init():
    entity = TEST_CLASS()
    assert entity.dxftype() == TEST_TYPE


def test_default_new():
    entity = TEST_CLASS.new(
        handle="ABBA",
        owner="0",
        dxfattribs={
            "color": "7",
            "view_direction_vector": (1, 2, 3),
        },
    )
    assert entity.dxf.layer == "0"
    assert entity.dxf.view_direction_vector == (1, 2, 3)
    assert entity.dxf.view_direction_vector.x == 1, "is not Vec3 compatible"
    assert entity.dxf.view_direction_vector.y == 2, "is not Vec3 compatible"
    assert entity.dxf.view_direction_vector.z == 3, "is not Vec3 compatible"
    assert entity.dxf.view_target_point == (0, 0, 0)
    assert entity.dxf.view_twist_angle == 0
    assert entity.dxf.view_height == 1
    assert entity.dxf.view_center_point == (0, 0)
    assert entity.dxf.perspective_lens_length == 50
    assert entity.dxf.front_clip_plane_z_value == 0
    assert entity.dxf.back_clip_plane_z_value == 0
    assert entity.dxf.flags == 0
    assert entity.dxf.circle_zoom == 100
    assert entity.dxf.ucs_icon == 0
    assert entity.dxf.snap_angle == 0
    assert entity.dxf.snap_base_point == (0, 0)
    assert entity.dxf.snap_spacing == (10, 10)
    assert entity.dxf.grid_spacing == (10, 10)
    assert len(list(entity.frozen_layers)) == 0


def test_get_view_direction_vector_defaults_to_z_axis():
    vp = TEST_CLASS.new(dxfattribs={"view_direction_vector": (0, 0, 0)})
    assert vp.get_view_direction().isclose(Z_AXIS)


def test_get_view_direction_vector_is_normalized():
    vp = TEST_CLASS.new(dxfattribs={"view_direction_vector": (0, 0, 100)})
    assert vp.get_view_direction().isclose(Z_AXIS)


def test_load_from_text(entity):
    assert entity.dxf.layer == "VIEWPORTS"
    assert entity.dxf.center == (0, 0, 0)


def test_write_dxf_r2000():
    expected = basic_tags_from_text(ENTITY_R2000)
    viewport = TEST_CLASS.from_text(ENTITY_R2000)
    collector = TagCollector(dxfversion=DXF2000, optional=True)
    viewport.export_dxf(collector)
    # todo: tag checking
    assert len(collector.tags) == len(expected)

    collector2 = TagCollector(dxfversion=DXF2000, optional=False)
    viewport.export_dxf(collector2)
    assert collector.has_all_tags(collector2)


def test_write_dxf_r12():
    viewport = TEST_CLASS.from_text(ENTITY_R12)
    collector = TagCollector(dxfversion=DXF12, optional=True)
    viewport.export_dxf(collector)
    xdata = ExtendedTags(DXFTag(c, v) for c, v in collector.tags).xdata[0]
    assert xdata[0] == (1001, "ACAD")
    assert xdata[1] == (1000, "MVIEW")
    assert xdata[2] == (1002, "{")
    assert xdata[-1] == (1002, "}")


def test_post_load_hook_resolves_frozen_layer_handles_into_names():
    doc = ezdxf.new("R2000")
    l1 = doc.layers.new("Layer1")
    l2 = doc.layers.new("Layer2")
    handles = [l1.dxf.handle, l2.dxf.handle]
    viewport = Viewport.from_text(ENTITY_R2000)
    # implant some handles
    viewport.frozen_layers = handles
    result = viewport.post_load_hook(doc)
    assert result is None
    assert viewport.frozen_layers == [
        "Layer1",
        "Layer2",
    ], "Layer handles must be resolved"


class TestFrozenLayers:
    @pytest.fixture
    def vp(self):
        return Viewport.new("F000")

    def test_set_and_get__frozen_layer_names(self, vp):
        layer_names = ["bricks", "steel", "glass"]
        vp.frozen_layers = layer_names
        assert layer_names == vp.frozen_layers

    def test_freeze_a_specific_layer(self, vp):
        vp.freeze("MyLayer")
        assert vp.frozen_layers == ["MyLayer"]

    def test_freezing_a_layer_twice_does_not_duplicate_entry(self, vp):
        vp.freeze("MyLayer")
        vp.freeze("MYLAYER")
        assert vp.frozen_layers == ["MyLayer"]

    def test_is_a_specific_layer_frozen(self, vp):
        vp.freeze("MyLayer")
        assert vp.is_frozen("MyLayer") is True
        assert (
            vp.is_frozen("MYLAYER") is True
        ), "layer names are case insensitive!"
        assert vp.is_frozen("OTHER_LAYER") is False

    def test_thaw_a_specific_layer(self, vp):
        vp.freeze("MyLayer")
        vp.thaw("MYLAYER")
        assert len(vp.frozen_layers) == 0, "layer names are case insensitive!"

    def test_ignore_thawing_non_frozen_layers_silently(self, vp):
        vp.freeze("MyLayer")
        vp.thaw("LayerA")
        vp.thaw("LayerB")
        assert vp.frozen_layers == ["MyLayer"]


def test_is_top_view():
    vp: Viewport = Viewport.from_text(ENTITY_R2000)
    assert vp.is_top_view is True


def test_get_scale():
    vp: Viewport = Viewport.from_text(ENTITY_R2000)
    assert vp.get_scale() == 1.0


def test_get_transformation_matrix():
    vp: Viewport = Viewport.from_text(ENTITY_R2000)
    m = vp.get_transformation_matrix()
    assert m.transform((1, 2, 3)).isclose((1, 2, 3))


def test_has_clipping_path():
    vp: Viewport = Viewport.from_text(ENTITY_R2000)
    assert vp.has_extended_clipping_path is False


def test_clipping_path_corners():
    vp: Viewport = Viewport.from_text(ENTITY_R2000)
    # the clipping rectangle as corner vertices
    assert len(vp.clipping_rect_corners()) == 4


def test_clipping_rect():
    vp: Viewport = Viewport.from_text(ENTITY_R2000)
    assert len(vp.clipping_rect()) == 2


def test_aspect_ratio():
    vp: Viewport = Viewport.new()
    vp.dxf.width = 2.0
    vp.dxf.height = 1.0
    assert vp.get_aspect_ratio() == 2.0


def test_invalid_aspect_ratio():
    vp: Viewport = Viewport.new()
    vp.dxf.width = 2.0
    vp.dxf.height = 0.0
    assert vp.get_aspect_ratio() == 0.0


def test_modelspace_limits():
    vp: Viewport = Viewport.new(dxfattribs={
        "width": 3.0,
        "height": 2.0,
        "view_center_point": (5, 7),
        "view_height": 6.0,
    })
    # view_width = 4.0
    x0, y0, x1, y1 = vp.get_modelspace_limits()
    assert x0 == pytest.approx(0.5)
    assert y0 == pytest.approx(4.0)
    assert x1 == pytest.approx(9.5)
    assert y1 == pytest.approx(10.0)


def test_modelspace_limits_rotated():
    vp: Viewport = Viewport.new(dxfattribs={
        "width": 2.0,
        "height": 1.0,
        "view_center_point": (2, 2),
        "view_height": 2.0,
        "view_twist_angle": 90
    })
    # view_width = 4.0
    x0, y0, x1, y1 = vp.get_modelspace_limits()
    assert x0 == pytest.approx(1.0)
    assert y0 == pytest.approx(-4.0)
    assert x1 == pytest.approx(3.0)
    assert y1 == pytest.approx(0.0)
