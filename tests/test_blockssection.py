#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test blocks section
# Created: 14.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License

from __future__ import unicode_literals

import unittest
from io import StringIO

import ezdxf
from ezdxf.tools.test import DrawingProxy, normlines, Tags
from ezdxf.sections.blocks import BlocksSection


class TestBlocksSectionAC1009(unittest.TestCase):
    def setUp(self):
        self.dwg = DrawingProxy('AC1009')
        self.section = BlocksSection(Tags.from_text(TESTBLOCKS), self.dwg)

    def test_write(self):
        stream = StringIO()
        self.section.write(stream)
        result = stream.getvalue()
        stream.close()
        t1 = sorted(normlines(TESTBLOCKS))
        t2 = sorted(normlines(result))
        self.assertEqual(t1, t2)

    def test_empty_section(self):
        section = BlocksSection(Tags.from_text(EMPTYSEC), self.dwg)
        stream = StringIO()
        section.write(stream)
        result = stream.getvalue()
        stream.close()
        self.assertEqual(EMPTYSEC, result)

    def test_create_block(self):
        block = self.section.new('TEST')
        self.assertTrue(block in self.section)

    def test_not_in_blocks_section(self):
        self.assertFalse('TEST' in self.section)

    def test_getitem(self):
        newblock = self.section.new('TEST')
        block = self.section['TEST']
        self.assertEqual('TEST', block.name)

    def test_iter_blocks(self):
        blocks = list(self.section)
        self.assertEqual(4, len(blocks))

    def test_block_content_entity_drawing_attribute(self):
        archtick = self.section['_ARCHTICK']
        entities = list(archtick)
        self.assertEqual(1, len(entities))  # VERTEX & SEQEND doesn't count
        e = entities[0]
        self.assertEqual(self.dwg, e.drawing)

    def test_delete_block(self):
        archtick = self.section['_ARCHTICK']
        entities = list(archtick)
        archtick_name = archtick.name
        self.section.delete_block(archtick_name)
        self.assertTrue(archtick_name not in self.section)
        db = self.dwg.entitydb
        self.assertTrue(archtick._block_handle not in db)
        self.assertTrue(archtick._endblk_handle not in db)
        for entity in entities:
            self.assertTrue(entity.dxf.handle not in db)

    def test_delete_all_blocks(self):
        self.section.delete_all_blocks()
        blocks = list(self.section)
        # assure not deleting layout blocks
        self.assertEqual(2, len(blocks))
        block_names = [block.name for block in blocks]
        block_names.sort()
        self.assertEqual(['$MODEL_SPACE', '$PAPER_SPACE'], block_names)


class TestBlocksSectionAC1015(unittest.TestCase):
    DWG_AC1015 = ezdxf.new('AC1015')  # DXF structure is too complex for dummy constructions.

    def setUp(self):
        self.dwg = self.DWG_AC1015
        if 'TestBlock' not in self.dwg.blocks:
            self.create_test_block()

    def create_test_block(self):
        block = self.dwg.blocks.new('TestBlock')
        block.add_line((0, 0), (10, 10))
        block.add_line((0, 0), (10, 10))
        block.add_line((0, 0), (10, 10))

    def test_dxf_block_structure(self):
        self.assertTrue('TestBlock' in self.dwg.blocks)
        block = self.dwg.blocks['TestBlock']
        block_record_handle = block.get_block_record_handle()

        # exists an associated block record entry?
        block_record = self.dwg.sections.tables.block_records.get(block.name)
        self.assertEqual(block_record_handle, block_record.dxf.handle)
        self.assertEqual(block_record.dxf.name, block.name)

    def test_delete_block(self):
        block = self.dwg.blocks['TestBlock']
        block_name = block.name
        entities = list(block)
        block_record_handle = block.get_block_record_handle()

        block_count = len(self.dwg.blocks)
        self.dwg.blocks.delete_block(block_name)

        # removed from blocks section?
        self.assertEqual(block_count-1, len(self.dwg.blocks))
        self.assertTrue(block_name not in self.dwg.blocks)

        # all block related management data deleted?
        db = self.dwg.entitydb
        self.assertTrue(block._block_handle not in db)
        self.assertTrue(block._endblk_handle not in db)
        self.assertTrue(block_record_handle not in db)

        # removed from block records table?
        self.assertTrue(block_name not in self.dwg.sections.tables.block_records)

        # all entities deleted ?
        for entity in entities:
            self.assertTrue(entity.dxf.handle not in db)
        # we are done!

    def test_delete_all_blocks(self):
        self.dwg.blocks.delete_all_blocks()
        blocks = list(self.dwg.blocks)

        # assure not deleting layout blocks
        self.assertEqual(2, len(blocks))

        block_names = [block.name for block in blocks]
        block_names.sort()
        self.assertEqual(['*Model_Space', '*Paper_Space'], block_names)


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

if __name__ == '__main__':
    unittest.main()