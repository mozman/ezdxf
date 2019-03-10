# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created 2019-02-15
import pytest
import math

from ezdxf.entities.acis import Body, Solid3d, Region, Surface, ExtrudedSurface, LoftedSurface, RevolvedSurface, \
    SweptSurface
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text

BODY = """0
BODY
5
0
330
0
100
AcDbEntity
8
0
100
AcDbModelerGeometry
70
1
"""


class MockDoc:
    def __init__(self):
        self.dxfversion = 'AC1024'


@pytest.fixture
def entity():
    return Body.from_text(BODY, doc=MockDoc())


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES
    assert 'BODY' in ENTITY_CLASSES
    assert '3DSOLID' in ENTITY_CLASSES
    assert 'REGION' in ENTITY_CLASSES
    assert 'SURFACE' in ENTITY_CLASSES
    assert 'EXTRUDEDSURFACE' in ENTITY_CLASSES
    assert 'LOFTEDSURFACE' in ENTITY_CLASSES
    assert 'REVOLVEDSURFACE' in ENTITY_CLASSES
    assert 'SWEPTSURFACE' in ENTITY_CLASSES


def test_default_init():
    entity = Body()
    assert entity.dxftype() == 'BODY'

    entity = Solid3d()
    assert entity.dxftype() == '3DSOLID'

    entity = Region()
    assert entity.dxftype() == 'REGION'

    entity = Surface()
    assert entity.dxftype() == 'SURFACE'

    entity = ExtrudedSurface()
    assert entity.dxftype() == 'EXTRUDEDSURFACE'

    entity = LoftedSurface()
    assert entity.dxftype() == 'LOFTEDSURFACE'

    entity = RevolvedSurface()
    assert entity.dxftype() == 'REVOLVEDSURFACE'

    entity = SweptSurface()
    assert entity.dxftype() == 'SWEPTSURFACE'


def test_default_new():
    entity = Body.new(handle='ABBA', owner='0', dxfattribs={
        'color': 7,
    })
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 7


def test_load_from_text(entity):
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 256, 'default color is 256 (by layer)'
    assert entity.dxf.version == 1


def test_body_write_dxf():
    entity = Body.from_text(BODY, doc=MockDoc())
    result = TagCollector.dxftags(entity)
    expected = basic_tags_from_text(BODY)
    assert result == expected


def test_region_write_dxf():
    entity = Region.from_text(REGION, doc=MockDoc())
    result = TagCollector.dxftags(entity)
    expected = basic_tags_from_text(REGION)
    assert result == expected


REGION = """0
REGION
5
0
330
0
100
AcDbEntity
8
0
100
AcDbModelerGeometry
70
1
"""


def test_3dsolid_write_dxf():
    entity = Solid3d.from_text(SOLID3D, doc=MockDoc())
    result = TagCollector.dxftags(entity)
    expected = basic_tags_from_text(SOLID3D)
    assert result == expected


SOLID3D = """0
3DSOLID
5
0
330
0
100
AcDbEntity
8
0
100
AcDbModelerGeometry
70
1
100
AcDb3dSolid
350
0
"""


def test_surface_write_dxf():
    entity = Surface.from_text(SURFACE, doc=MockDoc())
    result = TagCollector.dxftags(entity)
    expected = basic_tags_from_text(SURFACE)
    assert result == expected


SURFACE = """0
SURFACE
5
0
330
0
100
AcDbEntity
8
0
100
AcDbModelerGeometry
70
1
100
AcDbSurface
71
0
72
0
"""


def test_extruded_surface_write_dxf():
    entity = ExtrudedSurface.from_text(EXTRUDEDSURFACE, doc=MockDoc())
    result = TagCollector.dxftags(entity)
    expected = basic_tags_from_text(EXTRUDEDSURFACE)
    assert result == expected


