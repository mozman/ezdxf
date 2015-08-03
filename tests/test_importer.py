# encoding: utf-8
# Copyright (C) 2013, Manfred Moitzi
# License: GPLv3

import unittest
import os

import ezdxf
from ezdxf.tools.importer import Importer


def save_source_dwg(dwg, filename):
    if not os.path.exists(filename):
        dwg.saveas(filename)


def create_source_drawing(version):
    dwg = ezdxf.new(version)
    dwg.layers.create('Test', dxfattribs={'color': 17})
    dwg.layers.create('TestConflict', dxfattribs={'color': 18})
    msp = dwg.modelspace()
    msp.add_line((0, 0), (10, 0))
    msp.add_circle((0, 0), radius=5)
    msp.add_blockref("TestBlock", insert=(0, 0))
    msp.add_blockref("ConflictBlock", insert=(0, 0))
    build_block(dwg, "TestBlock")
    build_block(dwg, "ConflictBlock")
    block = build_block(dwg, "RefToConflictBlock")
    block.add_blockref('ConflictBlock', insert=(0,0))
    #save_source_dwg(dwg, 'ImportSource-' + version + '.dxf')
    return dwg


def create_target_drawing(version):
    dwg = ezdxf.new(version)
    dwg.layers.create('TestConflict', dxfattribs={'color': 19})
    conflict_block = build_block(dwg, "ConflictBlock")
    conflict_block.add_circle((1, 1), radius=7)
    return dwg


def build_block(dwg, name):
    block = dwg.blocks.new(name=name)
    block.add_line((0, 0), (10, 0))
    block.add_circle((0, 0), radius=5)
    return block


class TestCompatibilityCheck(unittest.TestCase):
    ac1009 = ezdxf.new('AC1009')
    ac1015 = ezdxf.new('AC1015')
    ac1024 = ezdxf.new('AC1024')

    def test_ac1009_to_ac1009(self):
        importer = Importer(self.ac1009, self.ac1009,  strict_mode=False)
        self.assertTrue(importer.is_compatible())

    def test_ac1015_to_ac1015(self):
        importer = Importer(self.ac1015, self.ac1015, strict_mode=False)
        self.assertTrue(importer.is_compatible())

    def test_ac1009_to_ac1015(self):
        importer = Importer(self.ac1009, self.ac1015, strict_mode=False)
        self.assertFalse(importer.is_compatible())

    def test_raise_error_ac1009_to_ac1015(self):
        with self.assertRaises(TypeError):
            Importer(self.ac1009, self.ac1015, strict_mode=True)

    def test_ac1015_to_ac1009(self):
        importer = Importer(self.ac1009, self.ac1015, strict_mode=False)
        self.assertFalse(importer.is_compatible())

    def test_ac1015_to_ac1024(self):
        importer = Importer(self.ac1015, self.ac1024, strict_mode=False)
        self.assertTrue(importer.is_compatible())

    def test_ac1024_to_ac1015(self):
        importer = Importer(self.ac1024, self.ac1015, strict_mode=False)
        self.assertFalse(importer.is_compatible())

SRC_DWG = {
    "AC1009": create_source_drawing("AC1009"),
    "AC1015": create_source_drawing("AC1015"),
}


class TestImportModelspace_AC1009(unittest.TestCase):
    VERSION = "AC1009"

    def setUp(self):
        self.source = SRC_DWG[self.VERSION]
        self.target = create_target_drawing(self.VERSION)
        self.importer = Importer(self.source, self.target)

    def test_import_simple_modelspace(self):
        self.importer.import_modelspace_entities()
        source_entities = list(self.source.modelspace())
        target_entities = list(self.target.modelspace())
        self.assertEqual(len(source_entities), len(target_entities))

    def test_import_tables_without_conflict(self):
        self.importer.import_table('layers')
        layer = self.target.layers.get('Test')
        self.assertEqual(17, layer.get_color())

    def test_import_tables_with_conflict_discard(self):
        self.importer.import_table('layers', conflict="discard")
        layer = self.target.layers.get('TestConflict')
        self.assertEqual(19, layer.get_color()) # target dwg layer def

    def test_import_tables_with_conflict_replace(self):
        self.importer.import_table('layers', conflict="replace")
        layer = self.target.layers.get('TestConflict')
        self.assertEqual(18, layer.get_color()) # source dwg layer def

    def test_import_block_without_conflict(self):
        self.importer.import_blocks('TestBlock')
        block = self.target.blocks.get('TestBlock')
        block_entities = list(block)
        self.assertEqual(2, len(block_entities))

    def test_import_block_with_conflict_discard(self):
        self.importer.import_blocks('ConflictBlock', conflict='discard')
        block = self.target.blocks.get('ConflictBlock')
        block_entities = list(block)
        self.assertEqual(3, len(block_entities))

    def test_import_block_with_conflict_replace(self):
        self.importer.import_blocks('ConflictBlock', conflict='replace')
        block = self.target.blocks.get('ConflictBlock')
        block_entities = list(block)
        self.assertEqual(2, len(block_entities))

    def test_import_block_with_conflict_rename(self):
        self.importer.import_blocks('ConflictBlock', conflict='rename')
        block = self.target.blocks.get('ConflictBlock_1')
        block_entities = list(block)
        self.assertEqual(2, len(block_entities))

    def test_import_block_with_conflict_rename_resolve_block_ref(self):
        self.importer.import_blocks('ConflictBlock', conflict='rename')
        self.importer.import_modelspace_entities('INSERT')
        msp = list(self.target.modelspace())
        self.assertEqual('ConflictBlock_1', msp[1].dxf.name)

    def test_import_block_with_conflict_rename_resolve_block_ref_inside_block_def(self):
        self.importer.import_blocks(conflict='rename')
        block = self.target.blocks.get('RefToConflictBlock')
        block_entities = list(block)
        block_ref_to_conflict_block = block_entities[2]
        self.assertEqual('ConflictBlock_1', block_ref_to_conflict_block.dxf.name)


class TestImportModelspace_AC1015(TestImportModelspace_AC1009):
    VERSION = "AC1015"

if __name__ == '__main__':
    unittest.main()
