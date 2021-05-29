#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import pytest

import ezdxf
from ezdxf.entities.hatch import MPolygon
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text


# MPolygon is similar to Hatch
@pytest.fixture
def entity():
    return MPolygon.from_text(MPOLYGON_NO_FILL)


def test_if_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES

    assert "MPOLYGON" in ENTITY_CLASSES


def test_default_init():
    entity = MPolygon()
    assert entity.dxftype() == "MPOLYGON"
    assert entity.dxf.handle is None
    assert entity.dxf.owner is None


def test_default_new():
    entity = MPolygon.new(
        handle="ABBA",
        owner="0",
        dxfattribs={
            "color": 7,  # color of boundary paths!
        },
    )
    assert entity.dxf.layer == "0"
    assert entity.dxf.color == 7
    assert entity.dxf.version == 1
    assert entity.dxf.solid_fill == 0
    assert entity.dxf.fill_color == ezdxf.const.BYLAYER


def test_fill_properties_without_solid_filling():
    entity = MPolygon()
    entity.dxf.solid_fill = 0
    assert entity.has_solid_fill is False
    assert entity.has_pattern_fill is True


def test_fill_properties_with_solid_filling():
    entity = MPolygon()
    entity.dxf.solid_fill = 1
    assert entity.has_solid_fill is True
    assert entity.has_pattern_fill is False


def test_load_from_text(entity):
    assert entity.dxf.layer == "mpolygons"
    assert entity.dxf.color == 1
    assert entity.dxf.version == 1
    assert entity.dxf.solid_fill == 0
    assert len(entity.paths) == 2
    assert entity.dxf.pattern_name == ""


def test_write_dxf_no_fill(entity):
    entity = MPolygon.from_text(MPOLYGON_NO_FILL)
    result = TagCollector.dxftags(entity)
    expected = basic_tags_from_text(MPOLYGON_NO_FILL)
    assert result == expected
    assert result.has_tag(78) is True, "unknown1 tag must be presents"


def test_write_dxf_with_fill(entity):
    entity = MPolygon.from_text(MPOLYGON_NO_FILL)
    entity.dxf.solid_fill = 1
    result = TagCollector.dxftags(entity)
    assert result.get_first_value(71) == 1  # solid_fill
    assert result.has_tag(78) is False, "unknown1 tag should not be presents"


def test_write_correct_polyline_path_tag_order(entity):
    entity = MPolygon.from_text(MPOLYGON_NO_FILL)
    result = TagCollector.dxftags(entity)
    tags = list(result.pop_tags([92, 72, 73]))
    # 92 = path type 2: polyline path
    # 73 = is_closed
    # 72 = has_bulge
    # The group codes 73 and 72 are swapped in comparison to HATCH
    # contains 2 polyline paths
    assert tags == [(92, 2), (73, 0), (72, 0), (92, 2), (73, 0), (72, 0)]


MPOLYGON_NO_FILL = """0
MPOLYGON
5
ABBA
330
DEAD
100
AcDbEntity
8
mpolygons
62
1
100
AcDbMPolygon
70
1
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

71
0
91
2
92
2
73
0
72
0
93
5
10
-85.2
20
35.04
10
-85.2
20
35.04
10
-85.2
20
35.04
10
-85.2
20
35.04
10
-85.2
20
35.04
92
2
73
0
72
0
93
4
10
-85.2
20
35.04
10
-85.2
20
35.04
10
-85.2
20
35.04
10
-85.2
20
35.04
76
0
52
0.0
41
1.0
77
0
78
0
11
0.0
21
0.0
99
0
"""

if __name__ == "__main__":
    pytest.main([__file__])