EXTRUDEDSURFACE = """0
EXTRUDEDSURFACE
5
0
330
0
100
AcDbEntity
8
0
100
AcDbModelerGeometry
70
1
100
AcDbSurface
71
0
72
0
100
AcDbExtrudedSurface
90
18
10
0.0
20
0.0
30
0.0
40
1.0
40
0.0
40
0.0
40
0.0
40
0.0
40
1.0
40
0.0
40
0.0
40
0.0
40
0.0
40
1.0
40
0.0
40
0.0
40
0.0
40
0.0
40
1.0
42
0.0
43
0.0
44
0.0
45
0.0
48
1.0
49
0.0
46
1.0
46
0.0
46
0.0
46
0.0
46
0.0
46
1.0
46
0.0
46
0.0
46
0.0
46
0.0
46
1.0
46 
0.0
46
0.0
46
0.0
46
0.0
46
1.0
47
1.0
47
0.0
47
0.0
47
0.0
47
0.0
47
1.0
47
0.0
47
0.0
47
0.0
47
0.0
47
1.0
47
0.0
47
0.0
47
0.0
47
0.0
47
1.0
290
0
70
0
71
2
292
1
293
0
294
0
295
1
296
0
11
0.0
21
0.0
31
0.0
"""


def test_lofted_surface_write_dxf():
    entity = LoftedSurface.from_text(LOFTEDSURFACE, doc=MockDoc())
    result = TagCollector.dxftags(entity)
    expected = basic_tags_from_text(LOFTEDSURFACE)
    assert result == expected


LOFTEDSURFACE = """0
LOFTEDSURFACE
5
0
330
0
100
AcDbEntity
8
0
100
AcDbModelerGeometry
70
1
100
AcDbSurface
71
0
72
0
100
AcDbLoftedSurface
40
1.0
40
0.0
40
0.0
40
0.0
40
0.0
40
1.0
40
0.0
40
0.0
40
0.0
40
0.0
40
1.0
40
0.0
40
0.0
40
0.0
40
0.0
40
1.0
70
0
41
0.0
42
0.0
43
0.0
44
0.0
290
0
291
1
292
1
293
1
294
0
295
0
296
0
297
1
"""


def test_revolved_surface_write_dxf():
    entity = RevolvedSurface.from_text(REVOLVEDSURFACE, doc=MockDoc())
    result = TagCollector.dxftags(entity)
    expected = basic_tags_from_text(REVOLVEDSURFACE)
    assert result == expected


REVOLVEDSURFACE = """0
REVOLVEDSURFACE
5
0
330
0
100
AcDbEntity
8
0
100
AcDbModelerGeometry
70
1
100
AcDbSurface
71
0
72
0
100
AcDbRevolvedSurface
90
36
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
1.0
40
0.0
41
0.0
42
1.0
42
0.0
42
0.0
42
0.0
42
0.0
42
1.0
42
0.0
42
0.0
42
0.0
42
0.0
42
1.0
42
0.0
42
0.0
42
0.0
42
0.0
42
1.0
43
0.0
44
0.0
45
0.0
46
0.0
290
0
291
0
"""


def test_swept_surface_write_dxf():
    entity = SweptSurface.from_text(SWEPTSURFACE, doc=MockDoc())
    result = TagCollector.dxftags(entity)
    expected = basic_tags_from_text(SWEPTSURFACE)
    assert result == expected


SWEPTSURFACE = """0
SWEPTSURFACE
5
0
330
0
100
AcDbEntity
8
0
100
AcDbModelerGeometry
70
1
100
AcDbSurface
71
0
72
0
100
AcDbSweptSurface
90
36
91
36
40
1.0
40
0.0
40
0.0
40
0.0
40
0.0
40
1.0
40
0.0
40
0.0
40
0.0
40
0.0
40
1.0
40
0.0
40
0.0
40
0.0
40
0.0
40
1.0
41
1.0
41
0.0
41
0.0
41
0.0
41
0.0
41
1.0
41
0.0
41
0.0
41
0.0
41
0.0
41
1.0
41
0.0
41
0.0
41
0.0
41
0.0
41
1.0
42
0.0
43
0.0
44
0.0
45
0.0
48
1.0
49
0.0
46
1.0
46
0.0
46
0.0
46
0.0
46
0.0
46
1.0
46
0.0
46
0.0
46
0.0
46
0.0
46
1.0
46
0.0
46
0.0
46
0.0
46
0.0
46
1.0
47
1.0
47
0.0
47
0.0
47
0.0
47
0.0
47
1.0
47
0.0
47
0.0
47
0.0
47
0.0
47
1.0
47
0.0
47
0.0
47
0.0
47
0.0
47
1.0
290
0
70
1
71
2
292
0
293
0
294
1
295
1
296
1
11
0.0
21
0.0
31
0.0
"""
