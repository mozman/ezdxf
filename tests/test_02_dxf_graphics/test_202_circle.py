# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
# created 2019-02-15
import pytest

from ezdxf.entities.circle import Circle
from ezdxf.lldxf.const import DXF12, DXF2000
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text
from ezdxf.math import Vector, Matrix44, OCS, NonUniformScalingError

TEST_CLASS = Circle
TEST_TYPE = 'CIRCLE'

ENTITY_R12 = """0
CIRCLE
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
"""

ENTITY_R2000 = """0
CIRCLE
5
0
330
0
100
AcDbEntity
8
0
100
AcDbCircle
10
0.0
20
0.0
30
0.0
40
1.0
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
    assert entity.dxf.handle is None
    assert entity.dxf.owner is None


def test_negative_radius():
    circle = Circle.new(dxfattribs={'radius': -1})
    assert circle.dxf.radius == -1, 'Radius < 0 is valid'


def test_zero_radius():
    circle = Circle.new(dxfattribs={'radius': 0})
    assert circle.dxf.radius == 0, 'Radius == 0 is valid'


def test_extrusion_can_not_be_a_null_vector():
    circle = Circle.new(dxfattribs={'extrusion': (0, 0, 0)})
    assert circle.dxf.extrusion == (0, 0, 1), 'expected default extrusion'


def test_default_new():
    entity = TEST_CLASS.new(handle='ABBA', owner='0', dxfattribs={
        'color': '7',
        'center': (1, 2, 3),
        'radius': 2.5,
    })
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 7
    assert entity.dxf.linetype == 'BYLAYER'

    assert entity.dxf.center == (1, 2, 3)
    assert entity.dxf.center.x == 1, 'is not Vector compatible'
    assert entity.dxf.center.y == 2, 'is not Vector compatible'
    assert entity.dxf.center.z == 3, 'is not Vector compatible'
    assert entity.dxf.radius == 2.5
    # can set DXF R2007 value
    entity.dxf.shadow_mode = 1
    assert entity.dxf.shadow_mode == 1
    assert entity.dxf.extrusion == (0.0, 0.0, 1.0)
    assert entity.dxf.hasattr('extrusion') is False, 'just the default value'


def test_load_from_text(entity):
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 256, 'default color is 256 (by layer)'
    assert entity.dxf.center == (0, 0, 0)
    assert entity.dxf.radius == 1


def test_get_point_2d_circle():
    radius = 2.5
    z = 3.0
    circle = TEST_CLASS.new(handle='ABBA', owner='0', dxfattribs={
        'center': (1, 2, z),
        'radius': radius,
    })
    vertices = list(circle.vertices([90]))
    assert vertices[0].isclose(Vector(1, 2 + radius, z))


def test_get_point_with_ocs():
    circle = TEST_CLASS.new(handle='ABBA', owner='0', dxfattribs={
        'center': (1, 2, 3),
        'radius': 2.5,
        'extrusion': (0, 0, -1),
    })
    vertices = list(circle.vertices([90, 180]))
    assert vertices[0].isclose(Vector(-1, 4.5, -3), abs_tol=1e-6)
    assert vertices[1].isclose(Vector(1.5, 2, -3), abs_tol=1e-6)


@pytest.mark.parametrize("txt,ver",
                         [(ENTITY_R2000, DXF2000), (ENTITY_R12, DXF12)])
def test_write_dxf(txt, ver):
    expected = basic_tags_from_text(txt)
    circle = TEST_CLASS.from_text(txt)
    collector = TagCollector(dxfversion=ver, optional=True)
    circle.export_dxf(collector)
    assert collector.tags == expected

    collector2 = TagCollector(dxfversion=ver, optional=False)
    circle.export_dxf(collector2)
    assert collector.has_all_tags(collector2)


def test_circle_default_ocs():
    circle = Circle.new(dxfattribs={'center': (2, 3, 4), 'thickness': 2})
    # 1. rotation - 2. scaling - 3. translation
    m = Matrix44.chain(Matrix44.scale(2, 2, 3), Matrix44.translate(1, 1, 1))
    # default extrusion is (0, 0, 1), therefore scale(2, 2, ..) is a uniform
    # scaling in the xy-play of the OCS
    circle.transform(m)

    assert circle.dxf.center == (5, 7, 13)
    assert circle.dxf.extrusion == (0, 0, 1)
    assert circle.dxf.thickness == 6


def test_circle_fast_translation():
    circle = Circle.new(
        dxfattribs={'center': (2, 3, 4), 'extrusion': Vector.random()})
    ocs = circle.ocs()
    offset = Vector(1, 2, 3)
    center = ocs.to_wcs(circle.dxf.center) + offset
    circle.translate(*offset)
    assert ocs.to_wcs(circle.dxf.center).isclose(center, abs_tol=1e-9)


def test_circle_non_uniform_scaling():
    circle = Circle.new(dxfattribs={'center': (2, 3, 4), 'extrusion': (0, 1, 0),
                                    'thickness': 2})
    # extrusion in WCS y-axis, therefore scale(2, ..., 3) is a non uniform
    # scaling in the xy-play of the OCS which is the xz-plane of the WCS
    with pytest.raises(NonUniformScalingError):
        circle.transform(Matrix44.scale(2, 2, 3))

    # source values unchanged after exception
    assert circle.dxf.center == (2, 3, 4)
    assert circle.dxf.extrusion == (0, 1, 0)
    assert circle.dxf.thickness == 2


def test_circle_user_ocs():
    center = (2, 3, 4)
    extrusion = (0, 1, 0)

    circle = Circle.new(
        dxfattribs={'center': center, 'extrusion': extrusion, 'thickness': 2})
    ocs = OCS(extrusion)
    v = ocs.to_wcs(center)  # (-2, 4, 3)
    v = Vector(v.x * 2, v.y * 4, v.z * 2)
    v += (1, 1, 1)
    # and back to OCS, extrusion is unchanged
    result = ocs.from_wcs(v)

    m = Matrix44.chain(Matrix44.scale(2, 4, 2), Matrix44.translate(1, 1, 1))
    circle.transform(m)
    assert circle.dxf.center == result
    assert circle.dxf.extrusion == (0, 1, 0)
    assert circle.dxf.thickness == 8  # in WCS y-axis


@pytest.mark.parametrize('radius, sagitta, count', [
    (1, 0.35, 5), (1, 0.10, 8),
    (0, 0.35, 0), (0, 0.10, 0),  # radius 0 works but yields nothing
    (-1, 0.35, 5), (-1, 0.10, 8),  # negative radius same as positive radius
])
def test_circle_flattening(radius, sagitta, count):
    circle = Circle.new(dxfattribs={'radius': radius})
    assert len(list(circle.flattening(sagitta))) == count
