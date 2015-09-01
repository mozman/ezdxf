# encoding: utf-8
# Copyright (C) 2014, Manfred Moitzi
# License: MIT-License

import unittest

import ezdxf
import os
FILE = "D:\Source\dxftest\ProE_AC1018.dxf"


def test_file_not_exists():
    return not os.path.exists(FILE)


@unittest.skipIf(test_file_not_exists(), "Skip reading ProE AC1018: test file '{}' not available.".format(FILE))
class TestReadProE_AC1018(unittest.TestCase):
    def test_open_proe_ac1018(self):
        dwg = ezdxf.readfile("D:\Source\dxftest\ProE_AC1018.dxf")
        modelspace = dwg.modelspace()

        # are there entities in model space
        self.assertEqual(17, len(modelspace))

        # can you get entities
        lines = modelspace.query('LINE')
        self.assertEqual(12, len(lines))

        # is owner tag correct
        first_line = lines[0]
        self.assertEqual(modelspace.layout_key, first_line.dxf.owner)

        # is paper space == 0
        self.assertEqual(0, first_line.dxf.paperspace)


if __name__ == '__main__':
    unittest.main()
