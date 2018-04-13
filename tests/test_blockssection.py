# Created: 14.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2018, Manfred Moitzi
# License: MIT License

from __future__ import unicode_literals
import pytest
from io import StringIO

import ezdxf
from ezdxf.tools.test import compile_tags_without_handles, load_section
from ezdxf.sections.blocks import BlocksSection
from ezdxf.lldxf.tagwriter import TagWriter


@pytest.fixture(scope='module')
def ac1009():
    return ezdxf.new('AC1009')


@pytest.fixture
def blocks(ac1009):
    return BlocksSection(load_section(TESTBLOCKS, 'BLOCKS', ac1009.entitydb), ac1009)


def test_write(blocks):
    stream = StringIO()
    blocks.write(TagWriter(stream))
    result = stream.getvalue()
    stream.close()
    t1 = list(compile_tags_without_handles(TESTBLOCKS))
    t2 = list(compile_tags_without_handles(result))
    assert t1 == t2


def test_empty_section(ac1009):
    blocks = BlocksSection(load_section(EMPTYSEC, 'BLOCKS'), ac1009)
    stream = StringIO()
    blocks.write(TagWriter(stream))
    result = stream.getvalue()
    stream.close()
    assert EMPTYSEC == result


def test_key(blocks):
    assert blocks.key('Test') == 'test'
    block = blocks.new('TEST')
    assert blocks.key(block) == 'test'


def test_create_block(blocks):
    block = blocks.new('TEST')
    assert block in blocks


def test_is_layout_block(blocks):
    block = blocks.new('TEST')
    assert block.is_layout_block is False
    msp = blocks.new('*Model_Space')
    assert msp.is_layout_block is True
    msp = blocks.new('$Model_Space')
    assert msp.is_layout_block is True
    psp = blocks.new('*Paper_Space')
    assert psp.is_layout_block is True
    psp = blocks.new('$Paper_Space')
    assert psp.is_layout_block is True


def test_overwrite_existing_block(blocks):
    block = blocks.new('TEST')
    assert block in blocks
    old_len = len(blocks)
    blocks.new('Test')  # block names are case insensitive
    assert len(blocks) == old_len, 'should overwrite block "TEST"'


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


def test_block_content_entity_drawing_attribute(blocks, ac1009):
    archtick = blocks['_ARCHTICK']
    entities = list(archtick)
    assert 1 == len(entities)  # VERTEX & SEQEND doesn't count
    e = entities[0]
    assert ac1009 == e.drawing


def test_delete_block(blocks, ac1009):
    archtick = blocks['_ARCHTICK']
    entities = list(archtick)
    archtick_name = archtick.name
    blocks.delete_block(archtick_name)
    assert archtick_name not in blocks
    db = ac1009.entitydb
    assert archtick._block_handle not in db
    assert archtick._endblk_handle not in db
    for entity in entities:
        assert entity.dxf.handle not in db


def test_delete_all_blocks(blocks):
    blocks.delete_all_blocks()
    blocks = list(blocks)
    # assure not deleting layout blocks
    assert 2 == len(blocks)
    block_names = [block.name for block in blocks]
    block_names.sort()
    assert ['$MODEL_SPACE', '$PAPER_SPACE'] == block_names


def test_rename_block(blocks):
    block = blocks.new('RENAME_ME')
    assert block in blocks

    blocks.rename_block('RENAME_ME', 'NEW_NAME')
    assert 'NEW_NAME' in blocks

    # block names are case insensitive
    blocks.rename_block('New_Name', 'check_lower_case')
    assert 'Check_Lower_Case' in blocks

    # but originals name is preserved
    assert blocks['Check_Lower_Case'].name == 'check_lower_case'


@pytest.fixture(scope='module')
def ac1015():
    return ezdxf.new('AC1015')


@pytest.fixture
def ac1015_blocks(ac1015):
    if 'TestBlock' not in ac1015.blocks:
        block = ac1015.blocks.new('TestBlock')
        block.add_line((0, 0), (10, 10))
        block.add_line((0, 0), (10, 10))
        block.add_line((0, 0), (10, 10))
    return ac1015.blocks


def test_ac1015_dxf_block_structure(ac1015_blocks, ac1015):
    assert 'TestBlock' in ac1015_blocks
    block = ac1015_blocks['TestBlock']
    block_record_handle = block.block_record_handle

    # exists an associated block record entry?
    block_record = ac1015.sections.tables.block_records.get(block.name)
    assert block_record_handle == block_record.dxf.handle
    assert block_record.dxf.name == block.name


def test_ac1015_delete_block(ac1015_blocks, ac1015):
    block = ac1015_blocks['TestBlock']
    block_name = block.name
    entities = list(block)
    block_record_handle = block.block_record_handle

    block_count = len(ac1015_blocks)
    ac1015_blocks.delete_block(block_name)

    # removed from blocks load_section?
    assert block_count-1 == len(ac1015_blocks)
    assert block_name not in ac1015_blocks

    # all block related management data deleted?
    db = ac1015.entitydb
    assert block._block_handle not in db
    assert block._endblk_handle not in db
    assert block_record_handle not in db

    # removed from block records table?
    assert block_name not in ac1015.sections.tables.block_records

    # all entities deleted ?
    for entity in entities:
        assert entity.dxf.handle not in db
    # we are done!


def test_ac1015_delete_all_blocks(ac1015_blocks):
    ac1015_blocks.delete_all_blocks()
    blocks = list(ac1015_blocks)

    # assure not deleting layout blocks
    assert 2 == len(blocks)

    block_names = [block.name for block in blocks]
    block_names.sort()
    assert ['*Model_Space', '*Paper_Space'], block_names


def test_ac1015_rename_block(ac1015_blocks):
    block = ac1015_blocks.new('RENAME_ME')
    assert block in ac1015_blocks

    ac1015_blocks.rename_block('RENAME_ME', 'NEW_NAME')
    assert 'NEW_NAME' in ac1015_blocks


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
