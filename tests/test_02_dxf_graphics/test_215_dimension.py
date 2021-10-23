# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
import pytest
import math

import ezdxf
from ezdxf.math import Vec3, Matrix44
from ezdxf.entities.dimension import Dimension, linear_measurement
from ezdxf.lldxf.const import DXF12, DXF2000
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text
from ezdxf.render.dim_base import format_text, DXFValueError, apply_dimpost

TEST_CLASS = Dimension
TEST_TYPE = "DIMENSION"

ENTITY_R12 = """0
DIMENSION
5
0
8
0
2
*D0
3
Standard
10
0.0
20
0.0
30
0.0
11
0.0
21
0.0
31
0.0
12
0.0
22
0.0
32
0.0
70
0
1

13
0.0
23
0.0
33
0.0
14
0.0
24
0.0
34
0.0
15
0.0
25
0.0
35
0.0
16
0.0
26
0.0
36
0.0
40
1.0
50
0.0
"""

ENTITY_R2000 = """  0
DIMENSION
5
0
330
0
100
AcDbEntity
8
0
100
AcDbDimension
2
*D0
3
Standard
10
0.0
20
0.0
30
0.0
11
0.0
21
0.0
31
0.0
70
32
71
5
42
0.0
100
AcDbAlignedDimension
 13
0.0
 23
0.0
 33
0.0
 14
0.0
 24
0.0
 34
0.0
50
0
100
AcDbRotatedDimension
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
            "defpoint": (1, 2, 3),
        },
    )
    assert entity.dxf.layer == "0"
    assert entity.dxf.color == 7
    assert entity.dxf.linetype == "BYLAYER"
    assert entity.dxf.defpoint == (1, 2, 3)
    assert entity.dxf.defpoint.x == 1, "is not Vec3 compatible"
    assert entity.dxf.defpoint.y == 2, "is not Vec3 compatible"
    assert entity.dxf.defpoint.z == 3, "is not Vec3 compatible"
    # can set DXF R2007 value
    entity.dxf.shadow_mode = 1
    assert entity.dxf.shadow_mode == 1


def test_load_from_text(entity):
    assert entity.dxf.layer == "0"
    assert entity.dxf.color == 256, "default color is 256 (by layer)"
    assert entity.dxf.defpoint == (0, 0, 0)


@pytest.mark.parametrize(
    "txt,ver", [(ENTITY_R2000, DXF2000), (ENTITY_R12, DXF12)]
)
def test_write_dxf(txt, ver):
    expected = basic_tags_from_text(txt)
    dimension = TEST_CLASS.from_text(txt)
    collector = TagCollector(dxfversion=ver, optional=True)
    dimension.export_dxf(collector)
    assert collector.tags == expected

    collector2 = TagCollector(dxfversion=ver, optional=False)
    dimension.export_dxf(collector2)
    assert collector.has_all_tags(collector2)


def test_missing_block_geometry_name():
    doc = ezdxf.new()
    dim = Dimension.new(doc=doc)
    assert dim.get_geometry_block() is None


def test_format_text():
    assert format_text(0, dimrnd=0, dimdec=1, dimzin=0, dimpost="<>") == "0.0"
    assert format_text(0, dimrnd=0, dimdec=1, dimzin=4, dimpost="<>") == "0"
    assert format_text(0, dimrnd=0, dimdec=1, dimzin=8, dimpost="<>") == "0"
    assert (
        format_text(100, dimrnd=0.0, dimdec=0, dimzin=8, dimpost="<>") == "100"
    )
    assert (
        format_text(100, dimrnd=None, dimdec=0, dimzin=8, dimpost="<>") == "100"
    )
    assert (
        format_text(100, dimrnd=0, dimdec=None, dimzin=8, dimpost="<>") == "100"
    )
    assert (
        format_text(100, dimrnd=None, dimdec=None, dimzin=8, dimpost="<>")
        == "100"
    )
    assert (
        format_text(1.23, dimrnd=0.5, dimdec=1, dimzin=0, dimpost="<> mm")
        == "1.0 mm"
    )
    assert (
        format_text(1.23, dimrnd=0.5, dimdec=1, dimzin=8, dimpost="<> mm")
        == "1 mm"
    )
    assert (
        format_text(1.23, dimrnd=0.5, dimdec=1, dimzin=12, dimpost="<> mm")
        == "1 mm"
    )
    assert (
        format_text(10.51, dimrnd=0.5, dimdec=2, dimzin=0, dimpost="<> mm")
        == "10.50 mm"
    )
    assert (
        format_text(10.51, dimrnd=0.5, dimdec=2, dimzin=8, dimpost="<> mm")
        == "10.5 mm"
    )
    assert (
        format_text(0.51, dimrnd=0.5, dimdec=2, dimzin=0, dimpost="mm <>")
        == "mm 0.50"
    )
    assert (
        format_text(0.51, dimrnd=0.5, dimdec=2, dimzin=4, dimpost="mm <>")
        == "mm .50"
    )
    assert (
        format_text(-0.51, dimrnd=0.5, dimdec=2, dimzin=4, dimpost="mm <>")
        == "mm -.50"
    )
    assert (
        format_text(-0.11, dimrnd=0.1, dimdec=2, dimzin=4, dimpost="mm <>")
        == "mm -.10"
    )
    assert format_text(-0.51, dimdsep=",", dimpost="! <> m") == "! -0,51 m"

    assert format_text(-0.51, dimdsep=",", dimpost="") == "-0,51"
    assert format_text(-0.51, dimdsep=",", dimpost="<>") == "-0,51"
    assert format_text(-0.51, dimdsep=",", dimpost="><>") == ">-0,51"
    assert (
        format_text(-0.51, dimdsep=",", dimpost="<><>") == "-0,51<>"
    )  # ignore stupid
    with pytest.raises(DXFValueError):
        _ = format_text(-0.51, dimpost="<")


def test_apply_dim_post():
    assert apply_dimpost("0°", "<>") == "0°"
    assert apply_dimpost("30°", "x <>") == "x 30°"
    assert apply_dimpost("30°", "<> x") == "30° x"
    assert apply_dimpost("30°", "x <> x") == "x 30° x"


def test_linear_measurement_without_ocs():
    measurement = linear_measurement(Vec3(0, 0, 0), Vec3(1, 0, 0))
    assert measurement == 1

    measurement = linear_measurement(
        Vec3(0, 0, 0), Vec3(1, 0, 0), angle=math.radians(45)
    )
    assert math.isclose(measurement, 1.0 / math.sqrt(2.0))

    measurement = linear_measurement(
        Vec3(0, 0, 0), Vec3(1, 0, 0), angle=math.radians(90)
    )
    assert math.isclose(measurement, 0, abs_tol=1e-12)


def test_dimension_transform_interface():
    dim = Dimension()
    dim.dxf.insert = (1, 0, 0)  # OCS point
    dim.dxf.defpoint = (0, 1, 0)  # WCS point
    dim.dxf.angle = 45

    dim.transform(Matrix44.translate(1, 2, 3))
    assert dim.dxf.insert == (2, 2, 3)
    assert dim.dxf.defpoint == (1, 3, 3)
    assert dim.dxf.angle == 45

    dim.transform(Matrix44.z_rotate(math.radians(45)))
    assert math.isclose(dim.dxf.angle, 90)
