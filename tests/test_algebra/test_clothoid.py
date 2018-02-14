# Created: 28.03.2010
# Copyright (C) 2010, Manfred Moitzi
# License: MIT License
import unittest
from ezdxf.algebra.clothoid import Clothoid

expected_points = [
    (0.0, 0.0), (0.4999511740825297, 0.0052079700401204106),
    (0.99843862987320509, 0.041620186803547267),
    (1.4881781381789292, 0.13983245006538086),
    (1.9505753764262783, 0.32742809475246343),
    (2.3516635639763064, 0.62320387651494735),
    (2.6419212729287223, 1.0273042715153904),
    (2.7637635905799862, 1.5086926753401932),
    (2.6704397998515645, 1.9952561538526452),
    (2.3566156629790327, 2.3766072153088964),
    (1.8936094203448928, 2.5322897289776636)
]


class TestAlgebraClothoid(unittest.TestCase):
    def test_approximate(self):
        clothoid = Clothoid(2.0)
        results = clothoid.approximate(5, 10)
        for expected, result in zip(expected_points, results):
            self.assertAlmostEqual(expected[0], result[0])
            self.assertAlmostEqual(expected[1], result[1])

    def test_get_radius(self):
        clothoid = Clothoid(2.0)
        self.assertAlmostEqual(clothoid.get_radius(1), 4.)
        self.assertAlmostEqual(clothoid.get_radius(0), 0.)

    def test_get_tau(self):
        clothoid = Clothoid(2.0)
        self.assertAlmostEqual(clothoid.get_tau(1), 0.125)

    def test_get_L(self):
        clothoid = Clothoid(2.0)
        self.assertAlmostEqual(clothoid.get_L(10), 0.4)

    def test_get_center(self):
        clothoid = Clothoid(2.0)
        xm, ym = clothoid.get_center(2.0)
        self.assertAlmostEqual(xm, 0.9917243)
        self.assertAlmostEqual(ym, 2.0825932)
