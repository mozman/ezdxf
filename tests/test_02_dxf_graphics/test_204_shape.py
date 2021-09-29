# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
import pytest

from ezdxf.entities.shape import Shape
from ezdxf.lldxf.const import DXF12, DXF2000
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text

TEST_CLASS = Shape
TEST_TYPE = "SHAPE"

ENTITY_R12 = """0
SHAPE
5
0
8
0
10
0.0
20
0.0
30
0.0
40
1.0
2
NAME
50
0.0
41
1.0
51
0.0
"""

ENTITY_R2000 = """0
SHAPE
5
0
330
0
100
AcDbEntity
8
0
100
AcDbShape
10
0.0
20
0.0
30
0.0
40
1.0
2
NAME
50
0.0
41
1.0
51
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
            "insert": (1, 2, 3),
        },
    )
    assert entity.dxf.layer == "0"
    assert entity.dxf.color == 7
    assert entity.dxf.linetype == "BYLAYER"
    assert entity.dxf.insert == (1, 2, 3)
    assert entity.dxf.insert.x == 1, "is not Vec3 compatible"
    assert entity.dxf.insert.y == 2, "is not Vec3 compatible"
    assert entity.dxf.insert.z == 3, "is not Vec3 compatible"
    # can set DXF R2007 value
    entity.dxf.shadow_mode = 1
    assert entity.dxf.shadow_mode == 1
    assert entity.dxf.extrusion == (0.0, 0.0, 1.0)
    assert entity.dxf.hasattr("extrusion") is False, "just the default value"


def test_load_from_text(entity):
    assert entity.dxf.layer == "0"
    assert entity.dxf.color == 256, "default color is 256 (by layer)"
    assert entity.dxf.insert == (0, 0, 0)


@pytest.mark.parametrize(
    "txt,ver", [(ENTITY_R2000, DXF2000), (ENTITY_R12, DXF12)]
)
def test_write_dxf(txt, ver):
    expected = basic_tags_from_text(txt)
    shape = TEST_CLASS.from_text(txt)
    collector = TagCollector(dxfversion=ver, optional=True)
    shape.export_dxf(collector)
    assert collector.tags == expected

    collector2 = TagCollector(dxfversion=ver, optional=False)
    shape.export_dxf(collector2)
    assert collector.has_all_tags(collector2)
