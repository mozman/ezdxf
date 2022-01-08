# Copyright (c) 2019-2022 Manfred Moitzi
# License: MIT License
import pytest

from ezdxf.entities.block import Block, EndBlk
from ezdxf.lldxf.const import DXF12, DXF2000
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text

TEST_CLASS = Block
TEST_TYPE = "BLOCK"

ENTITY_R12 = """0
BLOCK
5
0
8
0
2
BLOCKNAME
70
0
10
0.0
20
0.0
30
0.0
3
BLOCKNAME
1

"""

ENTITY_R2000 = """0
BLOCK
5
0
330
0
100
AcDbEntity
8
0
100
AcDbBlockBegin
2
BLOCKNAME
70
0
10
0.0
20
0.0
30
0.0
3
BLOCKNAME
1

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
            "base_point": (1, 2, 3),
        },
    )
    assert entity.dxf.layer == "0"
    assert entity.dxf.base_point == (1, 2, 3)
    assert entity.dxf.base_point.x == 1, "is not Vec3 compatible"
    assert entity.dxf.base_point.y == 2, "is not Vec3 compatible"
    assert entity.dxf.base_point.z == 3, "is not Vec3 compatible"


def test_load_from_text(entity):
    assert entity.dxf.layer == "0"
    assert entity.dxf.base_point == (0, 0, 0)


@pytest.mark.parametrize(
    "txt,ver", [(ENTITY_R2000, DXF2000), (ENTITY_R12, DXF12)]
)
def test_write_block_dxf(txt, ver):
    expected = basic_tags_from_text(txt)
    block = TEST_CLASS.from_text(txt)
    collector = TagCollector(dxfversion=ver, optional=True)
    block.export_dxf(collector)
    assert collector.tags == expected

    collector2 = TagCollector(dxfversion=ver, optional=False)
    block.export_dxf(collector2)
    assert collector.has_all_tags(collector2)


ENDBLK_R12 = "  0\nENDBLK\n  5\n0\n  8\n0\n"

ENDBLK_R2000 = """0
ENDBLK
5
0
330
0
100
AcDbEntity
8
0
100
AcDbBlockEnd
"""


@pytest.mark.parametrize(
    "txt,ver", [(ENDBLK_R2000, DXF2000), (ENDBLK_R12, DXF12)]
)
def test_write_endblk_dxf(txt, ver):
    expected = basic_tags_from_text(txt)
    endblk = EndBlk.from_text(txt)
    collector = TagCollector(dxfversion=ver, optional=True)
    endblk.export_dxf(collector)
    assert collector.tags == expected

    collector2 = TagCollector(dxfversion=ver, optional=False)
    endblk.export_dxf(collector2)
    assert collector.has_all_tags(collector2)


MALFORMED_BLOCK = """0
BLOCK
5
0
8
LY_EZDXF
330
0
100
AcDbEntity
2
BLOCKNAME
70
0
10
1.0
20
2.0
30
3.0
100
AcDbBlockBegin
3
IGNORED_BLOCKNAME
1

"""


def test_load_malformed_block():
    block = Block.from_text(MALFORMED_BLOCK)
    assert block.dxf.layer == "LY_EZDXF"
    assert block.dxf.base_point.isclose((1, 2, 3))
    assert block.dxf.name == "BLOCKNAME"


MALFORMED_ENDBLK = """0
ENDBLK
5
0
330
0
100
AcDbBlockEnd
8
LY_EZDXF
100
AcDbEntity
100
AcDbBlockEnd
"""


def test_load_malformed_endblk():
    endblk = EndBlk.from_text(MALFORMED_ENDBLK)
    assert endblk.dxf.layer == "LY_EZDXF"
