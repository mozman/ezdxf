#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import pytest

import ezdxf
from ezdxf.entities import MPolygon
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
    result = TagCollector.dxftags(entity, dxfversion=ezdxf.const.DXF2000)
    expected = basic_tags_from_text(MPOLYGON_NO_FILL)
    assert result == expected
    assert result.get_first_value(71) == 0  # pattern fill
    tags = list(result.pop_tags([52, 41, 77, 78]))
    assert tags == [
        (52, 0),  # pattern_angle tag must be presents
        (41, 1),  # pattern_scale tag must be presents
        (77, 0),  # pattern_double tag must be presents
        (78, 0),  # patten length tag must be presents
    ], "required pattern tags are not in expected order"

    assert (
        result.has_tag(450) is False
    ), "gradient data is not supported for DXF R2000"


def test_write_dxf_r2004_no_fill_requires_basic_gradient_data(entity):
    entity = MPolygon.from_text(MPOLYGON_NO_FILL)
    result = TagCollector.dxftags(entity, dxfversion=ezdxf.const.DXF2004)
    tags = list(result.pop_tags([450, 451, 460, 461, 452, 462, 453, 470]))
    assert tags == [
        (450, 0),  # kind = solid fill
        (451, 0),  # reserved for the future
        (460, 0),  # angle in radians
        (461, 0),  # centered
        (452, 0),  # one color
        (462, 0),  # tint
        (453, 0),  # number of colors
        (470, ""),  # gradient name
    ], "required gradient tags are not in expected order"


def test_write_dxf_with_fill(entity):
    entity = MPolygon.from_text(MPOLYGON_NO_FILL)
    entity.dxf.solid_fill = 1
    entity.dxf.fill_color = 163
    result = TagCollector.dxftags(entity, dxfversion=ezdxf.const.DXF2000)
    assert result.get_first_value(71) == 1  # solid_fill
    assert (
        result.has_tag(52) is False
    ), "pattern_angle tag should not be presents"
    assert (
        result.has_tag(41) is False
    ), "pattern_scale tag should not be presents"
    assert (
        result.has_tag(77) is False
    ), "pattern_double tag should not be presents"
    assert (
        result.has_tag(78) is False
    ), "pattern length tag should not be presents"
    assert (
        result.has_tag(63) is False
    ), "fill color tag is not supported for DXF R2000"


def test_write_dxf_R2004_with_fill(entity):
    entity = MPolygon.from_text(MPOLYGON_NO_FILL)
    entity.dxf.solid_fill = 1
    entity.dxf.fill_color = 163
    result = TagCollector.dxftags(entity, dxfversion=ezdxf.const.DXF2004)
    assert result.get_first_value(63) == 163, "missing fill color tag"

    tags = list(result.pop_tags([450, 451, 460, 461, 452, 462, 453, 470]))
    assert tags == [
        (450, 0),  # kind = solid fill
        (451, 0),  # reserved for the future
        (460, 0),  # angle in radians
        (461, 0),  # centered
        (452, 0),  # one color
        (462, 0),  # tint
        (453, 0),  # number of colors
        (470, ""),  # gradient name
    ], "required gradient tags are not in expected order"


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
