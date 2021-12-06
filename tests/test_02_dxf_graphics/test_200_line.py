# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
import pytest
import math

from ezdxf.entities.line import Line
from ezdxf.lldxf.const import DXF12, DXF2000, DXFValueError
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text
from ezdxf.math import Matrix44

TEST_CLASS = Line
TEST_TYPE = "LINE"

ENTITY_R12 = """0
LINE
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
11
1.0
21
1.0
31
1.0
"""

ENTITY_R2000 = """0
LINE
5
0
330
0
100
AcDbEntity
8
0
100
AcDbLine
10
0.0
20
0.0
30
0.0
11
1.0
21
1.0
31
1.0
"""


@pytest.fixture(params=[ENTITY_R12, ENTITY_R2000])
def line(request):
    return Line.from_text(request.param)


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES

    assert TEST_TYPE in ENTITY_CLASSES


def test_default_init():
    entity = Line()
    assert entity.dxftype() == TEST_TYPE


def test_default_new():
    entity = Line.new(
        handle="ABBA",
        owner="0",
        dxfattribs={
            "color": "7",
            "start": (1, 2, 3),
            "end": (4, 5, 6),
        },
    )
    assert entity.dxf.layer == "0"
    assert entity.dxf.color == 7
    assert entity.dxf.start == (1, 2, 3)
    assert entity.dxf.start.x == 1, "is not Vec3 compatible"
    assert entity.dxf.start.y == 2, "is not Vec3 compatible"
    assert entity.dxf.start.z == 3, "is not Vec3 compatible"
    assert entity.dxf.end == (4, 5, 6)
    assert entity.dxf.extrusion == (0.0, 0.0, 1.0)
    assert entity.dxf.hasattr("extrusion") is False, "just the default value"

    # can set DXF R2007 value
    entity.dxf.shadow_mode = 1
    assert entity.dxf.shadow_mode == 1


def test_load_from_text(line):
    assert line.dxf.layer == "0"
    assert line.dxf.color == 256, "default color is 256 (by layer)"
    assert line.dxf.start == (0, 0, 0)
    assert line.dxf.end == (1, 1, 1)


@pytest.mark.parametrize(
    "txt,ver", [(ENTITY_R2000, DXF2000), (ENTITY_R12, DXF12)]
)
def test_write_dxf(txt, ver):
    expected = basic_tags_from_text(txt)
    line = TEST_CLASS.from_text(txt)
    collector = TagCollector(dxfversion=ver, optional=True)
    line.export_dxf(collector)
    assert collector.tags == expected

    collector2 = TagCollector(dxfversion=ver, optional=False)
    line.export_dxf(collector2)
    assert collector.has_all_tags(collector2)


def test_get_pass_through_ocs():
    line = Line.new(
        dxfattribs={
            "start": (0, 0, 0),
            "end": (1, 0, 0),
            "extrusion": (0, 0, -1),
        }
    )
    ocs = line.ocs()
    assert ocs.to_wcs((0, 0, 0)) == (0, 0, 0)
    assert ocs.to_wcs((1, 0, 0)) == (1, 0, 0)


def test_transform():
    line = Line.new(
        dxfattribs={
            "start": (0, 0, 0),
            "end": (1, 0, 0),
            "extrusion": (0, 1, 0),
        }
    )
    m = Matrix44.translate(1, 2, 3)
    line.transform(m)

    # simple 3D entity - no OCS transformation,
    assert line.dxf.start == (1, 2, 3)
    assert line.dxf.end == (2, 2, 3)
    # extrusion direction without translation - not an OCS extrusion vector!
    assert line.dxf.extrusion == (0, 1, 0)

    # Create new entity by transformation:
    new_line = line.copy()
    new_line.transform(m)

    assert new_line.dxf.start == (2, 4, 6)
    assert new_line.dxf.end == (3, 4, 6)
    assert new_line.dxf.extrusion == (0, 1, 0)


def test_translation():
    line = Line.new(
        dxfattribs={
            "start": (0, 0, 0),
            "end": (1, 0, 0),
            "extrusion": (0, 1, 0),
        }
    )
    line.translate(1, 2, 3)
    assert line.dxf.start == (1, 2, 3)
    assert line.dxf.end == (2, 2, 3)


def test_rotation():
    line = Line.new(
        dxfattribs={
            "start": (0, 0, 0),
            "end": (1, 0, 0),
            "extrusion": (0, 1, 0),
        }
    )
    angle = math.pi / 4
    m = Matrix44.z_rotate(angle)
    line.transform(m)
    assert line.dxf.start == (0, 0, 0)
    assert line.dxf.end.isclose(
        (math.cos(angle), math.sin(angle), 0), abs_tol=1e-9
    )
    assert line.dxf.extrusion.isclose(
        (-math.cos(angle), math.sin(angle), 0), abs_tol=1e-9
    )
    assert line.dxf.thickness == 0


def test_scaling():
    line = Line.new(
        dxfattribs={
            "start": (0, 0, 0),
            "end": (1, 0, 0),
            "extrusion": (0, 1, 0),
            "thickness": 2,
        }
    )
    m = Matrix44.scale(2, 2, 0)
    line.transform(m)
    assert line.dxf.start == (0, 0, 0)
    assert line.dxf.end == (2, 0, 0)
    assert line.dxf.extrusion == (0, 1, 0)
    assert line.dxf.thickness == 4


def test_copy_entity_transparency():
    line = Line()
    line2 = line.copy()
    assert line2.dxf.hasattr("transparency") is False

    line.transparency = 0.5
    line2 = line.copy()
    assert line2.dxf.transparency == 0x0200007F


def test_setting_invalid_transparency_value_raises_exception():
    line = Line()
    with pytest.raises(DXFValueError):
        line.dxf.transparency = 0


ERR_LINE = """0
LINE
5
0
330
0
100
AcDbEntity
100
AcDbLine
8
0
62
1
6
Linetype
10
0.0
20
0.0
30
0.0
11
1.0
21
1.0
31
1.0
"""

def test_recover_acdb_entity_tags():
    line = Line.from_text(ERR_LINE)
    assert line.dxf.layer == "0"
    assert line.dxf.color == 1
    assert line.dxf.linetype == "Linetype"
