# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf


@pytest.fixture(scope='module')
def doc():
    d = ezdxf.new()
    blk = d.blocks.new('Test1')
    blk.add_line((0, 0), (1, 0))
    blk.add_line((0, 0), (0, 1))
    msp = d.modelspace()
    msp.add_blockref('Test1', (10, 10))
    msp.add_blockref('Test1', (20, 10), dxfattribs={'xscale': 2})  # yscale and zscale
    return d


@pytest.fixture(scope='module')
def msp(doc):
    return doc.modelspace()


@pytest.fixture(scope='module')
def entitydb(doc):
    return doc.entitydb


def test_01_virtual_entities(msp):
    blockrefs = msp.query('INSERT')
    blockref = blockrefs[0]

    virtual_entities = list(blockref.virtual_entities())
    assert len(virtual_entities) == 2

    e = virtual_entities[0]
    # Virtual entities should not be stored in the entity database.
    assert e.dxf.handle is None, 'handle should be None'
    # Virtual entities should not reside in a layout.
    assert e.dxf.owner is None, 'owner should be None'
    # Virtual entities should be assigned to the same document as the block reference.
    assert e.doc is blockref.doc

    assert e.dxftype() == 'LINE'
    assert e.dxf.start == blockref.dxf.insert
    assert e.dxf.end == blockref.dxf.insert + (1, 0)

    e = virtual_entities[1]
    assert e.dxftype() == 'LINE'
    assert e.dxf.start == blockref.dxf.insert
    assert e.dxf.end == blockref.dxf.insert + (0, 1)

    blockref = blockrefs[1]
    virtual_entities = list(blockref.virtual_entities(non_uniform_scaling=False))
    assert len(virtual_entities) == 0
    virtual_entities = list(blockref.virtual_entities(non_uniform_scaling=True))
    assert len(virtual_entities) == 2

    e = virtual_entities[0]
    assert e.dxftype() == 'LINE'
    assert e.dxf.start == blockref.dxf.insert
    assert e.dxf.end == blockref.dxf.insert + (2, 0), 'should apply xscale 2'

    e = virtual_entities[1]
    assert e.dxftype() == 'LINE'
    assert e.dxf.start == blockref.dxf.insert
    assert e.dxf.end == blockref.dxf.insert + (0, 1), 'should apply yscale 1'


def test_02_explode_blockrefs(doc, msp, entitydb):
    blockrefs = msp.query('INSERT')
    blockref = blockrefs.first
    blockref_owner = blockref.dxf.owner
    blockref_insert = blockref.dxf.insert

    assert len(msp) == 2  # 2 INSERT
    exploded_entities = blockref.explode()
    assert blockref.is_alive is False, 'Exploded block reference should be destroyed.'
    assert len(exploded_entities) == 2
    assert len(msp) == 3  # 2 INSERT - 1 exploded INSERT + 2 LINE

    e = exploded_entities[0]
    # Exploded entities should be stored in the entity database.
    assert e.dxf.handle is not None, 'entity should have a handle'
    assert e.dxf.handle in entitydb
    # Exploded entities should reside in a layout.
    assert e.dxf.owner is not None, 'entity should have an owner'
    assert e.dxf.owner is blockref_owner
    # Exploded entities should be assigned to the same document as the block reference.
    assert e.doc is doc

    assert e.dxftype() == 'LINE'
    assert e.dxf.start == blockref_insert
    assert e.dxf.end == blockref_insert + (1, 0)

    e = exploded_entities[1]
    assert e.dxftype() == 'LINE'
    assert e.dxf.start == blockref_insert
    assert e.dxf.end == blockref_insert + (0, 1)


if __name__ == '__main__':
    pytest.main([__file__])
