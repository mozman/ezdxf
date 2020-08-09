# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created 2019-02-15
import pytest
import ezdxf

from ezdxf.entities.insert import Insert
from ezdxf.lldxf.const import DXF12, DXF2000
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text
from ezdxf.math import Matrix44, InsertTransformationError

TEST_CLASS = Insert
TEST_TYPE = 'INSERT'

ENTITY_R12 = """0
INSERT
5
0
8
0
2
BLOCKNAME
10
0.0
20
0.0
30
0.0
41
1.0
42
1.0
43
1.0
50
0.0
"""

ENTITY_R2000 = """0
INSERT
5
0
330
0
100
AcDbEntity
8
0
100
AcDbBlockReference
2
BLOCKNAME
10
0.0
20
0.0
30
0.0
41
1.0
42
1.0
43
1.0
50
0.0
"""


@pytest.fixture(scope='module')
def doc():
    return ezdxf.new()


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
    entity = TEST_CLASS.new(handle='ABBA', owner='0', dxfattribs={
        'color': '7',
        'insert': (1, 2, 3),
    })
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 7
    assert entity.dxf.linetype == 'BYLAYER'
    assert entity.dxf.insert == (1, 2, 3)
    assert entity.dxf.insert.x == 1, 'is not Vector compatible'
    assert entity.dxf.insert.y == 2, 'is not Vector compatible'
    assert entity.dxf.insert.z == 3, 'is not Vector compatible'
    assert entity.has_scaling is False
    assert entity.has_uniform_scaling is True
    # can set DXF R2007 value
    entity.dxf.shadow_mode = 1
    assert entity.dxf.shadow_mode == 1


def test_has_scaling():
    entity = TEST_CLASS.new(handle='ABBA', owner='0', dxfattribs={'xscale': 2})
    assert entity.has_scaling is True
    assert entity.has_uniform_scaling is False
    entity = TEST_CLASS.new(handle='ABBA', owner='0', dxfattribs={'yscale': 2})
    assert entity.has_scaling is True
    assert entity.has_uniform_scaling is False
    entity = TEST_CLASS.new(handle='ABBA', owner='0', dxfattribs={'zscale': 2})
    assert entity.has_scaling is True
    assert entity.has_uniform_scaling is False

    # reflections are under control, so (-2, 2, 2) is a uniform scaling
    entity = TEST_CLASS.new(handle='ABBA', owner='0', dxfattribs={
        'xscale': -2,
        'yscale': 2,
        'zscale': 2,
    })
    assert entity.has_uniform_scaling is True


def test_load_from_text(entity):
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 256, 'default color is 256 (by layer)'
    assert entity.dxf.insert == (0, 0, 0)
    assert entity.has_scaling is False


@pytest.mark.parametrize("txt,ver", [(ENTITY_R2000, DXF2000), (ENTITY_R12, DXF12)])
def test_write_dxf(txt, ver):
    expected = basic_tags_from_text(txt)
    vertex = TEST_CLASS.from_text(txt)
    collector = TagCollector(dxfversion=ver, optional=True)
    vertex.export_dxf(collector)
    assert collector.tags == expected

    collector2 = TagCollector(dxfversion=ver, optional=False)
    vertex.export_dxf(collector2)
    assert collector.has_all_tags(collector2)


def test_add_attribs():
    insert = Insert()
    assert insert.attribs_follow is False
    insert.add_attrib('T1', 'value1', (0, 0))
    assert len(insert.attribs) == 1
    assert insert.attribs_follow is True


def test_get_block(doc):
    blk = doc.blocks.new('TEST-2020-02-29')
    msp = doc.modelspace()
    insert = msp.add_blockref('TEST-2020-02-29', (0, 0))
    assert insert.block() is blk
    insert = msp.add_blockref('NOT-EXIST-2020-02-29', (0, 0))
    assert insert.block() is None
    insert = Insert()
    assert insert.block() is None


def test_clone_with_insert():
    # difference of clone() to copy_entity() is:
    # - clone returns and unassigned entity without handle, owner or reactors
    # - copy_entity clones the entity and assigns the new entity to the same owner as the source and adds the entity
    #   and it linked entities (ATTRIB & VERTEX) to the entity database, but does not adding entity to a layout, setting
    #   owner tag is not enough to assign an entity to a layout, use Layout.add_entity()
    insert = Insert()
    insert.add_attrib('T1', 'value1', (0, 0))
    clone = insert.copy()
    assert clone.dxf.handle is None
    assert clone.dxf.owner is None
    assert len(clone.attribs) == 1
    attrib = clone.attribs[0]
    assert attrib.dxf.handle is None
    assert attrib.dxf.tag == 'T1'
    assert attrib.dxf.text == 'value1'
    # change cloned attrib
    attrib.dxf.tag = 'T2'
    attrib.dxf.text = 'value2'
    # source attrib is unchanged
    assert insert.attribs[0].dxf.tag == 'T1'
    assert insert.attribs[0].dxf.text == 'value1'


