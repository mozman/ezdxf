# Created: 2014-05-09
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

import unittest
from ezdxf.rgb import int2rgb, rgb2int, aci2rgb


class TestTrueColor(unittest.TestCase):
    def test_rgb(self):
        r, g, b = int2rgb(0xA0B0C0)
        self.assertTrue(0xA0, r)
        self.assertTrue(0xB0, g)
        self.assertTrue(0xC0, b)

    def test_from_rgb(self):
        self.assertEqual(0xA0B0C0, rgb2int((0xA0, 0xB0, 0xC0)))

    def test_from_aci(self):
        self.assertEqual((255, 0, 0), aci2rgb(1))
        self.assertEqual((255, 255, 255), aci2rgb(7))

    def test_0(self):
        with self.assertRaises(IndexError):
            aci2rgb(0)

    def test_256(self):
        with self.assertRaises(IndexError):
            aci2rgb(256)
