# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created 2019-02-15
import pytest

from ezdxf.entities.lwpolyline import LWPolyline
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text
from ezdxf.lldxf.const import DXFAttributeError

LWPOLYLINE = """0
LWPOLYLINE
5
0
330
0
100
AcDbEntity
8
0
100
AcDbPolyline
90
0
70
0
43
0.0
"""


@pytest.fixture
def entity():
    return LWPolyline.from_text(LWPOLYLINE)


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES
    assert 'LWPOLYLINE' in ENTITY_CLASSES


def test_default_init():
    dxfclass = LWPolyline()
    assert dxfclass.dxftype() == 'LWPOLYLINE'
    assert dxfclass.dxf.handle is None
    assert dxfclass.dxf.owner is None
    assert dxfclass.dxf.hasattr('const_width') is False


def test_default_new():
    entity = LWPolyline.new(handle='ABBA', owner='0', dxfattribs={
        'color': 7,
        'const_width': 2,
    })
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 7
    assert entity.dxf.const_width == 2.
    assert len(entity) == 0
    entity.append((1, 2))
    assert len(entity) == 1
    assert entity.dxf.count == 1
    with pytest.raises(DXFAttributeError):
        # count not writeable
        entity.dxf.count = 2


def test_load_from_text(entity):
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 256, 'default color is 256 (by layer)'
    assert entity.dxf.count == 0
    assert entity.dxf.const_width == 0


def test_write_dxf():
    entity = LWPolyline.from_text(LWPOLYLINE)
    collector = TagCollector()
    entity.export_dxf(collector)
    assert len(collector.tags) == 0, 'do not export empty polylines'
    entity.append((1, 2))
    entity.export_dxf(collector)
    result = collector.tags
    expected = basic_tags_from_text(RESULT1)
    assert result == expected


RESULT1 = """0
LWPOLYLINE
5
0
330
0
100
AcDbEntity
8
0
100
AcDbPolyline
90
1
70
0
43
0.0
10
1.
20
2.
"""

