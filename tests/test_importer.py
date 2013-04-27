# encoding: utf-8
# Copyright (C) 2013, Manfred Moitzi
# License: GPLv3

import unittest

import ezdxf
from ezdxf.importer import Importer

def create_source_drawing(version):
    return ezdxf.new(version)

def create_target_drawing(version):
    return ezdxf.new(version)

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

class TestImportModelspace_AC1009(unittest.TestCase):
    VERSION = "AC1009"
    def setUp(self):
        self.source = create_source_drawing(self.VERSION)
        self.target = create_target_drawing(self.VERSION)

class TestImportModelspace_AC1015(TestImportModelspace_AC1009):
    VERSION = "AC1015"


if __name__ == '__main__':
    unittest.main()
