# Copyright (c) 2011-2019, Manfred Moitzi
# License: MIT License
import pytest

import ezdxf
from ezdxf.tools.test import load_entities
from ezdxf.sections.blocks import BlocksSection
from ezdxf.lldxf.tagwriter import TagCollector
from ezdxf.entities import factory


@pytest.fixture
def dxf12():
    return ezdxf.new('R12')


@pytest.fixture
def blocks(dxf12):
    return BlocksSection(dxf12, list(load_entities(TESTBLOCKS, 'BLOCKS')))


@pytest.fixture
def bounded_blocks(dxf12):
    entities = list(load_entities(TESTBLOCKS, 'BLOCKS'))
    for entity in entities:
        factory.bind(entity, dxf12)
    return BlocksSection(dxf12, entities)


@pytest.fixture
def doc():
    doc = ezdxf.new()
    doc.blocks.new('_ARCHTICK')
    doc.blocks.new('_OPEN30')
    return doc


def test_empty_section(dxf12):
    blocks = BlocksSection(dxf12,
                           list(load_entities(EMPTYSEC, 'BLOCKS')))
    # the NES creates automatically *Model_Space and *Paper_Space blocks
    assert '*Model_Space' in blocks
    assert '*Paper_Space' in blocks

    collector = TagCollector(dxfversion=dxf12.dxfversion)
    blocks.export_dxf(collector)

    assert collector.tags[0] == (0, 'SECTION')
    assert collector.tags[1] == (2, 'BLOCKS')
    assert collector.tags[2] == (0, 'BLOCK')
    # tag[3] is a arbitrary handle
    assert collector.tags[3][0] == 5
    assert collector.tags[4] == (8, '0')  # default layer '0'
    assert collector.tags[5] == (
        2, '$Model_Space')  # export modelspace with leading '$' for R12
    assert collector.tags[-1] == (0, 'ENDSEC')


def test_key(blocks):
    assert blocks.key('Test') == 'test'
    block = blocks.new('TEST')
    assert blocks.key(block) == 'test'


def test_is_layout_block(blocks):
    block = blocks.new('TEST')
    assert block.is_any_layout is False

    # required modelspace block already created
    msp = blocks.get('*Model_Space')
    assert msp.is_modelspace is True

    # required paperspace block already created
    psp = blocks.get('*Paper_Space')
    assert psp.is_any_paperspace is True
    assert psp.is_active_paperspace is True


def test_overwrite_existing_block(blocks):
    block = blocks.new('TEST')
    assert block.dxf.name in blocks
    old_len = len(blocks)
    with pytest.raises(ezdxf.DXFTableEntryError):
        # can not create block with existing name
        blocks.new('Test')  # block names are case insensitive
    assert len(blocks) == old_len, 'should not create block "TEST"'

    blocks.delete_block('Test', safe=False)
    assert len(blocks) == old_len - 1, 'should remove existing block "TEST"'
    blocks.new('Test')
    assert len(blocks) == old_len, 'should create new block "Test"'


def test_not_in_blocks_section(blocks):
    assert 'TEST' not in blocks


def test_getitem(blocks):
    blocks.new('TEST')
    block = blocks['TEST']
    assert 'TEST' == block.name
    block = blocks['Test']
    assert 'TEST' == block.name


def test_case_insensitivity(blocks):
    blocks.new('TEST')
    assert 'TEST' in blocks
    assert 'Test' in blocks


def test_iter_blocks(blocks):
    blocks = list(blocks)
    assert 4 == len(blocks)


def test_block_content_entity_drawing_attribute(blocks, dxf12):
    archtick = blocks['_ARCHTICK']
    entities = list(archtick)
    assert 1 == len(entities)  # VERTEX & SEQEND doesn't count


def test_delete_block(bounded_blocks, dxf12):
    archtick = bounded_blocks['_ARCHTICK']
    entities = list(archtick)
    archtick_name = archtick.name
    bounded_blocks.delete_block(archtick_name, safe=False)
    assert archtick_name not in bounded_blocks
    assert archtick.is_alive is False
    for entity in entities:
        assert entity.is_alive is False


def test_safe_delete_block(blocks, dxf12):
    # block names are case insensitive
    with pytest.raises(ezdxf.DXFBlockInUseError):
        blocks.delete_block('_ArchTick', safe=True)


def test_do_not_delete_layouts_and_special_arrow_blocks(doc):
    doc.blocks.delete_all_blocks()
    assert len(doc.blocks) == 4
    block_names = set(block.name for block in doc.blocks)
    assert block_names == {'*Model_Space', '*Paper_Space', '_ARCHTICK',
                           '_OPEN30'}


def test_do_not_purge_layout_and_special_arrow_blocks(doc):
    doc.blocks.purge()
    assert len(doc.blocks) == 4
    block_names = set(block.name for block in doc.blocks)
    assert block_names == {'*Model_Space', '*Paper_Space', '_ARCHTICK',
                           '_OPEN30'}


@pytest.mark.parametrize('name', ['*D1', '*T1', '*U1', '*X1', '*E1', '*A1'])
def test_do_purge_unused_special_blocks(name, doc):
    doc.blocks.new(name)
    doc.blocks.purge()
    assert name not in doc.blocks


@pytest.mark.parametrize('name', ['*U1', '*X1', '*E1', '*A1'])
def test_do_not_purge_referenced_special_blocks(name, doc):
    doc.blocks.new(name)
    msp = doc.modelspace()
    msp.add_blockref(name, (0, 0))
    doc.blocks.purge()
    assert name in doc.blocks