def test_copy_with_insert(doc):
    msp = doc.modelspace()
    msp_count = len(msp)
    db = doc.entitydb
    db_len = len(doc.entitydb)

    insert = msp.add_blockref('Test', insert=(0, 0))
    assert insert.seqend.dxf.owner == insert.dxf.owner
    assert insert.seqend.dxf.handle is not None
    assert insert.seqend.dxf.handle in doc.entitydb

    insert.add_attrib('T1', 'value1')

    # linked attribs not stored in the entity space
    assert len(msp) == msp_count + 1
    # added INSERT + SEQEND
    assert len(db) == db_len + 2, 'ATTRIBs not automatically stored in db'
    db.refresh()
    assert len(db) == db_len + 3, 'db.refresh() should add new ATTRIBs in db'

    copy = doc.entitydb.duplicate_entity(insert)

    # not duplicated in entity space
    assert len(msp) == msp_count + 1
    # duplicated in entity database (2x SEQEND)
    assert len(doc.entitydb) == db_len + 6

    # get 1. paperspace in tab order
    psp = doc.layout()
    psp.add_entity(copy)
    assert len(psp) == 1

    assert copy.dxf.handle is not None
    assert copy.dxf.handle != insert.dxf.handle
    assert copy.dxf.owner == psp.layout_key
    assert copy.attribs[0].dxf.owner == psp.layout_key


def test_matrix44_no_transform():
    insert = TEST_CLASS.new(handle='ABBA', owner='0')
    m = insert.matrix44()
    assert m.transform((0, 0, 0)) == (0, 0, 0)
    assert m.transform_direction((1, 0, 0)) == (1, 0, 0)


def test_matrix44_insert():
    insert = TEST_CLASS.new(handle='ABBA', owner='0', dxfattribs={
        'insert': (1, 2, 3),
    })
    m = insert.matrix44()
    assert m.transform((0, 0, 0)) == (1, 2, 3)
    assert m.transform_direction((1, 0, 0)) == (1, 0, 0)


def test_matrix44_insert_and_base_point(doc):
    doc.blocks.new('Matrix44_001', base_point=(2, 2, 2))
    insert = doc.modelspace().add_blockref('Matrix44_001', insert=(1, 2, 3))
    m = insert.matrix44()
    assert m.transform((0, 0, 0)) == (-1, 0, 1)
    assert m.transform_direction((1, 0, 0)) == (1, 0, 0)


def test_matrix44_rotation():
    insert = TEST_CLASS.new(handle='ABBA', owner='0', dxfattribs={
        'insert': (0, 0, 0),
        'rotation': 90,
    })
    m = insert.matrix44()
    assert list(m.transform_vertices([(1, 0, 0), (0, 0, 1)])) == [(0, 1, 0), (0, 0, 1)]
    assert m.transform_direction((1, 0, 0)) == (0, 1, 0)


def test_matrix44_scaled():
    insert = TEST_CLASS.new(handle='ABBA', owner='0', dxfattribs={
        'xscale': 2,
        'yscale': 3,
        'zscale': 4,
    })
    m = insert.matrix44()
    assert m.transform((1, 1, 1)) == (2, 3, 4)
    assert m.transform_direction((1, 0, 0)) == (2, 0, 0), 'scaling has to be applied for directions'


def test_matrix44_direction():
    insert = TEST_CLASS.new(handle='ABBA', owner='0', dxfattribs={
        'insert': (1, 2, 3),
        'xscale': 2,
    })
    m = insert.matrix44()
    assert m.transform((1, 0, 0)) == (3, 2, 3)
    assert m.transform_direction((1, 0, 0)) == (2, 0, 0), 'only scaling has to be applied for directions'


def test_insert_transform_interface():
    insert = Insert()
    insert.dxf.insert = (1, 0, 0)

    insert.transform(Matrix44.translate(1, 2, 3))
    assert insert.dxf.insert == (2, 2, 3)

    # optimized translate implementation
    insert.translate(-1, -2, -3)
    assert insert.dxf.insert == (1, 0, 0)


def test_insert_transformation_error():
    insert = Insert.new(dxfattribs={
        'name': 'AXIS',
        'insert': (0, 0, 0),
        'rotation': 45,
    })
    m = Matrix44.scale(0.5, 1, 1)
    with pytest.raises(InsertTransformationError):
        insert.transform(m)


def test_insert_scaling():
    # Insert.transform() changes the extrusion vector
    # sign of scaling factors depend from new extrusion vector
    # just compare absolute values
    insert = Insert()
    insert.dxf.insert = (0, 0, 0)

    insert.scale(2, 3, 4)
    assert abs(insert.dxf.xscale) == 2
    assert abs(insert.dxf.yscale) == 3
    assert abs(insert.dxf.zscale) == 4

    insert.scale(-1, 1, 1)
    assert abs(insert.dxf.xscale) == 2
    assert abs(insert.dxf.yscale) == 3
    assert abs(insert.dxf.zscale) == 4

    insert.scale(-1, -1, 1)
    assert abs(insert.dxf.xscale) == 2
    assert abs(insert.dxf.yscale) == 3
    assert abs(insert.dxf.zscale) == 4

    insert.scale(-2, -2, -2)
    assert abs(insert.dxf.xscale) == 4
    assert abs(insert.dxf.yscale) == 6
    assert abs(insert.dxf.zscale) == 8
