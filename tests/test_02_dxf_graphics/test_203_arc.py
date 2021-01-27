# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
import pytest
import math

from ezdxf.math import Vec3, Matrix44
from ezdxf.entities.arc import Arc
from ezdxf.lldxf.const import DXF12, DXF2000
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text


TEST_CLASS = Arc
TEST_TYPE = 'ARC'

ENTITY_R12 = """0
ARC
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
50
0
51
360
"""

ENTITY_R2000 = """0
ARC
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
100
AcDbArc
50
0
51
360
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


def test_default_new():
    entity = TEST_CLASS.new(handle='ABBA', owner='0', dxfattribs={
        'color': '7',
        'center': (1, 2, 3),
        'radius': 2.5,
        'start_angle': 30,
        'end_angle': 290,
    })
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 7
    assert entity.dxf.linetype == 'BYLAYER'

    assert entity.dxf.center == (1, 2, 3)
    assert entity.dxf.center.x == 1, 'is not Vec3 compatible'
    assert entity.dxf.center.y == 2, 'is not Vec3 compatible'
    assert entity.dxf.center.z == 3, 'is not Vec3 compatible'
    assert entity.dxf.radius == 2.5
    assert entity.dxf.start_angle == 30
    assert entity.dxf.end_angle == 290
    # can set DXF R2007 value
    entity.dxf.shadow_mode = 1
    assert entity.dxf.shadow_mode == 1
    assert entity.dxf.extrusion == (0.0, 0.0, 1.0)
    assert entity.dxf.hasattr('extrusion') is False, 'just the default value'


def test_get_start_and_end_vertices_with_ocs():
    arc = TEST_CLASS.new(handle='ABBA', owner='0', dxfattribs={
        'center': (1, 2, 3),
        'radius': 2.5,
        'start_angle': 90,
        'end_angle': 180,
        'extrusion': (0, 0, -1),
    })
    # convenient properties
    assert arc.start_point.isclose(Vec3(-1, 4.5, -3), abs_tol=1e-6)
    assert arc.end_point.isclose(Vec3(1.5, 2, -3), abs_tol=1e-6)

    # more efficient method:
    start, end = list(arc.vertices([arc.dxf.start_angle, arc.dxf.end_angle]))
    assert start.isclose(Vec3(-1, 4.5, -3), abs_tol=1e-6)
    assert end.isclose(Vec3(1.5, 2, -3), abs_tol=1e-6)


def test_load_from_text(entity):
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 256, 'default color is 256 (by layer)'
    assert entity.dxf.center == (0, 0, 0)
    assert entity.dxf.radius == 1
    assert entity.dxf.start_angle == 0
    assert entity.dxf.end_angle == 360


@pytest.mark.parametrize("txt,ver", [(ENTITY_R2000, DXF2000), (ENTITY_R12, DXF12)])
def test_write_dxf(txt, ver):
    expected = basic_tags_from_text(txt)
    arc = TEST_CLASS.from_text(txt)
    collector = TagCollector(dxfversion=ver, optional=True)
    arc.export_dxf(collector)
    assert collector.tags == expected

    collector2 = TagCollector(dxfversion=ver, optional=False)
    arc.export_dxf(collector2)
    assert collector.has_all_tags(collector2)


def test_angles():
    arc = Arc.new(dxfattribs={'radius': 1, 'start_angle': 30, 'end_angle': 60})
    assert tuple(arc.angles(2)) == (30, 60)
    assert tuple(arc.angles(3)) == (30, 45, 60)

    arc.dxf.start_angle = 180
    arc.dxf.end_angle = 0
    assert tuple(arc.angles(2)) == (180, 0)
    assert tuple(arc.angles(3)) == (180, 270, 0)

    arc.dxf.start_angle = -90
    arc.dxf.end_angle = -180
    assert tuple(arc.angles(2)) == (270, 180)
    assert tuple(arc.angles(4)) == (270, 0, 90, 180)


def test_arc_default_ocs():
    arc = Arc.new(dxfattribs={'center': (2, 3, 4), 'thickness': 2, 'start_angle': 30, 'end_angle': 60})
    # 1. rotation - 2. scaling - 3. translation
    m = Matrix44.chain(Matrix44.scale(2, 2, 3), Matrix44.translate(1, 1, 1))
    # default extrusion is (0, 0, 1), therefore scale(2, 2, ..) is a uniform scaling in the xy-play of the OCS
    arc.transform(m)

    assert arc.dxf.center == (5, 7, 13)
    assert arc.dxf.extrusion == (0, 0, 1)
    assert arc.dxf.thickness == 6
    assert math.isclose(arc.dxf.start_angle, 30, abs_tol=1e-9)
    assert math.isclose(arc.dxf.end_angle, 60, abs_tol=1e-9)

    arc.transform(Matrix44.z_rotate(math.radians(30)))
    assert math.isclose(arc.dxf.start_angle, 60, abs_tol=1e-9)
    assert math.isclose(arc.dxf.end_angle, 90, abs_tol=1e-9)


# See also ConstructionArc(): test suite 645 - test_flattening()
@pytest.mark.parametrize('r, s, e, sagitta, count', [
    (1, 0, 180, 0.10, 5),
    (0, 0, 360, 0.10, 0),  # radius 0 works but yields nothing
    (-1, 0, 180, 0.35, 3),  # negative radius same as positive radius
    (1, 270, 90, 0.10, 5),  # start angle > end angle
])
def test_circle_flattening(r, s, e, sagitta, count):
    arc = Arc.new(dxfattribs={
        'radius': r, 'start_angle': s, 'end_angle': e,
    })
    assert len(list(arc.flattening(sagitta))) == count


def test_360_deg_arc_transformation():
    from ezdxf.render import make_path
    arc = Arc.new(dxfattribs={
        'radius': 1, 'start_angle': 0, 'end_angle': 360,
    })
    count1 = len(list(make_path(arc).flattening(0.01)))
    arc.transform(Matrix44.translate(1, 0, 0))
    count2 = len(list(make_path(arc).flattening(0.01)))
    assert count1 == count2

    arc.transform(Matrix44.z_rotate(math.pi/2))
    p = make_path(arc)
    count3 = len(list(p.flattening(0.01)))
    assert count1 == count3

