# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created 2019-03-08
import pytest

from ezdxf.entities.hatch import Hatch
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text

HATCH = """0
HATCH
5
0
330
0
100
AcDbEntity
8
0
62
1
100
AcDbHatch
10
0.0
20
0.0
30
0.0
210
0.0
220
0.0
230
1.0
2
SOLID
70
1
71
0
91
0
75
1
76
1
98
1
10
0.0
20
0.0
"""


@pytest.fixture
def entity():
    return Hatch.from_text(HATCH)


def test_if_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES

    assert "HATCH" in ENTITY_CLASSES


def test_default_init():
    entity = Hatch()
    assert entity.dxftype() == "HATCH"
    assert entity.dxf.handle is None
    assert entity.dxf.owner is None


def test_default_new():
    entity = Hatch.new(
        handle="ABBA",
        owner="0",
        dxfattribs={
            "color": 7,
        },
    )
    assert entity.dxf.layer == "0"
    assert entity.dxf.color == 7


def test_load_from_text(entity):
    assert entity.dxf.layer == "0"
    assert entity.dxf.color == 1, "default color is 1"


def test_write_dxf():
    entity = Hatch.from_text(HATCH)
    result = TagCollector.dxftags(entity)
    expected = basic_tags_from_text(HATCH)
    assert result == expected


def test_write_correct_polyline_path_tag_order(entity):
    entity = Hatch.from_text(HATCH)
    entity.paths.add_polyline_path(
        [(0, 0), (1, 0), (1, 1)], is_closed=True,
    )
    result = TagCollector.dxftags(entity)
    tags = list(result.pop_tags([92, 72, 73]))
    # 92 = path type 3: external polyline path
    # 72 = has_bulge
    # 73 = is_closed
    # The group codes 72 and 73 are swapped in comparison to MPOLYGON
    assert tags == [(92, 3), (72, 0), (73, 1)]
