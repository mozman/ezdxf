# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
import pytest

import ezdxf
from ezdxf.entities.viewport import Viewport
from ezdxf.lldxf.extendedtags import ExtendedTags, DXFTag
from ezdxf.lldxf.const import DXF12, DXF2000
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text

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


def test_viewport_set_frozen_layer_names():
    viewport = Viewport.new("F000")
    layer_names = ["bricks", "steel", "glass"]
    viewport.frozen_layers = layer_names
    assert layer_names == viewport.frozen_layers


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