def test_do_not_purge_used_dimension(doc):
    # DIMENSION (and ACAD_TABLE) block are not referenced by explicit INSERT
    # entity.
    dimension = factory.create_db_entry(
        'DIMENSION',
        dxfattribs={'geometry': '*D01'},
        doc=doc,
    )
    msp = doc.modelspace()
    msp.add_entity(dimension)
    doc.blocks.new('*D01')
    doc.blocks.purge()
    assert '*D01' in doc.blocks


def test_rename_block(blocks):
    block = blocks.new('RENAME_ME')
    assert block.dxf.name in blocks

    blocks.rename_block('RENAME_ME', 'NEW_NAME')
    assert 'NEW_NAME' in blocks

    # block names are case insensitive
    blocks.rename_block('New_Name', 'check_lower_case')
    assert 'Check_Lower_Case' in blocks

    # but originals name is preserved
    assert blocks['Check_Lower_Case'].name == 'check_lower_case'


@pytest.fixture(scope='module')
def dxf2000():
    return ezdxf.new('R2000')


@pytest.fixture
def dxf2000_blocks(dxf2000):
    if 'TestBlock' not in dxf2000.blocks:
        block = dxf2000.blocks.new('TestBlock')
        block.add_line((0, 0), (10, 10))
        block.add_line((0, 0), (10, 10))
        block.add_line((0, 0), (10, 10))
    return dxf2000.blocks


def test_dxf2000_dxf_block_structure(dxf2000_blocks, dxf2000):
    assert 'TestBlock' in dxf2000_blocks
    block = dxf2000_blocks['TestBlock']
    block_record_handle = block.block_record_handle

    # exists an associated block record entry?
    block_record = dxf2000.tables.block_records.get(block.name)
    assert block_record_handle == block_record.dxf.handle
    assert block_record.dxf.name == block.name


def test_dxf2000_delete_block(dxf2000_blocks, dxf2000):
    block = dxf2000_blocks['TestBlock']
    block_name = block.name
    entities = list(block)
    block_record_handle = block.block_record_handle

    block_count = len(dxf2000_blocks)
    dxf2000_blocks.delete_block(block_name)

    # removed from blocks load_section?
    assert block_count - 1 == len(dxf2000_blocks)
    assert block_name not in dxf2000_blocks

    # all block related management data deleted?
    assert block.is_alive is False

    # removed from block records table?
    assert block_name not in dxf2000.tables.block_records

    # all entities deleted ?
    for entity in entities:
        assert entity.is_alive is False
    # we are done!


def test_dxf2000_delete_all_blocks(dxf2000_blocks):
    dxf2000_blocks.delete_all_blocks()
    blocks = list(dxf2000_blocks)

    # assure not deleting layout blocks or arrow blocks
    assert len(blocks) == 2

    block_names = [block.name for block in blocks]
    block_names.sort()
    assert ['*Model_Space', '*Paper_Space'] == block_names


def test_dxf2000_rename_block(dxf2000_blocks):
    block = dxf2000_blocks.new('RENAME_ME')
    assert block.dxf.name in dxf2000_blocks

    dxf2000_blocks.rename_block('RENAME_ME', 'NEW_NAME')
    assert 'NEW_NAME' in dxf2000_blocks


EMPTYSEC = """  0
SECTION
  2
BLOCKS
  0
ENDSEC
"""

TESTBLOCKS = """  0
SECTION
  2
BLOCKS
  0
BLOCK
  8
0
  2
$MODEL_SPACE
 70
     0
 10
0.0
 20
0.0
 30
0.0
  3
$MODEL_SPACE
  1

  0
ENDBLK
  5
21
  8
0
  0
BLOCK
 67
     1
  8
0
  2
$PAPER_SPACE
 70
     0
 10
0.0
 20
0.0
 30
0.0
  3
$PAPER_SPACE
  1

  0
ENDBLK
  5
5B
 67
     1
  8
0
  0
BLOCK
  8
0
  2
_ARCHTICK
 70
     0
 10
0.0
 20
0.0
 30
0.0
  3
_ARCHTICK
  1

  0
POLYLINE
  5
239
  8
0
  6
BYBLOCK
 62
     0
 66
     1
 10
0.0
 20
0.0
 30
0.0
 40
0.15
 41
0.15
  0
VERTEX
  5
403
  8
0
  6
BYBLOCK
 62
     0
 10
-0.5
 20
-0.5
 30
0.0
  0
VERTEX
  5
404
  8
0
  6
BYBLOCK
 62
     0
 10
0.5
 20
0.5
 30
0.0
  0
SEQEND
  5
405
  8
0
  6
BYBLOCK
 62
     0
  0
ENDBLK
  5
23B
  8
0
  0
BLOCK
  8
0
  2
_OPEN30
 70
     0
 10
0.0
 20
0.0
 30
0.0
  3
_OPEN30
  1

  0
LINE
  5
23D
  8
0
  6
BYBLOCK
 62
     0
 10
-1.0
 20
0.26794919
 30
0.0
 11
0.0
 21
0.0
 31
0.0
  0
LINE
  5
23E
  8
0
  6
BYBLOCK
 62
     0
 10
0.0
 20
0.0
 30
0.0
 11
-1.0
 21
-0.26794919
 31
0.0
  0
LINE
  5
23F
  8
0
  6
BYBLOCK
 62
     0
 10
0.0
 20
0.0
 30
0.0
 11
-1.0
 21
0.0
 31
0.0
  0
ENDBLK
  5
241
  8
0
  0
ENDSEC
"""
