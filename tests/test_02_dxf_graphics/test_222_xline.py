# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created 2019-03-05
import pytest

from ezdxf.entities.xline import XLine
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text
from ezdxf.math import Matrix44

XLINE = """0
XLINE
5
0
330
0
100
AcDbEntity
8
0
100
AcDbXline
10
0.0
20
0.0
30
0.0
11
1.0
21
0.0
31
0.0
"""


@pytest.fixture
def entity():
    return XLine.from_text(XLINE)


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES

    assert "XLINE" in ENTITY_CLASSES


def test_default_init():
    entity = XLine()
    assert entity.dxftype() == "XLINE"
    assert entity.dxf.handle is None
    assert entity.dxf.owner is None


def test_default_new():
    entity = XLine.new(
        handle="ABBA",
        owner="0",
        dxfattribs={
            "color": 7,
            "start": (1, 2, 3),
            "unit_vector": (4, 5, 6),
        },
    )
    assert entity.dxf.layer == "0"
    assert entity.dxf.color == 7
    assert entity.dxf.start == (1, 2, 3)
    assert entity.dxf.unit_vector == (4, 5, 6)


def test_load_from_text(entity):
    assert entity.dxf.layer == "0"
    assert entity.dxf.color == 256, "default color is 256 (by layer)"
    assert entity.dxf.start == (0, 0, 0)
    assert entity.dxf.unit_vector == (1, 0, 0)


def test_write_dxf():
    entity = XLine.from_text(XLINE)
    result = TagCollector.dxftags(entity)
    expected = basic_tags_from_text(XLINE)
    assert result == expected


def test_xline_transform():
    # same implementation for Ray()
    xline = XLine.new(dxfattribs={"start": (2, 3, 4), "unit_vector": (1, 0, 0)})
    # 1. scaling - 2. rotation - 3. translation
    m = Matrix44.chain(Matrix44.scale(2, 2, 3), Matrix44.translate(1, 1, 1))
    xline.transform(m)

    assert xline.dxf.start == (5, 7, 13)
    assert xline.dxf.unit_vector == (1, 0, 0)


def test_xline_fast_translation():
    # same implementation for Ray()
    xline = XLine.new(dxfattribs={"start": (2, 3, 4), "unit_vector": (1, 0, 0)})
    xline.translate(1, 2, 3)
    assert xline.dxf.start == (3, 5, 7)
    assert xline.dxf.unit_vector == (1, 0, 0)
