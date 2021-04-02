# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf

from ezdxf.entities.insert import Insert
from ezdxf.lldxf.const import DXF12, DXF2000
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text
from ezdxf.math import Matrix44, InsertTransformationError
from ezdxf.entities import factory

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


@pytest.fixture(scope='module')
def layout(doc):
    return doc.modelspace()


@pytest.fixture(params=[ENTITY_R12, ENTITY_R2000])
def entity(request):
    return Insert.from_text(request.param)


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES
    assert 'INSERT' in ENTITY_CLASSES


def test_default_constructor():
    insert = Insert()
    assert insert.dxftype() == 'INSERT'
    assert insert.is_virtual
    assert insert.seqend is None, 'SEQEND must not exist'


def test_new_constructor():
    insert = Insert.new(handle='ABBA', owner='0', dxfattribs={
        'color': '7',
        'insert': (1, 2, 3),
    })
    assert insert.is_virtual is True, 'Has no assigned document'
    assert insert.dxf.layer == '0'
    assert insert.dxf.color == 7
    assert insert.dxf.linetype == 'BYLAYER'
    assert insert.dxf.insert == (1, 2, 3)
    assert insert.dxf.insert.x == 1, 'is not Vec3 compatible'
    assert insert.dxf.insert.y == 2, 'is not Vec3 compatible'
    assert insert.dxf.insert.z == 3, 'is not Vec3 compatible'
    assert insert.has_scaling is False
    assert insert.has_uniform_scaling is True
    # can set DXF R2007 value
    insert.dxf.shadow_mode = 1
    assert insert.dxf.shadow_mode == 1


def test_has_scaling():
    entity = Insert.new(handle='ABBA', owner='0', dxfattribs={'xscale': 2})
    assert entity.has_scaling is True
    assert entity.has_uniform_scaling is False
    entity = Insert.new(handle='ABBA', owner='0', dxfattribs={'yscale': 2})
    assert entity.has_scaling is True
    assert entity.has_uniform_scaling is False
    entity = Insert.new(handle='ABBA', owner='0', dxfattribs={'zscale': 2})
    assert entity.has_scaling is True
    assert entity.has_uniform_scaling is False

    # reflections are under control, so (-2, 2, 2) is a uniform scaling
    entity = Insert.new(handle='ABBA', owner='0', dxfattribs={
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


@pytest.mark.parametrize("txt,ver",
                         [(ENTITY_R2000, DXF2000), (ENTITY_R12, DXF12)])
def test_write_dxf(txt, ver):
    expected = basic_tags_from_text(txt)
    vertex = Insert.from_text(txt)
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


def test_export_without_sub_entities_to_dxf(doc):
    from ezdxf.lldxf.tagwriter import TagCollector
    blk = doc.blocks.new('INSERT_WITHOUT_ATTRIBS')
    blk.add_blockref('TEST', (0, 0))
    writer = TagCollector()
    blk.entity_space.export_dxf(tagwriter=writer)
    structure_tags = [tag for tag in writer.tags if tag[0] == 0]
    assert len(structure_tags) == 1
    assert structure_tags[0] == (0, 'INSERT')


def test_export_with_sub_entities_to_dxf(doc):
    from ezdxf.lldxf.tagwriter import TagCollector
    blk = doc.blocks.new('INSERT_WITH_ATTRIBS')
    insert = blk.add_blockref('TEST', (0, 0))
    insert.add_attrib('TAG', 'TEXT', (0, 0))
    writer = TagCollector()
    blk.entity_space.export_dxf(tagwriter=writer)
    structure_tags = [tag for tag in writer.tags if tag[0] == 0]
    assert structure_tags[0] == (0, 'INSERT')
    assert structure_tags[1] == (0, 'ATTRIB')
    assert structure_tags[2] == (0, 'SEQEND')


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
    assert len(db) == db_len + 3, 'New ATTRIBS automatically stored in db'

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
    insert = Insert.new(handle='ABBA', owner='0')
    m = insert.matrix44()
    assert m.transform((0, 0, 0)) == (0, 0, 0)
    assert m.transform_direction((1, 0, 0)) == (1, 0, 0)


def test_matrix44_insert():
    insert = Insert.new(handle='ABBA', owner='0', dxfattribs={
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
    insert = Insert.new(handle='ABBA', owner='0', dxfattribs={
        'insert': (0, 0, 0),
        'rotation': 90,
    })
    m = insert.matrix44()
    assert list(m.transform_vertices([(1, 0, 0), (0, 0, 1)])) == [(0, 1, 0),
                                                                  (0, 0, 1)]
    assert m.transform_direction((1, 0, 0)) == (0, 1, 0)


def test_matrix44_scaled():
    insert = Insert.new(handle='ABBA', owner='0', dxfattribs={
        'xscale': 2,
        'yscale': 3,
        'zscale': 4,
    })
    m = insert.matrix44()
    assert m.transform((1, 1, 1)) == (2, 3, 4)
    assert m.transform_direction((1, 0, 0)) == (
    2, 0, 0), 'scaling has to be applied for directions'


def test_matrix44_direction():
    insert = Insert.new(handle='ABBA', owner='0', dxfattribs={
        'insert': (1, 2, 3),
        'xscale': 2,
    })
    m = insert.matrix44()
    assert m.transform((1, 0, 0)) == (3, 2, 3)
    assert m.transform_direction((1, 0, 0)) == (2, 0, 0), \
        'only scaling has to be applied for directions'


def test_insert_transform_interface():
    insert = Insert()
    insert.dxf.insert = (1, 0, 0)

    insert.transform(Matrix44.translate(1, 2, 3))
    assert insert.dxf.insert == (2, 2, 3)

    # optimized translate implementation
    insert.translate(-1, -2, -3)
    assert insert.dxf.insert == (1, 0, 0)


@pytest.mark.xfail
# The new implementation of the INSERT transformation avoids this error!
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


def test_add_virtual_insert_with_attribs_to_layout(doc):
    doc.blocks.new('TestAddVirtualInsert')
    msp = doc.modelspace()
    insert = Insert.new(dxfattribs={'name': 'TestAddVirtualInsert'})
    insert.add_attrib('TAG', 'TEXT', (0, 0))
    msp.add_entity(insert)

    assert factory.is_bound(insert, doc) is True
    assert factory.is_bound(insert.seqend, doc) is True, \
        'SEQEND must be bound to document'

    assert insert.attribs_follow is True
    assert factory.is_bound(insert.attribs[0], doc) is True, \
        'ATTRIB must be bound to document'

